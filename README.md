# Time Calculator (Streamlit)

Local Streamlit app for common time calculations with a custom green/orange theme.

## Features

- Time difference between two times
- Add or subtract a duration from a time
- Add or subtract two durations
- Time unit converter
- Date difference calculator

## Run locally

1. Open terminal in this folder:
   - `cd "\\..\time_calculator_local"`
2. Install dependencies:
   - `py -m pip install -r requirements.txt`
3. Start app:
   - `py -m streamlit run app.py`

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. In Streamlit Cloud, create a new app from your repository.
3. Set:
   - Branch: `main`
   - Main file path: `app.py`
