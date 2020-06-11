import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import censusdata
import censusdata
import geopandas as gpd
import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


def reshape(df):
    for y in [2013, 2014, 2015, 2016, 2017, 2018]:
        temp_df = df[df['Year'] == y]
        temp_df = temp_df.drop(columns=['Year'])
        for n in temp_df.columns:
            if n != 'GEO_ID':
                temp_df = temp_df.rename(columns={n: n + ' ' + str(y)})
        if y == 2013:
            ndf = temp_df
        else:
            ndf = ndf.merge(temp_df, on=["GEO_ID"], how='outer')
    
    return ndf


def load_census():
    census = pd.read_csv("../census_schools.csv")
    print("census df: ", census.shape)
    print('census years: ', census['Year'].unique())
    census = census.drop(columns=['geo_12'])
    print("LONG\n", census.head())

    census_wide = reshape(census)
    print("WIDE\n", census_wide.head())

    return census, census_wide


def load_crimes():
    crimes = pd.read_csv("../crimes.csv")
    print("crime df: ", crimes.shape)
    print('crimes years: ', crimes['Year'].unique())
    crimes = crimes.rename(columns={"geo_id": "GEO_ID", "year": "Year"})
    crimes = crimes[['GEO_ID', 'Year', 'crime_count', 'crimes_per_capita']]
    print("LONG\n", crimes.head())

    crimes_wide = reshape(crimes)
    print("WIDE\n", crimes_wide.head())

    return crimes, crimes_wide


def load_cta():
    cta = pd.read_csv("../cta_dist.csv")
    print("cta df: ", cta.shape)
    cta = cta.rename(columns={"geo_id": "GEO_ID", "stop_id": "station_id"})
    cta = cta[['GEO_ID', 'station_id', 'station_name', 'distance_miles']]
    print(cta.head())

    return cta


def load_sales():
    sales = pd.read_csv("../sales_gdf.csv")
    print("sales df: ", sales.shape)
    print('sales years: ', sales['sale_year'].unique())
    sales = sales.rename(columns={"sale_year": "Year"})
    sales = sales.drop(columns=['centroid_x', 'centroid_y', 'shape_area', 'shape_len', 'index_right'])
    sales = sales[['GEO_ID', 'Year', 'pin', 'sale_price', 'age', 'addr', 'hd_sf', 'n_units', 'bldg_sf', 'geometry', 'pri_neigh', 'sec_neigh', 'side']]
    sales['n_units'] = sales['n_units'].fillna(1)
    sales['actual_sf'] = sales['hd_sf']/sales['n_units']
    print(sales.head())

    return sales


def comebine_data(census, census_wide, crimes, crimes_wide, cta, sales):
    df_long = sales.merge(census, on=["GEO_ID", "Year"], how='left')
    print('sales.shape: ', sales.shape)
    print('census.shape: ', census.shape)
    print('df_long.shape: ', df_long.shape)

    df_long = df_long.merge(crimes, on=["GEO_ID", "Year"], how='left')
    print('sales.shape: ', sales.shape)
    print('crimes.shape: ', crimes.shape)
    print('df_long.shape: ', df_long.shape)

    df_long = df_long.merge(cta, on=["GEO_ID"], how='left')
    print('sales.shape: ', sales.shape)
    print('cta.shape: ', cta.shape)
    print('df_long.shape: ', df_long.shape)

    print(df_long.head())

    df_wide = sales.merge(census_wide, on=["GEO_ID"], how='left')
    print('sales.shape: ', sales.shape)
    print('census_wide.shape: ', census_wide.shape)
    print('df_wide.shape: ', df_wide.shape)

    df_wide = df_wide.merge(crimes_wide, on=["GEO_ID"], how='left')
    print('sales.shape: ', sales.shape)
    print('crimes_wide.shape: ', crimes_wide.shape)
    print('df_wide.shape: ', df_wide.shape)

    df_wide = df_wide.merge(cta, on=["GEO_ID"], how='left')
    print('sales.shape: ', sales.shape)
    print('cta.shape: ', cta.shape)
    print('df_wide.shape: ', df_wide.shape)

    df_wide = df_wide.rename(columns={"Year": "sale_year"})
    print(df_wide.head())

    return df_long, df_wide


if __name__ == "__main__":
    census, census_wide = load_census()
    crimes, crimes_wide = load_crimes()
    cta = load_cta()  
    sales = load_sales()
    df_long, df_wide = comebine_data(census, census_wide, crimes, crimes_wide, cta, sales)   
    df_long.to_csv('../full_data.csv', index=False)
    #df_wide.to_csv('data/full_data_wide.csv', index=False)
