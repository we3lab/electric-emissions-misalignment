import os
import pandas as pd

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo

month_map = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
mef_results_dict = {}
aef_results_dict = {}
iso_regions = ["CAISO", "ERCOT", "ISONE", "NYISO", "PJM", "SPP", "MISO"]
for region in iso_regions:
    mef_df = pd.read_csv(os.path.join(basepath, "data", "MEFs", region + "mef.csv"))
    aef_df = pd.read_csv(os.path.join(basepath, "data", "AEFs", region + "aef.csv"))
    
    mef_region_dict = {}
    aef_region_dict = {}
    for month in range(1, 13):
        min_mef = mef_df[mef_df["month"] == month]["co2_eq_kg_per_MWh"].min()
        max_mef = mef_df[mef_df["month"] == month]["co2_eq_kg_per_MWh"].max()
        min_aef = aef_df[aef_df["month"] == month]["co2_eq_kg_per_MWh"].min()
        max_aef = aef_df[aef_df["month"] == month]["co2_eq_kg_per_MWh"].max()

        mef_region_dict[month_map[month] + "_min"] = min_mef
        mef_region_dict[month_map[month] + "_max"] = max_mef
        aef_region_dict[month_map[month] + "_min"] = min_aef
        aef_region_dict[month_map[month] + "_max"] = max_aef

    mef_results_dict[region] = mef_region_dict
    aef_results_dict[region] = aef_region_dict

pd.DataFrame(mef_results_dict).to_csv(
    os.path.join(basepath, "data", "MEFs", "min_max_monthly_mef.csv")
)
pd.DataFrame(aef_results_dict).to_csv(
    os.path.join(basepath, "data", "AEFs", "min_max_monthly_aef.csv")
)



