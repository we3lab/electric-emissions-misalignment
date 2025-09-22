# Electricity costs and emissions incentives are misaligned for commercial and industrial power consumers

Code and data for analysis and visualization accompanying our manuscript entitled "Electricity costs and emissions incentives are misaligned for commercial and industrial power consumers".

## Data sources

Raw data can be found in the `data` folder, when possible. All data used is from 2023.
Some data cannot be republished under MIT license, in which case links to the data sources are available below:

- *Average emission factors (AEFs)*: collected from United States Energy Information Administration (EIA) [Hourly Electric Grid Monitor](https://www.eia.gov/electricity/gridmonitor/about). Monthly/hourly averaged data available in `data/AEFs` folder, and raw data by ISO is available in subfolders.
- *Marginal emission factors (MEFs)*: computed using the method from Siler-Evans et al. [1]. Monthly/hourly averaged data available in `data/MEFs/average_mefs.csv`, with Monte Carlo simulations available in subfolders.
- *Electricity tariffs*: `industrial-electricity-tariffs` is updated monthly on [Zenodo](https://doi.org/10.5281/zenodo.16739989) and [GitHub](https://github.com/we3lab/industrial-electricity-tariffs). Archived data applicable to 2023 available in `data/tariffs/processed_sheets` folder.
- *Day-ahead market (DAM) prices*: downloaded from [GridStatus](https://gridstatus.io/). Data not available for re-publication, but to re-create analysis a user should save monthly/hourly averages to the `data/LMPs` folder with columns `month`, `hour`, and `USD_per_MWh`. Each region should have its own CSV file (e.g., `CAISOcosts.csv` and `ERCOTcosts.csv`).
- *Incentive-based demand response (IBDR)*: the Incentive Demand Response Program Parameter (IDroPP) dataset is available from the [Stanford Digital Repository as ["US incentive based demand response program parameters"](https://doi.org/10.25740/ck480bd0124). Data relevant to our analysis copied to `data/IBDR` folder.

## Data preprocessing

Code for data analysis can be found in `code/preprocess`. The preprocessing code was ran in the following order:

```
python tariff_timeseries.py
```

Which creates the following preprocessed data:

- `data/tariffs/timeseries`: tariffs are converted to timeseries format assuming a 1 MW load for future analysis
- 

## Data analysis

Code for data analysis can be found in `code/analyze`. 

## Data visualization

The final visualizations can be found in the `figures` folder.

## References

[1] Siler-Evans et al. ...