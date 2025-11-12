import os
import glob
import pandas as pd

corr_comparison_dict = {
    "region": [],
    "month": [],
    "tariff_id": [],
    "pearson_cc": [],
    "tariff_ratio": [],
}
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


basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo
tariff_path = os.path.join(basepath, "data", "tariffs", "bundled", "timeseries", "combined")
tariff_files = glob.glob(tariff_path + "/*.csv")

metadata_path = os.path.join(basepath, "data", "tariffs", "bundled", "metadata.csv")
metadata_df = pd.read_csv(metadata_path)

for tariff_file in tariff_files:
    tariff_id = os.path.basename(tariff_file).split("_")[1].split(".")[0]
    tariff_timeseries = pd.read_csv(tariff_file)
    region = metadata_df[metadata_df["label"] == tariff_id]["ISO"].values[0]
    if pd.isna(region):
        corr_coefs = pd.DataFrame({})
    else:
        corr_coefs = pd.read_csv(
            os.path.join(basepath, f"data/correlation/{region}_aef_pearson.csv")
        )
        corr_coefs.set_index("tariff_ids", inplace=True)
    for month in range(1, 13):
        corr_comparison_dict["region"].append(region)
        corr_comparison_dict["month"].append(month)
        corr_comparison_dict["tariff_id"].append(tariff_id)
        try:
            corr_comparison_dict["pearson_cc"].append(
                corr_coefs.loc[tariff_id][months[month - 1]]
            )
        except KeyError:
            corr_comparison_dict["pearson_cc"].append(pd.NA)
        monthly_max = tariff_timeseries[tariff_timeseries["Month"] == month][
            "Cost"
        ].max()
        monthly_min = tariff_timeseries[tariff_timeseries["Month"] == month][
            "Cost"
        ].min()
        ratio = monthly_max / monthly_min
        corr_comparison_dict["tariff_ratio"].append(ratio)

correlation_ratio_df = pd.DataFrame(corr_comparison_dict)
correlation_ratio_df.to_csv(
    os.path.join(basepath, "data", "correlation", "corr_coef_tariff_ratio.csv"),
    index=False,
)
