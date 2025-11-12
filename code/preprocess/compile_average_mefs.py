import pandas as pd
import numpy as np
import glob
import os

regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]

national_data = None

for region in regions:
    basepath = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )  # should be the root of the repo
    folderpath = os.path.join(basepath, "data", "MEFs", region)
    month_to_str = {
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

    files = glob.glob(folderpath + "/*.csv")
    if len(files) != 12:
        print(len(files))
        raise ValueError("There are not 12 files in the folder")

    regional_data = pd.DataFrame(columns=["month", "hour", "co2_eq_kg_per_MWh"])
    regional_data["month"] = regional_data["month"].astype(int)
    regional_data["hour"] = regional_data["hour"].astype(int)
    regional_data["co2_eq_kg_per_MWh"] = regional_data["co2_eq_kg_per_MWh"].astype(
        float
    )

    # grab the files that contains the month
    for f in files:
        tmp = pd.read_csv(f)
        # add the month from the local timestamp
        months = pd.to_datetime(
            tmp["datetime_local"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        ).dt.month.values
        hours = pd.to_datetime(
            tmp["datetime_local"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        ).dt.hour.values
        emission_factors = tmp.iloc[:, 1:].mean(
            axis=1
        )  # grab all but the datetime column
        # add to the aggregate dataframe
        regional_data = pd.concat(
            [
                regional_data,
                pd.DataFrame(
                    {
                        "month": months,
                        "hour": hours,
                        "co2_eq_kg_per_MWh": emission_factors,
                    }
                ),
            ],
            ignore_index=True,
        )

    # sort df_aggregate by month
    regional_data = regional_data.sort_values(
        by=["month", "hour"], ascending=[True, True], ignore_index=True
    )

    # average by month and hour
    regional_data = regional_data.groupby(["month", "hour"]).mean().reset_index()

    # save the data
    regional_data = regional_data.reset_index(drop=True)
    regional_data.to_csv(
        os.path.join(basepath, "data", "MEFs", region + "mef.csv"), index=False
    )

    # merge regional data with national data
    if national_data is None:
        national_data = regional_data.copy()
        national_data["isorto"] = region
    else:
        regional_data["isorto"] = region
        national_data = pd.concat([national_data, regional_data])

# save national data to CSV
national_data.to_csv(
    os.path.join(basepath, "data", "MEFs", "average_mefs.csv"), index=False
)
