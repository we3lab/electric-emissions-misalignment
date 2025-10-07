# Electricity costs and emissions incentives are misaligned for commercial and industrial power consumers

Code and data for analysis and visualization accompanying our manuscript entitled "Electricity costs and emissions incentives are misaligned for commercial and industrial power consumers".

Before you get started, please install the Python dependencies listed in `requirements.txt`. For example, using `pipenv`:

```
pipenv shell
pip install -r requirements.txt
```

## Data sources

Raw data can be found in the `data` folder, when possible. All data used is from 2023.
Some data cannot be republished under MIT license, in which case links to the data sources are available below:

- *Average emission factors (AEFs)*: collected from United States Energy Information Administration (EIA) [Hourly Electric Grid Monitor](https://www.eia.gov/electricity/gridmonitor/about) using a method from de Chalendar et al. [1]. Monthly/hourly averaged data available in `data/AEFs` folder, and raw data by ISO is available in subfolders.
- *Marginal emission factors (MEFs)*: Monthly/hourly averaged data available in `data/MEFs/average_mefs.csv`, with Monte Carlo simulations computed using the method from Siler-Evans et al. [2] available in subfolders.
- *Electricity tariffs*: `industrial-electricity-tariffs` is updated monthly on [Zenodo](https://doi.org/10.5281/zenodo.16739989) and [GitHub](https://github.com/we3lab/industrial-electricity-tariffs) [3]. Archived data applicable to 2023 available in `data/tariffs/bundled` and `data/tariffs/delivery_only` folders.
- *Day-ahead market (DAM) prices*: downloaded from [GridStatus](https://gridstatus.io/). Raw historical data not available for re-publication. Monthly/hourly averages are saved to the `data/DAMs` folder with columns `month`, `hour`, and `USD_per_MWh`
- *Incentive-based demand response (IBDR)*: the Incentive Demand Response Program Parameter (IDroPP) dataset is available from the [Stanford Digital Repository as ["US incentive based demand response program parameters"](https://doi.org/10.25740/ck480bd0124) [4]. Data relevant to our analysis copied to `data/IBDR` folder.
- *Geospatial data*: 
    - Census boundaries for IBDR display from [Census.gov](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html)
    - Independent System Operator (ISO) shapefile from US Department of Homeland Security's [Homeland Infrastructure Foundation-Level Data (HIFLD)](https://hifld-geoplatform.hub.arcgis.com/datasets/50f80920d36e435d9a34db2bd0fd3ad8_0/explore).
        - ***NOTE***: This dataset is no longer publicly accessible, but similar data is available through EIA's [U.S. Energy Atlas](https://atlas.eia.gov/search) under [RTO Regions](https://atlas.eia.gov/datasets/b286c693074045b3ac9b5d7300162e99_256/explore?location=35.167089%2C-95.679808%2C3.72).

## Data preprocessing

Code for data preprocessing can be found in `code/preprocess`. The preprocessing code was run in the following order:

```
python compile_average_aefs.py
python compile_average_mefs.py
python compile_average_dams.py
python tariff_timeseries.py
```

Which creates the following preprocessed data (note that this data has been saved to the repository for posterity, but should be recreated by the scripts exactly):

- `data/AEFs/`: average emission factors (AEFs) averaged by month and hour, with each region having its own CSV file (e.g., `CAISOaef.csv` or `ERCOTaef.csv`)
- `data/MEFs/average_mefs.csv`: marginal emission factor (MEF) samples as monthly/hourly average timeseries.
- `data/DAMs/`: average day-ahead market (DAM) price as monthly/hourly average timeseries, with each region having its own CSV file (e.g., `CAISOcosts.csv` or `ERCOTcosts.csv`).
  - ***NOTE***: `compile_average_dams.py` will throw an error without data provided by the user since we cannot re-publish the raw DAM data that we collected.
- `data/tariffs/bundled/timeseries` and `data/tariffs/delivery_only/timeseries`: tariffs are converted to timeseries format assuming a 1 MW load for future analysis.


## Data analysis

Code for data analysis can be found in `code/analyze`. The analysis code consists of the following stpes:

```
python min_max_emissions.py
python dam_mef_alignment.py
python tariff_aef_alignment.py
python bay_area_correlation.py
python correlation_versus_tariff_ratio.py
```

This should create the following results in the `data` folder:

- `data/correlation`: CSV files of the Pearson correlation coefficient by region for both DAM/MEF and Tariff/AEF.
  - ***NOTE***: `dam_mef_alignment.py` will throw an error without data provided by the user since we cannot re-publish the raw DAM data that we collected.
- `bay_area_correlation.py` does not produce any file output, but prints some statistics included in the manuscript and supplementary information.

## Data visualization

The final visualizations can be found in the `figures` folder after running all the scripts in `code/visualize`:

```
python figure2.py
python figure3.py
python figure4.py
python figure5.py
python figure6.py
python supplementary1.py
python supplementary2.py
python supplementary3.py
python supplementary4.py
```

Note that Figure 1 was made outside of Python. Figures 3, 5, and 6 and Supplmentary Figure 1 will throw errors without data provided by the user since we cannot re-publish the raw DAM data that was used to generate the published figures.

## References

[1] de Chalendar, J. A., Taggart, J., & Benson, S. M. (2019). Tracking emissions in the US electricity system. *Proceedings of the National Academy of Sciences, 116*(51), 25497-25502. https://doi.org/10.1073/pnas.1912950116 

[2] Siler-Evans, K., Azevedo, I. L., & Morgan, M. G. (2012). Marginal emissions factors for the US electricity system. *Environmental science & technology, 46*(9), 4742-4748. https://doi.org/10.1021/es300145v

[3] Chapin, F. T., Rao, A. K., Sakthivelu, A., Chen, C. S., & Mauter, M. S. (2025). *Industrial and Commercial Electricity Tariffs in the United States* (Version 2023.06.01) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.16739989

[4] David, E., Sakthivelu, A., Rao, A. K., & Mauter, M. S. (2024). *US incentive based demand response program parameters* (Version 2) [Data set]. https://doi.org/10.25740/ck480bd0124