# Student Performance Analyzer

A Streamlit web app that analyzes student marks from sample data, CSV, or Excel.

## Required input columns
Your CSV/Excel file must contain these columns:
- Name
- Python
- Maths
- AI

Marks should normally be between 0 and 100.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy online
1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Open https://share.streamlit.io and sign in with GitHub.
3. Choose **Create app**, select the repository, branch `main`, and file `app.py`.
4. Click **Deploy**.

The app can use sample data or accept CSV/Excel uploads.
