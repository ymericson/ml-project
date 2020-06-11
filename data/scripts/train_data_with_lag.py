import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import censusdata
import censusdata
import geopandas as gpd
import warnings
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

FILE_NAME = "../full_data.csv"
INFO_COLS = ['GEO_ID', 'Year', 'Total Population', 'Median Age', 'Median HH Income',
       'Total Housing Units', 'Median Number of Rooms', 'Median Year Built',
       'Median Gross Rent', 'Mean HH Size', 'Percent White', 'Percent Black',
       'Percent HH with Children', 'Percent Housing Vacant',
       'Number of Public Schools', 'crime_count', 'crimes_per_capita',
       'station_name', 'distance_miles']


def prepare_sales(file):
    df_long = pd.read_csv(file)
    sales = df_long[['GEO_ID', 'Year', 'sale_price', 'age', 'actual_sf',
                 'pri_neigh', 'sec_neigh', 'side']]
    print("sales years:", sales['Year'].unique())

    sales['count'] = 1
    sales1 = sales[['GEO_ID', 'Year', 'pri_neigh', 'sec_neigh', 'side',
                'sale_price', 'actual_sf', 'count']].groupby([
                'GEO_ID', 'Year', 'pri_neigh', 'sec_neigh', 'side']).sum().reset_index()
    sales2 = sales[['GEO_ID', 'Year', 'pri_neigh', 'sec_neigh', 'side',
                'age']].groupby([
                'GEO_ID', 'Year', 'pri_neigh', 'sec_neigh', 'side']).mean().reset_index()
    
    sales_small = sales1.merge(sales2, on=['GEO_ID', 'Year', 'pri_neigh', 'sec_neigh', 'side'], how='inner')
    sales_small['price_p_sf'] = sales_small['sale_price'] / sales_small['actual_sf']
    sales_small['price_p_house'] = sales_small['sale_price'] / sales_small['count']
    sales_small['avg_sf'] = sales_small['actual_sf'] / sales_small['count']
    sales_small = sales_small.rename(columns={"age": "avg_age", "count": "no_of_sales"})

    sales_info = sales_small[['GEO_ID', 'Year', 'no_of_sales', 'avg_age',
    'price_p_sf', 'price_p_house', 'avg_sf']]
    sales_info['Year'] = sales_info['Year'] + 3
    sales_info = sales_info.rename(columns={"no_of_sales": "prev_year_no_of_sales", "avg_age": "prev_year_avg_age",
                "price_p_sf": "prev_year_price_p_sf", "price_p_house": "prev_year_price_p_house",
                "avg_sf": "prev_year_avg_sf"})
    sales_info = sales_info[(sales_info['Year'] >= 2016) & (sales_info['Year'] <= 2019)]

    sales_small = sales_small.drop(columns=['sale_price', 'actual_sf'])
    sales_small = sales_small[(sales_small['Year'] >= 2016) & (sales_small['Year'] <= 2019)]

    return sales_small, sales_info


def prepare_info(file):
    df_long = pd.read_csv(file)
    info = df_long[INFO_COLS]
    print("info years:", info['Year'].unique()) 
    info['Year'] = info['Year'] + 3
    
    info_small = info[INFO_COLS].groupby(['GEO_ID', 'Year', 'station_name']).mean().reset_index()
    info_small = info_small[(info_small['Year'] >= 2016) & (info_small['Year'] <= 2019)]

    return info_small


def merge_data(sales_small, sales_info, info_small):
    df = sales_small.merge(sales_info, on=['GEO_ID', 'Year'], how='left')
    df = df.merge(info_small, on=['GEO_ID', 'Year'], how='left')
    df['Number of Public Schools'][df['Number of Public Schools'] >= 5] = 5
    df['Number of Public Schools'][df['Number of Public Schools'].isna()] = 0
    df = df.rename(columns={'Number of Public Schools': 'public_schools'})
    df = df[(df['Year'] >= 2016) & (df['Year'] <= 2019)]

    return df


if __name__ == "__main__":
    sales, sales_prv = prepare_sales(FILE_NAME)
    print("sales length:", len(sales))
    print(sales.head())
    print("prev year sales info length:", len(sales_prv))
    print(sales_prv.head())

    info = prepare_info(FILE_NAME)
    print("info length:", len(info))   
    print(info.head())

    df = merge_data(sales, sales_prv, info)
    print("merged df length:", len(df))    
    print("merged df years:", df['Year'].unique())

    df.to_csv('../train_data_with_lag.csv', index=False)
