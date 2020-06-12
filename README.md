# Spring 2020 - Machine Learning for Public Policy
Group Project

Linh Dinh, Eric Son, Emily Zhang

## Project Description
This is a machine learning model that predicts housing prices in Chicago, IL using neighborhood characteristics. Our housing price data uses housing sales in 2013 - 2019 from the Cook County Assessor's Office, aggregated at the Census block group level. Our features include data on demographics, crime, distance to public transit, and more.

The purpose of our model is to predict housing price trends in neighborhoods across Chicago, in order to help the city government better predict the areas where housing prices is expected to rise. More advance notice on housing price trends can help the city assess areas where affordability is expected to be more of an issue, so that they can provide more resources for 

## Usage

### Running a command in your environment

Run shell script to re-pull the data from APIs and prepare for analysis.

```bash
$ ./run_software.sh
```

The bulk of our analysis is performed in the `train-models-lag.ipynb` file.
Data visualizations are prepared in the `data_viz.ipynb` file.


## Structure of the software
1. Data collecting, cleaning, and manipulation:
    - `census_schools.py`: Pulls demographic data from U.S. Census Bureau's American Community Survey (https://www.census.gov/programs-surveys/acs/data.html) and school data from Chicago Data Portal (https://data.cityofchicago.org/)
    - `crimes_cta_dist.py`: Pulls crime and CTA 'L' station data from the Chicago Data Portal and calculates crime count and distance to nearest CTA station for each census block
    - `sales_gdf.py`: Pulls residential sales data from Cook County Assessor's Office (https://datacatalog.cookcountyil.gov/Property-Taxation/Cook-County-Assessor-s-Residential-Sales-Data/5pge-nu6u) and aggregates at census block level
    - `full_data.py`: Merges together all cleaned datasets
    - `train_data_with_lag.py`: Transforms training data for model by lagging by three years and other data manipulations
    - `prediction_data_with_lag.py`: Transforms data for predictions by lagging by three years and other data manipulations
    
2. Modeling scripts:
    - `train-models-lag.ipynb`: Creates grid search to run models
    
3. Data Visualization
    - `data_viz.ipynb`: Creates data visualizations

