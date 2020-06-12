#!/bin/bash

if [ $1 = "-d" ] ; then
echo "Collecting census data ... "
python3 census_schools.py

echo "Collecting CTA data ..."
python3 crimes_cta_dist.py

echo "Collecting housing sales data ..."
python3 sales_gdf.py

echo "Combining datasets ..."
python3 full_data.py
fi


echo "Training data with lag ..."
python3 train_data_with_lag.py
echo "Running model ..."
python3 prediction_data_with_lag.py