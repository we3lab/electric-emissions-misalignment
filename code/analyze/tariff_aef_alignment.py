import os
import glob
import numpy as np
import pandas as pd

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo


def get_sample_tariff_data(
    iso_monthly_tariffs, region, month, aef_values, iso_tariff_ids
):
    corr_coefs = []
    tariff_files = iso_monthly_tariffs[region][month]
    print(f"{region} {month} unfiltered: {len(tariff_files)}")
    tariff_df_list = [pd.read_csv(file) for file in tariff_files]
    # exclude nan values
    tariff_dfs = [
        df["Cost"].values for df in tariff_df_list if not df["Cost"].isna().all()
    ]
    desired_idx = [~df["Cost"].isna().all() for df in tariff_df_list]
    filtered_tariff_ids = np.array(iso_tariff_ids)[desired_idx]
    print(f"{region} {month} filtered: {len(filtered_tariff_ids)}")
    tariff_dfs = np.array(tariff_dfs)
    for tariff in tariff_dfs:
        tariff_data = pd.DataFrame(
            {"DateTime": tariff_df_list[0]["DateTime"], "Cost": tariff}
        )
        tariff_data["DateTime"] = pd.to_datetime(tariff_data["DateTime"])
        tariff_data = tariff_data.resample("h", on="DateTime").mean()
        if len(tariff_data.values) == len(aef_values):
            pp = np.corrcoef(aef_values, tariff_data["Cost"].values)[0, 1]
        else:
            end = len(aef_values)
            pp = np.corrcoef(tariff_data.values.flatten()[:end], aef_values)[0][1]
        corr_coefs.append(pp)
    return corr_coefs, filtered_tariff_ids


tariff_path = os.path.join(basepath, "data", "tariffs", "timeseries")
tariff_files = glob.glob(tariff_path + "/*.csv")

# sort through tariff files split _[1] and group all identical tariff identifiers
tariff_dict = {}
for tariff_file in tariff_files:
    tariff_id = os.path.basename(tariff_file).split("_")[0]
    if tariff_id not in tariff_dict:
        tariff_dict[tariff_id] = []
    tariff_dict[tariff_id].append(tariff_file)

metadata_path = os.path.join(basepath, "data", "tariffs", "metadata.csv")
metadata = pd.read_csv(metadata_path)

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
regions = [region for region in metadata["ISO"].unique() if isinstance(region, str)]

iso_tariff_label_dict = {}
for region in regions:
    iso_tariff_label_dict[region] = metadata.loc[
        metadata["ISO"] == region, "label"
    ].values
    print(region, len(iso_tariff_label_dict[region]))

iso_monthly_tariffs = {
    region: {month: [] for month in months}
    for region in regions
    if isinstance(region, str)
}
tariff_ids = {region: [] for region in regions if isinstance(region, str)}

# Process each region's tariffs
for region in regions:
    # Get all tariff IDs for this region
    region_tariff_ids = iso_tariff_label_dict[region]

    # Process each tariff ID
    for tariff_id in region_tariff_ids:
        if tariff_id not in tariff_dict:
            continue
        else:
            tariff_ids[region].append(tariff_id)

        # Process each month's file for this tariff
        for file_path in tariff_dict[tariff_id]:
            # Extract month from filename
            month = os.path.basename(file_path).split("_")[-1].split(".")[0]
            iso_monthly_tariffs[region][month].append(file_path)

corr_dict = {}
for region in regions:
    corr_dict[region] = {}
    corr_df = None
    for month in months:
        corr_dict[region][month] = {}
        aef_data = pd.read_csv(
            f"data/AEFs/{region}/{region}_aef_historical_{month}_HOUR.csv"
        )
        aef_values = aef_data["co2_eq_kg_per_MWh"].values
        corr_dict[region][month][month], corr_dict[region][month]["tariff_ids"] = (
            get_sample_tariff_data(
                iso_monthly_tariffs, region, month, aef_values, tariff_ids[region]
            )
        )

        monthly_df = pd.DataFrame(corr_dict[region][month])
        if corr_df is None:
            corr_df = monthly_df.copy()
        else:
            corr_df = pd.merge(corr_df, monthly_df)

    corr_df.set_index("tariff_ids", inplace=True)
    corr_df.to_csv(f"data/correlation/{region}_aef_pearson.csv")
