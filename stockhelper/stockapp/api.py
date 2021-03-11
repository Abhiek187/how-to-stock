import pandas as pd

def get_stock_data(form_data):
    region = form_data["region"]
    sector = form_data["sector"]

    # Read the CSV file containing company information
    df = pd.read_csv("stock-information.csv", encoding="utf-8", header=0)
    # Filter by country
    df_country = df.loc[df["Country"] == region]
    # Filter by sector (ignore NaN values)
    df_sector = df_country[df_country["Category Name"].str.contains(sector, regex=False, na=False)]
    return df_sector
