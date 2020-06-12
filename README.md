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


## Structure of the repository
### Scripts
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
    
### Data
#### Model Outputs
- `2019_predictions.csv`: Housing price predictions for 2019
- `2020_2021_predictions.csv`: Housing price predictions for 2020-2021
#### Model Inputs
- `Boundaries - Neighborhoods.geojson`: Neighborhood boundaries
- `census_schools.csv`: Census & school data, output from `census_schools.py`
- `crimes.csv`: Crimes data, output from `crimes_cta_dist.py`
- `cta_dist.csv`: CTA distance data, output from `crimes_cta_dist.py`
- `full_data.csv`: All model inputs compiled, output from `full_data.py`
- `prediction_data_with_lag.csv`: Transformed prediction data, output from `prediction_data_with_lag.py`
- `sales_gdf.csv`: Housing sales data, output from `sales_gdf.py`
- `train_data_with_lag.csv`: Transformed training data, output from `train_data_with_lag.py`

### Graphs
    - 

