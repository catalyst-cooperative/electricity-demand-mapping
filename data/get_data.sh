#!/bin/bash

# Download required data and put it in its place:
# FERC 714 Demand
cd demand/ferc714/
curl -o ferc714.zip \
    https://www.ferc.gov/docs-filing/forms/form-714/data/form714-database.zip
unzip ferc714.zip
cd ../../

# planning area geometries
cd geometries/hifld_planning_areas
curl -o hifld_planning_areas.zip \
    https://hifld-geoplatform.opendata.arcgis.com/datasets/7d35521e3b2c48ab8048330e14a4d2d1_0.zip
unzip hifld_planning_areas.zip
cd ../../

# balancing authority geometries
cd geometries/hifld_control_areas/
curl -o hifld_control_areas.zip \
    https://hifld-geoplatform.opendata.arcgis.com/datasets/02602aecc68d4e0a90bf65e818155f60_0.zip
unzip hifld_control_areas.zip
cd ../../

# Stuff for later
# utility service territory geometries
cd geometries/hifld_service_territories
curl -o hifld_service_territories.zip \
    https://hifld-geoplatform.opendata.arcgis.com/datasets/c4fd0b01c2544a2f83440dab292f0980_0.zip
unzip hifld_service_territories.zip
cd ../../
