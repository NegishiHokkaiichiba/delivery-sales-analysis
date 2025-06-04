# delivery-sales-analysis

This project contains a small Streamlit application for exploring delivery sales data.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

The sales data is read from `delivery_sales_analysis.xlsx`. Optional weather data
and holiday labels are loaded when the related packages are available.

Utility scripts such as `fetch_weather.py` can be used to update local weather
files using the [meteostat](https://github.com/meteostat/meteostat) service.
