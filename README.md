# DHL Team Tool (All workflows enabled)

Run in GitHub Codespaces (no installs on your PC).

## Run

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Open port 8501 from the Ports panel.

## Secrets

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill `DHL_API_KEY`.
Do not commit secrets.
