"""Per-tab ZIP + Items workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import re
import zipfile

from .common import normalize_text, norm_key

DATE_TZ = 'Africa/Cairo'
DATE_FMT = '%d-%m-%Y'

TEMPLATE_PHONE_COL = 'Destination Phone'
ITEM_COLS = ['Item Name', 'Item Price', 'Qty', 'Pc Weight']

SKIP_SHEETS = {'ALL DEPARTMENTS', 'LANGUAGE', 'ITEMS', 'Items', 'items'}

BLANK_ON_CONTINUATION = {
    'Date','To Name','Company','Country Code','DDP',
    'Destination Building','Destination Street','Destination Suburb','Destination City',
    'Destination State','Destination Postcode','Destination Country','Destination Email'
}


def only_digits(s: str) -> str:
    return re.sub(r'[^0-9]', '', s or '')


def safe_sheet_name(name: str) -> str:
    s = normalize_text(name)
    s = re.sub(r'[:\\/?\\*\\[\\]]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return (s or 'DATA')[:31]


def safe_filename(name: str) -> str:
    s = normalize_text(name)
    s = re.sub(r'[^A-Za-z0-9\-\_]+', '_', s)
    s = s.strip('_')
    return (s or 'TAB')[:80]


def phone_like_score(s: str) -> int:
    if not s:
        return 0
    digits = sum(ch.isdigit() for ch in s)
    if digits < 7:
        return 0
    score = digits
    if '+' in s:
        score += 50
    if s.strip().startswith('00'):
        score += 30
    return score


def extract_phone_from_row(row_dict: dict) -> str:
    candidates = []
    for col, val in row_dict.items():
        nk = norm_key(col)
        if any(k in nk for k in ['PHONE','TEL','TELEPHONE','MOBILE','CELL']):
            v = normalize_text(val)
            if phone_like_score(v) > 0:
                candidates.append(v)
    if not candidates:
        for val in row_dict.values():
            v = normalize_text(val)
            if phone_like_score(v) > 0:
                candidates.append(v)
    if not candidates:
        return ''
    return sorted(candidates, key=phone_like_score, reverse=True)[0]


def normalize_phone_keep_if_cannot(raw: str):
    raw0 = normalize_text(raw)
    if not raw0:
        return '', 'NO_PHONE'
    m = re.search(r'\+\s*([0-9][0-9\s\-\(\)]{6,})', raw0)
    if m:
        d = only_digits(m.group(1))
        if 8 <= len(d) <= 15:
            return '+' + d, 'E164_FROM_PLUS'
    d = only_digits(raw0)
    if d.startswith('00'):
        d2 = d[2:]
        if 8 <= len(d2) <= 15:
            return '+' + d2, 'E164_FROM_00'
    return raw0, 'RAW_KEPT'


def load_items(items_xlsx: Path):
    items_df = pd.read_excel(items_xlsx, engine='openpyxl')
    items_df = items_df.loc[:, ~items_df.columns.duplicated()].copy()

    col_by_key = {norm_key(c): c for c in items_df.columns}
    if 'ITEM NAME' not in col_by_key or 'VALUE' not in col_by_key:
        raise ValueError('Items.xlsx must contain columns: Item Name, Value, Pc Weight')

    pc_weight_keys = {'PC WEIGHT','PCS WEIGHT','PIECE WEIGHT','ITEM WEIGHT','WEIGHT','WEIGHT KG','WEIGHT (KG)','PC WEIGHT (KG)'}
    pcw_col = None
    for k in pc_weight_keys:
        if k in col_by_key:
            pcw_col = col_by_key[k]
            break
    if pcw_col is None:
        raise ValueError('Items.xlsx must contain Pc Weight (kg per piece).')

    name_col = col_by_key['ITEM NAME']
    value_col = col_by_key['VALUE']

    items_df = items_df.dropna(subset=[name_col]).copy()
    items_df[name_col] = items_df[name_col].astype(str).map(normalize_text)
    items_df = items_df[items_df[name_col] != '']
    items_df[value_col] = pd.to_numeric(items_df[value_col], errors='coerce').fillna(0)
    items_df[pcw_col] = pd.to_numeric(items_df[pcw_col], errors='coerce').fillna(0)

    return (
        items_df[[name_col, value_col, pcw_col]]
        .rename(columns={name_col:'Item Name', value_col:'Value', pcw_col:'Pc Weight'})
        .to_dict('records')
    )


def sheet_code(name: str, used: dict) -> str:
    toks = [t for t in re.split(r'[^A-Za-z0-9]+', normalize_text(name)) if t]
    code = (''.join(toks).upper() or 'SHEET')[:6]
    n = used.get(code, 0)
    used[code] = n + 1
    return f"{code}{n+1}" if n > 0 else code


@dataclass
class PerTabZipOptions:
    keep_phone_on_all_item_lines: bool = True
    out_dirname: str = 'output_multiline'


def run_per_tab_zip(main_xlsx: Path, items_xlsx: Path, options: PerTabZipOptions = PerTabZipOptions()):
    main_xlsx = Path(main_xlsx)
    items_xlsx = Path(items_xlsx)
    if not main_xlsx.exists():
        raise FileNotFoundError(f"Missing main Excel: {main_xlsx}")
    if not items_xlsx.exists():
        raise FileNotFoundError(f"Missing Items.xlsx: {items_xlsx}")

    out_dir = main_xlsx.parent / options.out_dirname
    per_tab_dir = out_dir / 'per_tab_excels'
    out_dir.mkdir(exist_ok=True)
    per_tab_dir.mkdir(exist_ok=True)

    try:
        run_date = datetime.now(ZoneInfo(DATE_TZ)).strftime(DATE_FMT)
    except Exception:
        run_date = datetime.now().strftime(DATE_FMT)

    blank_on_cont = set(BLANK_ON_CONTINUATION)
    if options.keep_phone_on_all_item_lines:
        blank_on_cont.discard(TEMPLATE_PHONE_COL)
    else:
        blank_on_cont.add(TEMPLATE_PHONE_COL)

    item_list = load_items(items_xlsx)

    xls = pd.ExcelFile(main_xlsx)
    used_codes = {}

    combined_rows = []
    combined_headers = []
    qc_rows = []
    per_tab_count = 0

    def extend_union_headers(union_list, new_headers):
        seen = set(union_list)
        for h in new_headers:
            if h not in seen:
                union_list.append(h)
                seen.add(h)
        return union_list

    for sh in xls.sheet_names:
        if sh in SKIP_SHEETS or norm_key(sh) in {norm_key(s) for s in SKIP_SHEETS}:
            continue
        raw = pd.read_excel(main_xlsx, sheet_name=sh, engine='openpyxl')
        raw = raw.loc[:, ~raw.columns.duplicated()].copy()
        if raw.empty:
            continue

        base_headers = list(raw.columns)
        extra_cols = []
        if 'Order Number' not in base_headers:
            extra_cols.append('Order Number')
        if TEMPLATE_PHONE_COL not in base_headers:
            extra_cols.append(TEMPLATE_PHONE_COL)
        for c in ITEM_COLS:
            if c not in base_headers:
                extra_cols.append(c)

        out_headers = base_headers + extra_cols
        combined_headers = extend_union_headers(combined_headers, out_headers)

        sc = sheet_code(sh, used_codes)
        seq = 1
        out_rows = []

        for _, r in raw.iterrows():
            row_dict = r.to_dict()
            for c in extra_cols:
                row_dict.setdefault(c, '')

            order = f"{sc}-{seq:04d}"
            seq += 1
            row_dict['Order Number'] = order

            phone_existing = normalize_text(row_dict.get(TEMPLATE_PHONE_COL, ''))
            phone_raw = phone_existing or extract_phone_from_row(row_dict)
            phone_out, phone_note = normalize_phone_keep_if_cannot(phone_raw)
            row_dict[TEMPLATE_PHONE_COL] = phone_out

            for i, item in enumerate(item_list):
                rec = dict(row_dict)
                rec['Item Name'] = item.get('Item Name','')
                rec['Item Price'] = item.get('Value', 0)
                rec['Pc Weight'] = item.get('Pc Weight', 0)
                rec['Qty'] = 1

                if i > 0:
                    for col in blank_on_cont:
                        if col in rec:
                            rec[col] = ''

                out_rows.append(rec)
                combined_rows.append(dict(rec, **{'Source Tab': sh}))

            qc_rows.append({
                'Order Number': order,
                'Source Tab': sh,
                'Phone Raw': phone_raw,
                'Phone Output': phone_out,
                'Phone Note': phone_note,
                'Run Date': run_date
            })

        df_out = pd.DataFrame(out_rows).reindex(columns=out_headers)
        tab_xlsx = per_tab_dir / (safe_filename(sh) + '.xlsx')
        with pd.ExcelWriter(tab_xlsx, engine='openpyxl') as w:
            df_out.to_excel(w, sheet_name=safe_sheet_name(sh), index=False)

        per_tab_count += 1

    combined_xlsx = None
    if combined_rows:
        if 'Source Tab' not in combined_headers:
            combined_headers.append('Source Tab')
        combined_df = pd.DataFrame(combined_rows).reindex(columns=combined_headers)
        combined_xlsx = out_dir / 'ALL_TABS_COMBINED.xlsx'
        with pd.ExcelWriter(combined_xlsx, engine='openpyxl') as w:
            combined_df.to_excel(w, sheet_name='COMBINED', index=False)

    qc_df = pd.DataFrame(qc_rows)
    qc_xlsx = out_dir / '_QC.xlsx'
    with pd.ExcelWriter(qc_xlsx, engine='openpyxl') as w:
        qc_df.to_excel(w, sheet_name='_QC', index=False)

    zip_path = out_dir / 'DHL_PER_TAB_EXCELS.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(per_tab_dir.glob('*.xlsx')):
            z.write(p, arcname=f"per_tab_excels/{p.name}")
        z.write(qc_xlsx, arcname=qc_xlsx.name)
        if combined_xlsx is not None and combined_xlsx.exists():
            z.write(combined_xlsx, arcname=combined_xlsx.name)

    return {
        'zip_path': zip_path,
        'combined_xlsx': combined_xlsx,
        'qc_xlsx': qc_xlsx,
        'per_tab_dir': per_tab_dir,
        'per_tab_count': per_tab_count,
    }
