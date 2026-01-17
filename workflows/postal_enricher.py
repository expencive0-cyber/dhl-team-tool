"""Postal/City Enricher using DHL Location Finder API.

Adapted from your Batch Enricher v4.1:
- Calls DHL Location Finder /find-by-address
- Normalizes country code + city, fills postal code
- Uses CSV cache to reduce API calls
- Writes enriched workbook with _LOG and _SUMMARY sheets

This module is based on your POSTAL_CODE_.txt notebook export.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
import difflib
import pandas as pd
import requests

API_BASE = 'https://api.dhl.com/location-finder/v1'

@dataclass
class EnricherOptions:
    provider_type: str = 'express'
    service_type: str = ''
    limit_results: int = 15
    max_accepted_distance_m: int = 25000
    request_delay_sec: float = 0.2
    max_retries: int = 5
    strict_city_from_dhl: bool = True
    fallback_to_capital: bool = True
    only_empty: bool = False
    cache_file: str = 'dhl_city_cache.csv'
    city_index_file: str = 'dhl_country_city_index.csv'

COUNTRY_SYNONYMS = {
    'UNITED ARAB EMIRATES': 'AE','UAE':'AE',
    'EGYPT':'EG',
    'SAUDI ARABIA':'SA','KSA':'SA',
    'UNITED KINGDOM':'GB','UK':'GB',
    'UNITED STATES':'US','USA':'US'
}

ISO2_TO_CANONICAL = {
    'AE':'United Arab Emirates','EG':'Egypt','SA':'Saudi Arabia','GB':'United Kingdom','US':'United States'
}

CAPITAL_BY_ISO2 = {
    'EG':'Cairo','AE':'Abu Dhabi','SA':'Riyadh','GB':'London','US':'Washington'
}

CITY_SYNONYMS = {
    'EG': {'EL MAADI':'MAADI','AL MAADI':'MAADI','AL QAHIRA':'CAIRO','EL QAHERA':'CAIRO',
           '6 OCTOBER':'6TH OF OCTOBER','6TH OCTOBER':'6TH OF OCTOBER'}
}


def to_upper_ascii(text):
    if not text:
        return ''
    import unicodedata
    t = str(text).upper()
    t_norm = unicodedata.normalize('NFKD', t)
    return ''.join(ch for ch in t_norm if not unicodedata.combining(ch))


def normalize_country(country_name, country_code):
    code = to_upper_ascii(country_code).strip()
    if len(code) == 2 and code.isalpha():
        return code, ISO2_TO_CANONICAL.get(code, country_name or code)
    name = to_upper_ascii(country_name).strip()
    if name in COUNTRY_SYNONYMS:
        code = COUNTRY_SYNONYMS[name]
        return code, ISO2_TO_CANONICAL.get(code, country_name or name.title())
    return None, None


def load_cache(path: Path):
    if path.exists():
        df = pd.read_csv(path, dtype=str).fillna('')
        return {(r['iso2'], r['city_seed']): {'postal': r.get('postal',''), 'city': r.get('city',''), 'country_name': r.get('country_name',''), 'distance': r.get('distance','')} for _, r in df.iterrows()}
    return {}


def save_cache(cache: dict, path: Path):
    rows = []
    for (iso2, city_seed), v in cache.items():
        rows.append({'iso2': iso2, 'city_seed': city_seed, 'postal': v.get('postal',''), 'city': v.get('city',''), 'country_name': v.get('country_name',''), 'distance': v.get('distance','')})
    if rows:
        pd.DataFrame(rows).drop_duplicates().to_csv(path, index=False)


def load_city_index(path: Path):
    idx = {}
    if path.exists():
        df = pd.read_csv(path, dtype=str).fillna('')
        for _, r in df.iterrows():
            idx.setdefault(r['iso2'], set()).add(to_upper_ascii(r['city']))
    return idx


def save_city_index(index_map: dict, path: Path):
    rows = []
    for iso2, cities in index_map.items():
        for c in sorted(cities):
            rows.append({'iso2': iso2, 'city': c})
    if rows:
        pd.DataFrame(rows).drop_duplicates().to_csv(path, index=False)


def dhl_request_find_by_address(api_key: str, params: dict, max_retries: int):
    headers = {'DHL-API-Key': api_key, 'Accept': 'application/json'}
    backoff = 0.5
    for _ in range(max_retries):
        r = requests.get(f"{API_BASE}/find-by-address", params=params, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 400 and 'Unknown Country' in r.text:
            return None
        if r.status_code in (429, 502, 503, 504):
            time.sleep(min(10.0, backoff))
            backoff *= 1.6
            continue
        r.raise_for_status()
    raise RuntimeError('Max retries reached (DHL).')


def best_location(payload):
    locs = (payload or {}).get('locations', [])
    if not locs:
        return None, None, None, None, None
    def dist(l):
        try:
            return float(l.get('distance', 1e18))
        except Exception:
            return 1e18
    loc = sorted(locs, key=dist)[0]
    addr = ((loc.get('place') or {}).get('address') or {})
    return addr.get('postalCode'), addr.get('addressLocality'), loc.get('distance'), loc.get('name'), ','.join(sorted(loc.get('serviceTypes', [])))


def apply_city_synonyms(iso2, city):
    c = to_upper_ascii(city).strip()
    if iso2 in CITY_SYNONYMS and c in CITY_SYNONYMS[iso2]:
        return CITY_SYNONYMS[iso2][c]
    return c


def fuzzy_candidates(country_city_index, iso2, city, cutoff=0.85, topn=3):
    src = to_upper_ascii(city)
    pool = sorted(list(country_city_index.get(iso2, set())))
    if not pool:
        return []
    scored = []
    for p in pool:
        ratio = difflib.SequenceMatcher(None, src, p).ratio()
        if ratio >= cutoff:
            scored.append((ratio, p))
    scored.sort(reverse=True)
    return [p for _, p in scored[:topn]]


def query_with_corrections(api_key, country_city_index, iso2, city_seed, opts: EnricherOptions):
    city_seed = apply_city_synonyms(iso2, city_seed)

    def do_query(city_used, label):
        params = {'countryCode': iso2, 'addressLocality': city_used}
        if opts.provider_type:
            params['providerType'] = opts.provider_type
        if opts.service_type:
            params['serviceType'] = opts.service_type
        if opts.limit_results:
            params['limit'] = str(opts.limit_results)
        payload = dhl_request_find_by_address(api_key, params, opts.max_retries)
        if payload is None:
            return {'unknown_country': True}
        postal, dhl_city, dist, name, svc = best_location(payload)
        if dhl_city:
            return {'postal': postal or '', 'city': to_upper_ascii(dhl_city), 'distance': dist or '', 'attempt': label, 'used_city': to_upper_ascii(city_used), 'serviceTypes': svc or ''}
        return None

    if len(city_seed.strip()) >= 3:
        out = do_query(city_seed, 'synonym_or_input')
        if out:
            return out
        time.sleep(opts.request_delay_sec)

    for cand in fuzzy_candidates(country_city_index, iso2, city_seed):
        out = do_query(cand, 'fuzzy')
        if out:
            return out
        time.sleep(opts.request_delay_sec)

    if opts.fallback_to_capital and iso2 in CAPITAL_BY_ISO2:
        cap = to_upper_ascii(CAPITAL_BY_ISO2[iso2])
        if len(cap.strip()) >= 3:
            out = do_query(cap, 'capital')
            if out:
                return out

    return {'postal':'', 'city': to_upper_ascii(city_seed), 'distance':'', 'attempt':'fallback', 'used_city': to_upper_ascii(city_seed), 'serviceTypes': ''}


def run_postal_enricher(input_xlsx: Path, out_xlsx: Path, dhl_api_key: str, opts: EnricherOptions = EnricherOptions()):
    input_xlsx = Path(input_xlsx)
    out_xlsx = Path(out_xlsx)
    if not input_xlsx.exists():
        raise FileNotFoundError(f"Missing input: {input_xlsx}")
    if not dhl_api_key:
        raise ValueError('DHL API key is required')

    cache_path = input_xlsx.parent / opts.cache_file
    city_index_path = input_xlsx.parent / opts.city_index_file

    cache = load_cache(cache_path)
    city_index = load_city_index(city_index_path)

    def find_col(df, candidates):
        cols = {c.lower(): c for c in df.columns}
        for cand in candidates:
            if cand.lower() in cols:
                return cols[cand.lower()]
        for k, v in cols.items():
            for cand in candidates:
                if cand.lower() in k:
                    return v
        return None

    def maybe_write(df, idx, col, value):
        if opts.only_empty and str(df.loc[idx, col]).strip():
            return
        df.loc[idx, col] = value

    def process_df(df, sheet_name):
        df = df.copy().fillna('')
        country_name_col = find_col(df, ['country','country name','destination country']) or 'Country'
        country_code_col = find_col(df, ['country code','iso2','iso']) or 'Country Code'
        city_col = find_col(df, ['city','address locality','town']) or 'City'
        postal_col = find_col(df, ['postal code','postcode','zip']) or 'Postal Code'

        for col in [country_name_col, country_code_col, city_col, postal_col]:
            if col not in df.columns:
                df[col] = ''
        if 'Original City' not in df.columns:
            df['Original City'] = ''

        logs = []
        api_calls = 0
        cache_hits = 0
        flagged_far = 0

        recs = df.to_dict('records')
        for i, row in enumerate(recs):
            in_name = row.get(country_name_col, '')
            in_code = row.get(country_code_col, '')
            in_city = row.get(city_col, '')
            maybe_write(df, i, 'Original City', in_city)

            iso2, canonical = normalize_country(in_name, in_code)
            log = {'sheet': sheet_name, 'row': i+1, 'input_country': in_name, 'input_country_code': in_code, 'input_city': in_city}

            if not iso2:
                log['status'] = 'no_country'
                logs.append(log)
                continue

            seed = to_upper_ascii(in_city).strip()
            if not seed and opts.fallback_to_capital and iso2 in CAPITAL_BY_ISO2:
                seed = to_upper_ascii(CAPITAL_BY_ISO2[iso2])
            if not seed:
                log['status'] = 'no_city_seed'
                logs.append(log)
                continue

            ck = (iso2, seed)
            if ck in cache:
                out = dict(cache[ck]); out['cache'] = 'hit'
                cache_hits += 1
            else:
                out = query_with_corrections(dhl_api_key, city_index, iso2, seed, opts)
                if out.get('unknown_country'):
                    log['status'] = 'unknown_country'
                    logs.append(log)
                    continue
                out['cache'] = 'miss'
                api_calls += 1
                cache[ck] = {'postal': out.get('postal',''), 'city': out.get('city',''), 'country_name': to_upper_ascii(ISO2_TO_CANONICAL.get(iso2, canonical)), 'distance': out.get('distance','')}

            if out.get('city'):
                city_index.setdefault(iso2, set()).add(out['city'])

            final_city = out.get('city') if (opts.strict_city_from_dhl and out.get('city')) else seed
            final_country = to_upper_ascii(ISO2_TO_CANONICAL.get(iso2, canonical))
            final_postal = out.get('postal','')

            needs_review = False
            try:
                if out.get('distance') and float(out['distance']) > float(opts.max_accepted_distance_m):
                    needs_review = True
                    flagged_far += 1
            except Exception:
                pass

            maybe_write(df, i, country_code_col, iso2)
            maybe_write(df, i, country_name_col, final_country)
            maybe_write(df, i, city_col, final_city)
            maybe_write(df, i, postal_col, final_postal)

            status = 'ok_cached' if out.get('cache') == 'hit' else 'ok_api'
            if needs_review:
                status += '_needs_review'

            log.update({'iso2': iso2, 'final_city': final_city, 'postal': final_postal, 'distance': out.get('distance',''), 'status': status})
            logs.append(log)
            time.sleep(opts.request_delay_sec)

        return df, pd.DataFrame(logs), {'api_calls': api_calls, 'cache_hits': cache_hits, 'flagged_far': flagged_far}

    sheets = pd.read_excel(input_xlsx, sheet_name=None, dtype=str, engine='openpyxl')
    out_book = {}
    log_frames = []
    sheet_kpis = []

    for sname, sdf in sheets.items():
        odf, ldf, kpi = process_df(sdf, sname)
        out_book[sname[:31] or 'Sheet1'] = odf
        log_frames.append(ldf.assign(sheet=sname))
        sheet_kpis.append({'sheet': sname, **kpi})

    LOG_DF = pd.concat(log_frames, ignore_index=True) if log_frames else pd.DataFrame()

    RUN_CONFIG = pd.DataFrame([
        ['PROVIDER_TYPE', opts.provider_type],
        ['SERVICE_TYPE', opts.service_type],
        ['LIMIT_RESULTS', opts.limit_results],
        ['MAX_ACCEPTED_DISTANCE_M', opts.max_accepted_distance_m],
        ['REQUEST_DELAY_SEC', opts.request_delay_sec],
        ['MAX_RETRIES', opts.max_retries],
        ['ONLY_EMPTY', opts.only_empty],
        ['STRICT_CITY_FROM_DHL', opts.strict_city_from_dhl],
        ['FALLBACK_TO_CAPITAL', opts.fallback_to_capital],
    ], columns=['Key','Value'])

    if not LOG_DF.empty:
        st = LOG_DF['status'].fillna('')
        OVERALL = pd.DataFrame([
            ['total_rows', len(LOG_DF)],
            ['ok_api', int(st.str.startswith('ok_api').sum())],
            ['ok_cached', int(st.str.startswith('ok_cached').sum())],
            ['needs_review', int(st.str.contains('needs_review').sum())],
            ['no_country', int((st=='no_country').sum())],
            ['no_city_seed', int((st=='no_city_seed').sum())],
            ['unknown_country', int((st=='unknown_country').sum())],
        ], columns=['Metric','Value'])
        SHEET_KPI = pd.DataFrame(sheet_kpis)
    else:
        OVERALL = pd.DataFrame(columns=['Metric','Value'])
        SHEET_KPI = pd.DataFrame(columns=['sheet','api_calls','cache_hits','flagged_far'])

    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        for sname, odf in out_book.items():
            odf.to_excel(writer, index=False, sheet_name=sname)
        if not LOG_DF.empty:
            LOG_DF.to_excel(writer, index=False, sheet_name='_LOG')

        start = 0
        RUN_CONFIG.to_excel(writer, index=False, sheet_name='_SUMMARY', startrow=start)
        start += len(RUN_CONFIG) + 2
        OVERALL.to_excel(writer, index=False, sheet_name='_SUMMARY', startrow=start)
        start += len(OVERALL) + 2
        SHEET_KPI.to_excel(writer, index=False, sheet_name='_SUMMARY', startrow=start)

    save_cache(cache, cache_path)
    save_city_index(city_index, city_index_path)

    return {'rows': int(len(LOG_DF)) if not LOG_DF.empty else 0, 'cache_size': len(cache)}
