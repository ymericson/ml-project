import pandas as pd
import numpy as np
import geopandas as gpd
import censusdata
import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)



def gather_census():
    years = [2013, 2014, 2015, 2016, 2017, 2018]
    tables = ['B02001_001E', 'B01002_001E', 'B02001_002E', 'B02001_003E',
            'B19013_001E', 'B25001_001E', 'B25002_003E', 'B25018_001E',
            'B25035_001E', 'B25064_001E', 'B25010_001E', 'B23007_002E',
            'B23007_001E']
    df = pd.DataFrame()
    for t in tables:
        table = pd.DataFrame()
        for y in years:
            temp = pd.DataFrame(censusdata.download(
                    "acs5", y, censusdata.censusgeo(
                    [("state", "17"), ("county", "031"), ("block group", "*")]),
                    [t, "GEO_ID"])).reset_index(drop=True)
            temp['Year'] = y
            table = table.append(temp)
            
        if df.shape[0] == 0:
            df = table
        else:
            df = pd.merge(df, table, how="inner", on=["GEO_ID", "Year"])
    df = df.rename(columns={"B02001_001E": "Total Population", "B01002_001E": "Median Age",
                    "B02001_002E": "Total White", "B02001_003E": "Total Black",
                    "B19013_001E": "Median HH Income", "B25001_001E": "Total Housing Units",
                    "B25002_003E": "Total Vacant Units", "B25018_001E": "Median Number of Rooms",
                    "B25035_001E": "Median Year Built", "B25064_001E": "Median Gross Rent",
                    "B25010_001E": "Mean HH Size", "B23007_002E": "HH with Children",
                    "B23007_001E": "Total HH"})
    print(df.head())
    return df

def impute_negative(df):
    df['Percent White'] = df['Total White']/df['Total Population']
    df['Percent Black'] = df['Total Black']/df['Total Population']
    df['Percent HH with Children'] = df['HH with Children']/df['Total HH']
    df['Percent Housing Vacant'] = df['Total Vacant Units']/df['Total Housing Units']
    df['Median Age'][df['Median Age'] < 0] = None
    df['Median HH Income'][df['Median HH Income'] < 0] = None
    df['Median Number of Rooms'][df['Median Number of Rooms'] < 0] = None
    df['Median Year Built'][df['Median Year Built'] <= 0] = None
    df['Median Gross Rent'][df['Median Gross Rent'] < 0] = None
    df['Mean HH Size'][df['Mean HH Size'] < 0] = None
    df = df[['GEO_ID', 'Year', 'Total Population', 'Median Age', 
            'Median HH Income', 'Total Housing Units', 
            'Median Number of Rooms', 'Median Year Built',
            'Median Gross Rent', 'Mean HH Size',
            'Percent White', 'Percent Black', 
            'Percent HH with Children', 'Percent Housing Vacant']]
    df["geo_12"] = df["GEO_ID"].map(lambda x: str(x)[-12:])
    return df

def school_data(df):
    schools_12 = gpd.read_file("https://data.cityofchicago.org/resource/anck-gptm.geojson?$limit=9999999")
    schools_12['Year'] = 2012
    schools_13 = gpd.read_file("https://data.cityofchicago.org/resource/98wb-ks45.geojson?$limit=9999999")
    schools_13['Year'] = 2013
    schools_14 = gpd.read_file("https://data.cityofchicago.org/resource/dgq3-i7xm.geojson?$limit=9999999")
    schools_14['Year'] = 2014
    schools_15 = gpd.read_file("https://data.cityofchicago.org/resource/mntu-576c.geojson?$limit=9999999")
    schools_15['Year'] = 2015
    schools_16 = gpd.read_file("https://data.cityofchicago.org/resource/mb74-gx3g.geojson?$limit=9999999")
    schools_16['Year'] = 2016
    schools_17 = gpd.read_file("https://data.cityofchicago.org/resource/75e5-35kf.geojson?$limit=9999999")
    schools_17['Year'] = 2017
    schools_18 = gpd.read_file("https://data.cityofchicago.org/resource/d2h8-2upd.geojson?$limit=9999999")
    schools_18['Year'] = 2018
    schools = schools_12.append(schools_13)
    schools = schools.append(schools_14)
    schools = schools.append(schools_15)
    schools = schools.append(schools_16)
    schools = schools.append(schools_17)
    schools = schools.append(schools_18)
    schools.shape
    chicago_gdf = gpd.read_file("https://data.cityofchicago.org/resource/bt9m-d2mf.geojson?$limit=9999999")
    chicago_gdf["geo_12"] = chicago_gdf["geoid10"].map(lambda x: str(x)[:12])
    schools_gdf = gpd.sjoin(chicago_gdf, schools, how="left", op='intersects')
    schools_geo12 = schools_gdf[['Year', 'geo_12', 'school_id']].groupby(['Year', 'geo_12'])\
        .count().reset_index().rename(columns = {'school_id': 'Number of Public Schools'})
    df = df.merge(schools_geo12, on=["geo_12", "Year"], how='left')
    df['Number of Public Schools'][df['Number of Public Schools'].isna()] = 0
    return df

if __name__ == "__main__":
    df = gather_census()
    print("length:", len(df))
    df = impute_negative(df)
    print("length:", len(df))    
    df = school_data(df)
    print("length:", len(df))    
    df.to_csv('../census_schools.csv', index=False)