import pandas as pd
import numpy as np
import geopandas as gpd
import datetime, calendar
import censusdata
from shapely.geometry import Point

"""
INSTALL:
sudo apt-get update
sudo apt install udo
sudo apt-get install libspatialindex-dev
pip install Rtree --user
pip install geopandas
sudo apt-get install -y python-rtree
sudo gpt-get install-y python-shapely
pip install inputs
"""


def import_sales_data():
    query = ("""https://datacatalog.cookcountyil.gov/resource/5pge-nu6u.json?$limit=1000000&$select=pin,sale_price,sale_year,est_land,est_bldg,age,bldg_sf,addr,centroid_x,centroid_y,hd_sf,n_units"""
        ).replace('\n','')
    sales_df = pd.read_json(query)
    # filter any sales that are not arms-length transactions (only fair sales)
    sales_df = sales_df[sales_df['sale_price'] > 1000]
    return sales_df
    
def merge_neighborhood(sales_df):
    side_dic = {'Central': ['Loop', 'Near South Side', 'Streeterville', 'West Loop', 'Printers Row',
                         'Gold Coast', 'Rush & Division', 'River North'],
                'North': ['North Center', 'Lake View', 'Lincoln Park', 'Avondale', 'Logan Square', 'Rogers Park', 
                       'West Ridge', 'Uptown', 'Lincoln Square', 'Edison Park', 'Norwood Park', 'Jefferson Park',
                       'Sauganash,Forest Glen', 'North Park', 'Albany Park', "O'Hare", 'Edgewater',
                       'Portage Park', 'Irving Park', 'Dunning', 'Belmont Cragin', 'Hermosa', 'Wrigleyville',
                       'Boystown', 'Andersonville', 'Sheffield & DePaul', 'Bucktown', 'Old Town', 'East Village'],
                'West' : ['Humboldt Park', 'West Loop', 'West Town', 'Austin', 'Garfield Park', 'North Lawndale',
                       'Lower West Side', 'Wicker Park', 'Little Village', 'Little Italy, UIC', 'Greektown',
                       'United Center', 'Montclare', 'Galewood', 'Ukrainian Village'],
                'South': ['Armour Square', 'Douglas', 'Oakland', 'Fuller Park', 'Grand Boulevard', 'Kenwood',
                       'Washington Park', 'Hyde Park', 'Woodlawn', 'South Shore', 'Bridgeport',
                       'Grand Crossing', 'Garfield Ridge', 'Archer Heights', 'Brighton Park', 'Mckinley Park',
                       'New City', 'West Elsdon', 'Gage Park', 'Clearing', 'West Lawn', 'Chicago Lawn',
                       'Englewood', 'Chatham', 'Avalon Park', 'South Chicago', 'Burnside', 'Calumet Heights',
                       "Roseland", 'Pullman', 'South Deering', 'East Side', 'West Pullman', 'Riverdale',
                       'Hegewisch', 'Ashburn', 'Auburn Gresham', 'Beverly', 'Washington Heights',
                       'Mount Greenwood', 'Morgan Park', 'Chinatown']}
    nbs_gdf = gpd.read_file('../Boundaries - Neighborhoods.geojson')
    sales_df = sales_df.dropna(subset=['centroid_x', 'centroid_y'])
    geom = [Point(xy) for xy in zip(sales_df['centroid_x'], sales_df['centroid_y'])]
    sales_gdf = gpd.GeoDataFrame(sales_df, crs={'init': 'epsg:4326'}, geometry=geom)

    sales_gdf = gpd.sjoin(sales_gdf, nbs_gdf, how='inner', op='intersects')
    new_dic = {}
    for k,v in side_dic.items():
        for x in v:
            new_dic[x] = k
    sales_gdf['side'] = sales_gdf['pri_neigh'].map(new_dic)
    return sales_gdf


def merge_census(sales_gdf):
    # Download Census block boundaries for Chicago
    census_gdf = gpd.read_file("https://data.cityofchicago.org/resource/bt9m-d2mf.geojson?$limit=9999999")
    # Load the ACS data with variables
    variables = ["GEO_ID"]
    acs_df = censusdata.download("acs5", 2013, censusdata.censusgeo(
        [("state", "17"), ("county", "031"), ("block group", "*")]), variables)
    # Merge ACS data with Census block boundaries 
    census_gdf["geo_12"] = census_gdf["geoid10"].map(lambda x: str(x)[:12])
    acs_df["geo_12"] = acs_df["GEO_ID"].map(lambda x: str(x)[-12:])
    merged_gdf = acs_df.merge(census_gdf, on="geo_12", how="inner")
    merged_gdf = gpd.GeoDataFrame(merged_gdf[variables + ["geometry"]].drop_duplicates())
    print("merged_gdf length:", len(merged_gdf))
    # Merge the dataframe from step 3 with sales geopandas dataframe
    sales_gdf = gpd.sjoin(sales_gdf.drop(columns=['index_right']), merged_gdf, how='left')
    print("sales_gdf length:", len(sales_gdf))
    return sales_gdf


if __name__ == "__main__":
    sales_df = import_sales_data()
    print("sales data imported. length:", len(sales_df))
    sales_gdf = merge_neighborhood(sales_df)
    print("neighborhood data merged. length:", len(sales_gdf))
    sales_gdf = merge_census(sales_gdf)
    print("census data merged. length:", len(sales_gdf))
    sales_gdf.to_csv('../sales_gdf.csv', index=False)