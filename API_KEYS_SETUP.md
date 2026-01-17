# 🔑 Setup API Keys on Streamlit Cloud

## Required API Keys

The following API keys have been added to your app:

| API | Key | Secret |
|-----|-----|--------|
| **DHL** | `GZmaHSo0of9i4KHvXXgAJVf6UZDZ0fY8` | `rbXtN5wThN14GFgP` |
| **Geoapify** | `643f8c3849fc4738b477686e3b4431fb` | - |
| **Geonames** | `mabuzeid` (username) | - |

## ✅ How to Add to Streamlit Cloud

1. Go to: https://dhlmailshot0.streamlit.app/
2. Click the **⋯** menu (top right)
3. Select **Settings**
4. Click **Secrets**
5. Add the following TOML:

```toml
DHL_API_KEY = "GZmaHSo0of9i4KHvXXgAJVf6UZDZ0fY8"
API_SECRET = "rbXtN5wThN14GFgP"
GEOAPIFY_KEY = "643f8c3849fc4738b477686e3b4431fb"
GEONAMES_USER = "mabuzeid"
```

6. Click **Save**
7. App will auto-restart

## ✅ Verify Keys Work

After adding secrets, the app will automatically:
- Use DHL API for postal enrichment
- Use Geoapify for location data
- Use Geonames for city lookups

All workflows should now have full API access!
