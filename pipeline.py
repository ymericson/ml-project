#from sklearn import datasets, linear_model
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets, linear_model
import numpy as np
sns.set_style("darkgrid")
import datetime
import calendar
 


def print_test():
    print('hello')
    
# 1. Read data
def read_data(file_path):
    return pd.read_csv(file_path)

# 2. Explore data
def explore_data(df):
    display(df.describe())
    display(df.head(5))
def explore_data_null(df):
    fig, ax = plt.subplots(figsize=(17,10))
    sns.heatmap(df.isnull(), yticklabels=False, cbar=False, cmap='viridis')
    plt.show()
    return df.isnull().sum().sort_values(ascending=False)    
def explore_data_corr(df):
    fig, ax = plt.subplots(figsize=(17,10))
    corr_df = df.corr()
    ax = sns.heatmap(corr_df, xticklabels=corr_df.columns, yticklabels=corr_df.columns,
                     cmap='RdBu_r', annot=True, linewidth=0.5)
    plt.show()
    
# 3. Create Training and Testing Sets 
def create_train_test(df, train_cols, test_col):
    X_train, X_test, y_train, y_test = \
        train_test_split(df[train_cols], df[test_col], test_size=0.3, random_state=0)
    return X_train, X_test, y_train, y_test
    
# 4. Pre-Process Data
def impute_null(df, columns_list):
    return df[columns_list].fillna(df[columns_list].mean())
def normalize_features(X_train, X_test, col_list):
    scaler = StandardScaler()
    X_train_norm = scaler.fit_transform(X_train[col_list])
    X_test_norm = scaler.transform(X_test[col_list])
    # replace train/test feature columns with normalized values
    X_train[col_list] = pd.DataFrame(X_train_norm, index=X_train.index, columns=col_list)
    X_test[col_list] = pd.DataFrame(X_test_norm, index=X_test.index, columns=col_list)
    return X_train, X_test

# 5. Generate Features
def dummy_vars(df, dummy_cols):
    return pd.get_dummies(data=df, columns=dummy_cols)
def discretize_cont_vars(df, column, n):
    return pd.cut(df[column], bins=n)
def align_cols(X_train, X_test):
    for col in list(X_train.columns.symmetric_difference(X_test.columns)):
        if col not in X_train.columns:
            X_train[col] = 0
        if col not in X_test.columns:
            X_test[col] = 0  
    return X_train, X_test

# 6. Build Classifiers
def build_classifiers():
    gnb = GaussianNB() # Initialize Gaussia classifier
    #nb = ComplementNB() 
    model = gnb.fit(X_train_norm, y_train) # Train our classifier
    # Make predictions
    preds = gnb.predict(X_test_norm)
    print(preds)


# 7. Evaluate Classifiers
def eval_classifiers(MODELS, GRID, X_train, X_test, y_train, y_test):
    #print(accuracy_score(y_test, preds))

    # Begin timer 
    start = datetime.datetime.now()

    # Initialize results data frame 
    results_df = pd.DataFrame(columns=['Training model', 'penalty', 'C', 'random_state', 'priors', 'accuracy_score'])

    # Loop over models 
    for model_key in MODELS.keys(): 

        # Loop over parameters 
        for params in GRID[model_key]: 
            print("Training model:", model_key, "|", params)

            # Create model 
            model = MODELS[model_key]
            model.set_params(**params)

            # Fit model on training set 

            model.fit(X_train, y_train.iloc[:,0])

            # Predict on testing set 
            preds = model.predict(X_test)

            # Evaluate predictions 
            accuracy = accuracy_score(y_test.iloc[:,0], preds)

            # Store results in your results data frame 


            params["Training model"] = model_key
            params["accuracy_score"] = accuracy
            #print(params)
            #print()
            results_df = results_df.append(params, ignore_index=True)

    # End timer
    stop = datetime.datetime.now()
    print("Time Elapsed:", stop - start)
    return results_df