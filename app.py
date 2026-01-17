import streamlit as st
from pathlib import Path
import tempfile

from workflows.per_tab_zip import run_per_tab_zip, PerTabZipOptions
from workflows.final_ai_standard import run_final_ai_standard
from workflows.final_ai_smart import run_final_ai_smart
from workflows.postal_enricher import run_postal_enricher, EnricherOptions
from auth import check_login, logout
from admin_panel import show_admin_panel
from user_management import create_user

# Set page config
st.set_page_config(page_title="DHL Team Tool", layout="wide")

# Check login
check_login()

# Create only mabuzeid user on first run
try:
    create_user("mabuzeid", "Mta@0127809934800", "admin")
except:
    pass

# Sidebar
with st.sidebar:
    st.write(f"👤 **User:** {st.session_state.username}")
    st.write(f"📊 **Role:** {st.session_state.user_role}")
    
    if st.button("Logout", use_container_width=True):
        logout()

# Main content
st.write("### 📦 DHL Team Tool")

# Show admin panel only to admins
if st.session_state.user_role == "admin":
    show_admin_panel()
    st.divider()

workflow = st.selectbox(
    "Choose a workflow",
    [
        "1) Final AI Builder (Standard)",
        "2) Final AI Builder (Smart)",
        "3) Per-tab ZIP + Items",
        "4) Postal/City Enricher (DHL Location Finder)",
    ],
)

st.divider()

work_dir = Path(tempfile.mkdtemp(prefix="dhl_team_tool_"))

def save_uploaded(uploaded_file, target_path: Path):
    target_path.write_bytes(uploaded_file.getbuffer())
    return target_path


def get_secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, '')).strip()
    except Exception:
        return ''


if workflow.startswith('1)') or workflow.startswith('2)'):
    st.subheader("Inputs")
    af_input = st.file_uploader("Upload AF Input.xlsx", type=["xlsx", "xlsm"], key="af")
    country_code = st.file_uploader("Upload country code .xlsx", type=["xlsx"], key="cc")
    template = st.file_uploader("Upload final AI template .xlsx", type=["xlsx"], key="tpl")

    st.caption("Output schema follows the template headers/order. The output also contains a _QC sheet.")

    run_btn = st.button("Run", type="primary", disabled=not (af_input and country_code and template))

    if run_btn:
        af_path = save_uploaded(af_input, work_dir / "AF Input.xlsx")
        cc_path = save_uploaded(country_code, work_dir / "country code .xlsx")
        tpl_path = save_uploaded(template, work_dir / "final AI template.xlsx")
        out_path = work_dir / ("final_AI_output.xlsx" if workflow.startswith('1)') else "final_AI_smart_output.xlsx")

        with st.spinner("Building…"):
            if workflow.startswith('1)'):
                stats = run_final_ai_standard(af_path, cc_path, tpl_path, out_path)
            else:
                stats = run_final_ai_smart(af_path, cc_path, tpl_path, out_path)

        st.success(f"Done. Rows: {stats.get('rows', 0)} | Highlighted: {stats.get('highlighted', 0)}")

        with open(out_path, 'rb') as f:
            st.download_button(
                "Download output Excel",
                data=f,
                file_name=out_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


elif workflow.startswith('3)'):
    st.subheader("Inputs")
    main_xlsx = st.file_uploader("Upload MAIN Excel (multiple tabs)", type=["xlsx", "xlsm"], key="main")
    items_xlsx = st.file_uploader("Upload Items.xlsx", type=["xlsx"], key="items")

    st.subheader("Options")
    keep_phone_all_lines = st.checkbox("Keep Destination Phone on all item lines", value=True)

    run_btn = st.button("Run", type="primary", disabled=not (main_xlsx and items_xlsx))

    if run_btn:
        main_path = save_uploaded(main_xlsx, work_dir / "main.xlsx")
        items_path = save_uploaded(items_xlsx, work_dir / "Items.xlsx")

        with st.spinner("Processing…"):
            opts = PerTabZipOptions(keep_phone_on_all_item_lines=keep_phone_all_lines)
            result = run_per_tab_zip(main_path, items_path, options=opts)

        zip_path = result['zip_path']
        st.success(f"Done. Per-tab files: {result['per_tab_count']}. ZIP ready.")
        with open(zip_path, "rb") as f:
            st.download_button(
                label="Download DHL_PER_TAB_EXCELS.zip",
                data=f,
                file_name=zip_path.name,
                mime="application/zip",
            )


else:
    st.subheader("Inputs")
    in_xlsx = st.file_uploader("Upload Excel to enrich", type=["xlsx", "xlsm"], key="enrich")

    st.subheader("DHL API Key")
    default_key = get_secret('DHL_API_KEY')
    api_key = st.text_input(
        "DHL_API_KEY (recommended: store in .streamlit/secrets.toml)",
        value=default_key,
        type='password'
    )

    st.subheader("Options")
    provider = st.selectbox("Provider type", options=['express','parcel'], index=0)
    strict_city = st.checkbox("Use city returned by DHL", value=True)
    only_empty = st.checkbox("Only fill empty cells", value=False)

    run_btn = st.button("Run", type="primary", disabled=not (in_xlsx and api_key))

    if run_btn:
        in_path = save_uploaded(in_xlsx, work_dir / "input.xlsx")
        out_path = work_dir / "enriched_output.xlsx"

        opts = EnricherOptions(provider_type=provider, strict_city_from_dhl=strict_city, only_empty=only_empty)

        with st.spinner("Enriching… (DHL API calls may take time)"):
            stats = run_postal_enricher(in_path, out_path, dhl_api_key=api_key, opts=opts)

        st.success(f"Done. Rows processed: {stats.get('rows', 0)} | Cache size: {stats.get('cache_size', 0)}")
        with open(out_path, 'rb') as f:
            st.download_button(
                "Download enriched_output.xlsx",
                data=f,
                file_name=out_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.caption("Cache files are saved in the run folder during this session.")
