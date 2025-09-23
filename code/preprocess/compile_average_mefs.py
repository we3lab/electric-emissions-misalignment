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

    file = glob.glob(folderpath + "/*.csv")
    if len(file) != 12:
        print(len(file))
        raise ValueError("There are not 12 files in the folder")

    regional_data = pd.DataFrame(columns=["month", "hour", "co2_eq_kg_per_MWh"])
    regional_data["month"] = regional_data["month"].astype(int)
    regional_data["hour"] = regional_data["hour"].astype(int)
    regional_data["co2_eq_kg_per_MWh"] = regional_data["co2_eq_kg_per_MWh"].astype(
        float
    )

    for month in range(1, 13):
        # grab the file that contains the month
        for f in file:
            if month_to_str[month] in f:
                df = pd.read_csv(f)
                co2i = df[:24]["sample_0"].values

                month_data = np.ones((24, 1)) * month
                hour_data = np.arange(24)

                # append
                regional_data = pd.concat(
                    [
                        regional_data,
                        pd.DataFrame(
                            np.hstack(
                                [
                                    month_data.reshape(-1, 1),
                                    hour_data.reshape(-1, 1),
                                    co2i.reshape(-1, 1),
                                ]
                            ),
                            columns=["month", "hour", "co2_eq_kg_per_MWh"],
                        ),
                    ],
                    axis=0,
                )

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
