#!/bin/bash

echo "Collecting census data ... "
python3 data/scripts/census_schools.py

echo "Collecting CTA data ..."
python3 data/scripts/crimes_cta_dist.py

echo "Collecting housing sales data ..."
python3 data/scripts/sales_gdf.py

echo "Combining datasets ..."
python3 data/scripts/full_data.py

echo "Preparing training data with lag ..."
python3 data/scripts/train_data_with_lag.py

echo "Preparing prediction data with lag ..."
python3 data/scripts/prediction_data_with_lag.py