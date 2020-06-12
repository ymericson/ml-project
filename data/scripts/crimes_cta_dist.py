import pandas as pd
import numpy as np
import censusdata
import geopandas as gpd
import geoplot as gplt
import geopy.distance
from matplotlib.patches import Polygon
from shapely.ops import nearest_points
from shapely.geometry import Point
import requests
import json

import matplotlib.pyplot as plt


def gather_census(years, tables):
    """
    Gathers census data
    """
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
    return df
``

def import_data():
    """
    Imports data for demographic, crime, and census geographies.
    """
    years = [2012, 2013, 2014, 2015, 2016, 2017, 2018]
    tables = ['B02001_001E']
    #crimes_df = pd.read_csv("data/Crimes-2013-2019.csv")
    crimes_12 = pd.read_json("https://data.cityofchicago.org/resource/ijzp-q8t2.json?$limit=9999999")
    crimes_df = crimes[crimes['year'].between(2012, 2018)]
    crimes_gdf = gpd.GeoDataFrame(crimes_df, geometry=gpd.points_from_xy(crimes_df.Longitude, crimes_df.Latitude))
    census_gdf = gpd.read_file("https://data.cityofchicago.org/resource/bt9m-d2mf.geojson?$limit=9999999")
    acs_df = gather_census(years, tables)
    acs_df = acs_df.rename(columns={"B02001_001E": "total_pop"})
    census_gdf["geo_12"] = census_gdf["geoid10"].map(lambda x: str(x)[:12])
    acs_df["geo_12"] = acs_df["GEO_ID"].map(lambda x: str(x)[-12:])
    return acs_df, crimes_gdf, census_gdf

def merge_data(acs_df, crimes_gdf, census_gdf):
    """
    Merges datasets into a single dataframe.
    """
    merged_gdf = acs_df.merge(census_gdf, on="geo_12", how="inner")
    merged_gdf = gpd.GeoDataFrame(merged_gdf)
    allmerged_gdf = gpd.sjoin(crimes_gdf, merged_gdf, how='left')
    limited_gdf = allmerged_gdf[["total_pop", "ID", "Case Number", "Year_left", "Primary Type", "blockce10", "GEO_ID", "geometry", "Latitude", "Longitude"]]
    return limited_gdf

def modify_data(df):
    """
    Cleans dataframe
    """
    df = df[df.total_pop != 0]
    df = df.dropna()
    df = df.drop_duplicates('Case Number')
    count_by_block = pd.Series(df.groupby(['GEO_ID', 'Year_left'])['Case Number'].count(), name='crime_count').reset_index()
    joined2 = count_by_block.merge(df, on=["GEO_ID","Year_left"], how="inner").reset_index()
    joined2 = joined2.rename(columns={"Year_left": "Year"})
    joined2 = joined2[joined2.total_pop != 0]
    joined2.dropna()
    joined2.reset_index()
    joined2['crimes_per_capita'] = joined2['crime_count']/joined2['total_pop']
    # impute crimes_per_capita with values > 1 with median
    median = joined2.loc[joined2['crimes_per_capita']<1, 'crimes_per_capita'].median()
    joined2.loc[joined2['crimes_per_capita'] > 1, 'crimes_per_capita'] = np.nan
    joined2['crimes_per_capita'].fillna(median,inplace=True)
    final_gdf = gpd.GeoDataFrame(joined2)
    return final_gdf

def visualize_crimes(df):
    """
    Plots crimes
    """
    df.plot(figsize=(20, 20), column='crimes_per_capita', cmap=plt.cm.coolwarm, legend=True)


def import_cta():
    """
    Imports CTA 'L' station data
    """
    #cta_df = pd.read_csv("data/CTA-LStops.csv")
    cta_df = pd.read_json("https://data.cityofchicago.org/resource/8pix-ypme.json")
    cta_df['Longitude'] = cta_df['location'].map(lambda x: float(x['longitude']))
    cta_df['Latitude'] = cta_df['location'].map(lambda x: float(x['latitude']))
    cta_gdf = gpd.GeoDataFrame(cta_df, geometry=gpd.points_from_xy(cta_df.Longitude, cta_df.Latitude))
    cta_gdf = cta_gdf[['STOP_ID', 'STOP_NAME', 'STATION_NAME', 'Longitude', 'Latitude', 'geometry']]
    return cta_gdf

    
def near(cta_gdf, point, pts):
    """
    Calculates nearest CTA station and returns the corresponding Stop ID.
    """
    nearest = cta_gdf.geometry == nearest_points(point, pts)[1]
    return max(cta_gdf[nearest].STOP_ID)


def nearest_point(merged_df2, cta_gdf):
    """
    Calculates nearest CTA station and returns updated dataset with nearest point.
    """
    pts3 = cta_gdf.geometry.unary_union
    merged_df2['STOP_ID'] = merged_df2.apply(lambda row: near(cta_gdf, row.geometry, pts3), axis=1)
    merged_with_cta = merged_df2.merge(merged_df2, on="STOP_ID", how="left")
    return merged_with_cta

def calc_distance(coords_1, coords_2):
    """
    Calculates distance between two coordinates
    """
    return geopy.distance.distance(coords_1, coords_2).miles


def gen_distance(df):
    """
    Generates distance between each point and its nearest CTA line
    """
    df['distance'] = df.apply(lambda row: calc_distance((row.Longitude_x, row.Latitude_x), (row.Longitude_y, row.Latitude_y)), axis=1)
    final_cta = df[['GEO_ID','STOP_ID','STATION_NAME', 'distance']]
    return final_cta

def visualize_cta(df):
    """
    Plots distances
    """
    df = gpd.GeoDataFrame(df)
    df = df.rename(columns={"geometry_x": "geometry"})
    df.plot(figsize=(20, 20), column='distance', cmap=plt.cm.coolwarm, legend=True)
    

if __name__ == "__main__":
    ## Crime Data
    acs_df, crimes_gdf, census_gdf = import_data()
    merged_df = merge_data(acs_df, crimes_gdf, census_gdf)
    merged_df2 = modify_data(merged_df)
    visualize_crimes(merged_df2)

    ## CTA Data
    cta_gdf = import_cta()
    cta_df2 = nearest_point(merged_df2, cta_gdf)
    cta_df3 = gen_distance(cta_df2)
    visualize_cta(cta_df3)

    ## Create CSV for both datasets
    merged_df.to_csv('../crimes.csv')
    final_cta.to_csv('../cta_dist.csv')
