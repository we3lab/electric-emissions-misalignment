# Electricity costs and emissions incentives are misaligned for commercial and industrial power consumers

Code and data for analysis and visualization accompanying our manuscript entitled "Electricity costs and emissions incentives are misaligned for commercial and industrial power consumers".

## Data sources

Raw data can be found in the `data` folder, when possible. All data used is from 2023.
Some data cannot be republished under MIT license, in which case links to the data sources are available below:

- *Average emission factors (AEFs)*: collected from United States Energy Information Administration (EIA) [Hourly Electric Grid Monitor](https://www.eia.gov/electricity/gridmonitor/about). Monthly/hourly averaged data available in `data/average_AEFs` folder.
- *Marginal emission factors (MEFs)*: computed using the method from Siler-Evans et al. [INSERT CITATION]. Monthly/hourly averaged data available in `data/average_mefs.csv`.
- *Electricity tariffs*: `industrial-electricity-tariffs` available on [Zenodo](https://doi.org/10.5281/zenodo.16739989) and [GitHub](https://github.com/we3lab/industrial-electricity-tariffs).
- *Day-ahead market (DAM) prices*: downloaded from [GridStatus](https://gridstatus.io/). Data not available for re-publication.
- *Incentive-based demand response (IBDR)*: the Incentive Demand Response Program Parameter (IDroPP) dataset is available from the [Stanford Digital Repository as ["US incentive based demand response program parameters"](https://doi.org/10.25740/ck480bd0124).

## Data preprocessing

Code for data analysis can be found in `code/preprocess`. 

## Data analysis

Code for data analysis can be found in `code/analyze`. 

## Data visualization

The final visualizations can be found in the `figures` folder.

## References

Siler-Evans et al. ...