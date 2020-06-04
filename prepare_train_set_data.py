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

FILE_NAME = "data/Full_Data_long.csv"
INFO_COLS = ['GEO_ID', 'Year', 'Total Population', 'Median Age', 'Median HH Income',
       'Total Housing Units', 'Median Number of Rooms', 'Median Year Built',
       'Median Gross Rent', 'Mean HH Size', 'Percent White', 'Percent Black',
       'Percent HH with Children', 'Percent Housing Vacant',
       'Number of Public Schools', 'crime_count', 'crimes_per_capita',
       'station_name', 'distance_miles']

NUM_COLS = ['prev_year_no_of_sales', 'prev_year_avg_age',
       'prev_year_price_p_sf', 'prev_year_price_p_house', 'prev_year_avg_sf',
       'Total Population', 'Median Age', 'Median HH Income',
       'Total Housing Units', 'Median Number of Rooms', 'Median Year Built',
       'Median Gross Rent', 'Mean HH Size', 'Percent White', 'Percent Black',
       'Percent HH with Children', 'Percent Housing Vacant',
       'crime_count', 'crimes_per_capita', 'distance_miles']

CAT_COLS = ['pri_neigh', 'sec_neigh', 'side', 'station_name', 'Number of Public Schools']


def process_bool_and_missing(train, test, features):
    '''
    Purpose: apply filters to numeric features in the df

    Inputs:
        df (dataframe)
        filter_info (dict): of the form {'column_name': ['value1', 'value2']}

    Returns: (dataframe) filtered dataframe,
      or None if a specified column does not exist
    '''

    for f in features:
        if train[f].dtype == 'bool':
            print(f, "is bool, converting to int")
            train[f] = train[f].astype(int)
            test[f] = test[f].astype(int)
            
        if train[f].dtype in ('float64', 'int64'):   
            print(f, "training data's mean:", train[f].mean(),
                "will replace missing values of", f)
            train[f][train[f].isna()] = train[f].mean()
            test[f][test[f].isna()] = train[f].mean()

    return None


def normalize_features(train, test, features):
    '''
    Purpose: normalize the set of features listed, using training set
    mean and standard deviation

    Inputs:
    train, test (df): train and test sets

    Returns: modify the existing train and test sets with new normalized 
    variables as new variables
    '''

    for feature in features:
        scaler = StandardScaler()
        scaler.fit(pd.DataFrame(train.loc[:, feature]))
        n_feature = 'Norm ' + feature
        train[n_feature] = scaler.transform(pd.DataFrame(train.loc[:, feature]))
        test[n_feature] = scaler.transform(pd.DataFrame(test.loc[:, feature]))

    return None


def one_hot_encoding_features(train, test, features, prefix):
    '''
    Purpose: Encode categorical variables

    Inputs:
    train, test (df): train and test sets
    features (list): list of features to encode

    Returns: modify the existing train and test sets

    '''

    train = pd.get_dummies(train, columns = features, prefix = prefix)
    test = pd.get_dummies(test, columns = features, prefix = prefix)
    
    for v in test.columns:
        if v not in train.columns:
            test = test.drop(columns=[v])
        
    for v in train.columns:
            if v not in test.columns:
                test[v] = 0

    return train, test


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
    sales_info['Year'] = sales_info['Year'] + 1
    sales_info = sales_info.rename(columns={"no_of_sales": "prev_year_no_of_sales", "avg_age": "prev_year_avg_age",
                "price_p_sf": "prev_year_price_p_sf", "price_p_house": "prev_year_price_p_house",
                "avg_sf": "prev_year_avg_sf"})
    sales_info = sales_info[(sales_info['Year'] >= 2014) & (sales_info['Year'] <= 2019)]

    sales_small = sales_small.drop(columns=['sale_price', 'actual_sf', 'no_of_sales', 'avg_age', 'avg_sf'])
    sales_small = sales_small[(sales_small['Year'] >= 2014) & (sales_small['Year'] <= 2019)]

    return sales_small, sales_info


def prepare_info(file):
    df_long = pd.read_csv(file)
    info = df_long[INFO_COLS]
    print("info years:", info['Year'].unique()) 
    info['Year'] = info['Year'] + 1
    
    info_small = info[INFO_COLS].groupby(['GEO_ID', 'Year', 'station_name']).mean().reset_index()
    info_small = info_small[(info_small['Year'] >= 2014) & (info_small['Year'] <= 2019)]

    return info_small


def merge_data(sales_small, sales_info, info_small):
    df = sales_small.merge(sales_info, on=['GEO_ID', 'Year'], how='left')
    df = df.merge(info_small, on=['GEO_ID', 'Year'], how='left')
    df['Number of Public Schools'][df['Number of Public Schools'] >= 5] = 5
    df['Number of Public Schools'][df['Number of Public Schools'].isna()] = 0
    df = df[(df['Year'] >= 2014) & (df['Year'] <= 2019)]

    return df


def prepare_train_test(df):
    train = df[df['Year'] <= 2017]
    test = df[df['Year'] >= 2018]
    process_bool_and_missing(train, test, NUM_COLS)
    normalize_features(train, test, NUM_COLS)
    train, test = one_hot_encoding_features(train, test, CAT_COLS,
        ['pri_neigh', 'sec_neigh', 'side', 'station_name', 'public_schools'])

    return train, test

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

    train, test = prepare_train_test(df)
    print("train length:", len(train))
    print("train years:", train['Year'].unique())
    print("test length:", len(test))
    print("test years:", test['Year'].unique())
    train.to_csv('data/train.csv', index=False)
    test.to_csv('data/test.csv')
