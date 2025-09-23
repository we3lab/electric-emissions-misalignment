import os
import glob
import pandas as pd

basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo
folderpath = os.path.join(basepath, "data", "LMPs", region)

regions = ["CAISO", "ERCOT", "MISO", "NYISO", "PJM", "SPP", "ISONE"]
for region in regions:
    files = glob.glob(os.path.join(folderpath, "AEFs", region, "*.csv"))
    df_aggregate = pd.DataFrame(columns=["month", "hour", "co2_eq_kg_per_MWh"])

    for f in files:
        print(f)
        tmp = pd.read_csv(f)
        # add the month from the local timestamp
        months = pd.to_datetime(tmp["DateTime"], format="%Y-%m-%d %H:%M:%S", errors="coerce").dt.month.values
        hours = pd.to_datetime(tmp["DateTime"], format="%Y-%m-%d %H:%M:%S", errors="coerce").dt.hour.values
        power = tmp["co2_eq_kg_per_MWh"].values

        # add to the aggregate dataframe
        df_aggregate = pd.concat([df_aggregate, pd.DataFrame({"month": months, "hour": hours, "co2_eq_kg_per_MWh": power})], ignore_index=True)

    # sort df_aggregate by month
    df_aggregate = df_aggregate.sort_values(by=["month", "hour"], ascending=[True, True], ignore_index=True)

    # average by month and hour
    df_aggregate = df_aggregate.groupby(["month", "hour"]).mean().reset_index()
    
    # save as csv
    df_aggregate.to_csv(f"{region}aef.csv", index=False)
