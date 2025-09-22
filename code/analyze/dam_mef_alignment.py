import os
import numpy as np
import pandas as pd
import eeco.utils as ut

# disable SettingWithCopyWarning
pd.options.mode.chained_assignment = None 

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # should be the root of the repo

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
    12: "Dec"
}
iso_regions = ["CAISO", "ERCOT", "ISONE", "NYISO", "PJM", "SPP", "MISO"]

corr_dict = {}
mef_data = pd.read_csv(os.path.join(basepath, "data", "MEFs", "average_mefs.csv"))
for _iso in iso_regions:
    corr_dict[_iso] = []
    for _month in range(1,13):
        _days_in_month = pd.Period(f"2023-{_month}-01").days_in_month
        if _month == 12:
            datetime_series = pd.date_range(
                start="2023-{}-01".format(_month), 
                end="2024-01-01", 
                freq="1h"
            )[:-1]
        else:
            datetime_series = pd.date_range(
                start="2023-{}-01".format(_month), 
                end="2023-{}-01".format(_month+1), 
                freq="1h"
            )[:-1]
        print(f"{_iso} in month {_month}")
        if _iso in ["CAISO", "ISONE", "NYISO", "PJM"]:
            lmp_data = pd.read_csv(
                f"data/local/2023/LMP/{_iso}/unprocessed/{_iso}_DAM_2023_{month_map[_month]}_HOUR_RAW.csv",
                parse_dates=["Time"]
            )
            tmp = lmp_data["Time"].apply(
                    lambda x: pd.to_datetime(x, utc=True).tz_convert(
                        ut.TIMEZONE_DICT["iso_rto_code"][_iso]
                    ).replace(tzinfo=None)
                )
            lmp_data["Time"] = tmp
        elif _iso == "SPP":
            lmp_no_time = pd.read_csv(
                f"data/local/2023/LMP/{_iso}/unprocessed/{_iso}_DAM_2023_{month_map[_month]}_HOUR_RAW.csv",
                parse_dates=["Date"]
            )
            lmp_data = []
            for timestamp in datetime_series:
                hour = timestamp.hour
                if hour == 0:
                    hour_str = " HE01"
                elif hour < 9:
                    hour_str = "HE0" + str(hour+1)
                else:
                    hour_str = "HE" + str(hour+1)
                
                rows = lmp_no_time[
                    (lmp_no_time["Date"].dt.month == timestamp.month)
                    & (lmp_no_time["Date"].dt.day == timestamp.day)
                    & (lmp_no_time[" Price Type"] == "LMP")
                ]
                for _, row  in rows.iterrows():
                    if not pd.isna(row[hour_str]):
                        new_row = {
                            "Time": timestamp,
                            "Location": row[" Settlement Location Name"],
                            "LMP": row[hour_str]
                        }
                        lmp_data.append(new_row)
            lmp_data = pd.DataFrame(lmp_data)
        elif _iso == "MISO":
            lmp_no_time = pd.read_csv(
                f"data/local/2023/LMP/{_iso}/unprocessed/{_iso}_DAM_2023_HOUR.csv",
                parse_dates=["MARKET_DAY"]
            )
            lmp_data = []
            for timestamp in datetime_series:
                hour = timestamp.hour
                hour_str = "HE" + str(hour+1)
                
                rows = lmp_no_time[
                    (lmp_no_time["MARKET_DAY"].dt.month == timestamp.month)
                    & (lmp_no_time["MARKET_DAY"].dt.day == timestamp.day)
                    & (lmp_no_time["VALUE"] == "LMP")
                ]
                for _, row in rows.iterrows():
                    new_row = {
                        "Time": timestamp,
                        "Location": row["NODE"],
                        "LMP": row[hour_str]
                    }
                    lmp_data.append(new_row)
            lmp_data = pd.DataFrame(lmp_data)
        else:
            lmp_data = pd.read_csv(
                f"data/local/2023/LMP/{_iso}/unprocessed/{_iso}_DAM_2023_HOUR.csv",
                parse_dates=["Time"]
            )
            tmp = lmp_data["Time"].apply(
                    lambda x: pd.to_datetime(x, utc=True).tz_convert(
                        ut.TIMEZONE_DICT["iso_rto_code"][_iso]
                    ).replace(tzinfo=None)
                )
            lmp_data["Time"] = tmp
            lmp_data = lmp_data[lmp_data["Time"].dt.month == _month]
        mef_hourly_profile = mef_data[(mef_data["month"] == _month) & (mef_data["isorto"] == _iso)]
        mef_sample_data = pd.DataFrame({"timestamp": pd.to_datetime(datetime_series)})
        mef_sample_data["co2_eq_kg_per_MWh"] = mef_sample_data.map(
            lambda row: mef_hourly_profile[(mef_hourly_profile["hour"] == row.hour)]["co2_eq_kg_per_MWh"].values[0]
        )
        location_colname = "Location"
        try:
            locations = lmp_data[location_colname].unique()
        except KeyError:
            location_colname = "Location Id"
            locations = lmp_data[location_colname].unique()
        for location in locations:
            mef_values = mef_sample_data["co2_eq_kg_per_MWh"].values
            lmp_sample = lmp_data[lmp_data[location_colname] == location]
            if (lmp_sample.shape[0] - mef_sample_data.shape[0]) != 0:
                if _iso == "SPP":
                    # SPP is missing the first few hours of each month
                    mef_values = mef_values[len(mef_values)-len(lmp_sample):]
                else:
                    # interpolate the missing LMP data for the month
                    lmp_sample = lmp_sample.set_index("Time")
                    # remove the duplicate timestamps
                    lmp_sample = lmp_sample[~lmp_sample.index.duplicated(keep="first")]
                    # resample the data to hourly
                    lmp_sample = lmp_sample.resample("h").ffill()
                    lmp_sample["LMP"] = lmp_sample["LMP"].interpolate(method="time")
                    lmp_sample = lmp_sample.reset_index()
            try:
                pp = np.corrcoef(mef_values, pd.to_numeric(lmp_sample["LMP"]).values)[0,1]
                corr_dict[_iso].append({
                    "location": location,
                    "month": _month,
                    "pearson_cc": pp,
                })
            except (ValueError, TypeError) as ex:
                print("Error for location {}: ".format(location), ex)

    pp_value = pd.DataFrame(corr_dict[_iso]).set_index("location")
    pp_value.to_csv(f"data/correlation/{_iso}_mef_pearson.csv")