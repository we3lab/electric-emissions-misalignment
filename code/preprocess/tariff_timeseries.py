import os
import glob
import numpy as np
import pandas as pd
from eeco.costs import (
    get_next_limit,
    calculate_energy_cost,
    calculate_demand_cost,
    get_charge_dict,
)


def calculate_energy_charge_timeseries(
    tariff, charge_dict, load_array, consumption_estimate
):
    result = np.zeros(len(load_array))
    # loop through energy charges
    for key, charge_array in charge_dict.items():
        utility, charge_type, name, eff_start, eff_end, limit_str = key.split("_")
        # if we want itemized costs skip irrelvant portions of the bill
        if (utility != "electric") or (charge_type != "energy"):
            continue

        charge_limit = int(limit_str)
        key_substr = "_".join([utility, charge_type, name, eff_start, eff_end])
        next_limit = get_next_limit(key_substr, charge_limit, charge_dict.keys())

        # calculate the cost of each charge
        cost, _ = calculate_energy_cost(
            charge_array,
            load_array,
            divisor=4,
            limit=charge_limit,
            next_limit=next_limit,
            prev_consumption=0,
            consumption_estimate=consumption_estimate,
        )

        # divide the charge over the course of a month
        charges_present = np.ones(len(load_array))
        charges_present[charge_array != 0] = 0
        num_steps = np.sum(charges_present)
        if num_steps > 0:
            result = result + charges_present * cost / num_steps

    return result


def calculate_demand_charge_timeseries(
    tariff, charge_dict, load_array, consumption_estimate
):
    result = np.zeros(len(load_array))
    # loop through energy charges
    for key, charge_array in charge_dict.items():
        utility, charge_type, name, eff_start, eff_end, limit_str = key.split("_")
        # if we want itemized costs skip irrelvant portions of the bill
        if (utility != "electric") or (charge_type != "demand"):
            continue

        charge_limit = int(limit_str)
        key_substr = "_".join([utility, charge_type, name, eff_start, eff_end])
        next_limit = get_next_limit(key_substr, charge_limit, charge_dict.keys())

        # calculate the cost of each charge
        cost, _ = calculate_demand_cost(
            charge_array,
            load_array,
            limit=charge_limit,
            next_limit=next_limit,
            prev_demand=0,
            prev_demand_cost=0,
            consumption_estimate=consumption_estimate,
        )

        # divide the charge over the course of a month when the charge was nonzero
        charges_present = np.ones(len(load_array))
        charges_present[charge_array != 0] = 0
        num_steps = np.sum(charges_present)
        if num_steps > 0:
            result = result + charges_present * cost / num_steps

    return result


def create_monthly_timeseries(tariff, month, load_kw=1000):
    if month == 12:
        start_dt = np.datetime64("2024-" + str(month) + "-01")
        end_dt = np.datetime64("2025-01-01")
    elif month > 9:
        start_dt = np.datetime64("2024-" + str(month) + "-01")
        end_dt = np.datetime64("2024-" + str(month + 1) + "-01")
    elif month == 9:
        start_dt = np.datetime64("2024-09-01")
        end_dt = np.datetime64("2024-10-01")
    else:
        start_dt = np.datetime64("2024-0" + str(month) + "-01")
        end_dt = np.datetime64("2024-0" + str(month + 1) + "-01")

    # get the charge dictionary
    charge_dict = get_charge_dict(start_dt, end_dt, tariff, resolution="15m")

    # define a dummy 1MW flat load
    datetime_range = pd.date_range(start=start_dt, end=end_dt, freq="15min")
    flat_load = np.ones(len(datetime_range) - 1) * load_kw
    consumption_estimate = np.sum(flat_load) * 0.25
    result = pd.DataFrame()
    result["DateTime"] = datetime_range[:-1]
    result["Cost"] = calculate_demand_charge_timeseries(
        tariff, charge_dict, flat_load, consumption_estimate
    ) + calculate_energy_charge_timeseries(
        tariff, charge_dict, flat_load, consumption_estimate
    )
    return result


# get a list of all the tariffs
basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo
timeseries_path = os.path.join(basepath, "data", "tariffs", "timeseries")
tariff_list = glob.glob(
    os.path.join(basepath, "data", "tariffs", "processed_sheets", "*.csv")
)

num_month_to_str = {
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

# loop through create_monthly_timeseries for each tariff and month
for month in range(1, 13):
    for tariff in tariff_list:
        tariff_df = pd.read_csv(tariff)
        result = create_monthly_timeseries(tariff_df, month)
        path_prefix = os.path.basename(tariff).split(".")[0]
        outpath = os.path.join(timeseries_path, path_prefix + "_" + num_month_to_str[month] + ".csv")
        result.to_csv(outpath, index=False)

tariff_files = glob.glob(timeseries_path + "/*.csv")

# sort through tariff files and group all identical tariff identifiers
tariff_dict = {}
for tariff_file in tariff_files:
    tariff_id = os.path.basename(tariff_file).split("_")[0]
    if tariff_id not in tariff_dict:
        tariff_dict[tariff_id] = []
    tariff_dict[tariff_id].append(tariff_file)

# combine the tariffs in the `data/tariffs/timeseries/combined` folder
combine_sheets = True
if combine_sheets:
    for key, files in tariff_dict.items():
        combined_df = pd.DataFrame(columns=["Month", "Hour", "Cost"])
        for f in files:
            tmp = pd.read_csv(f, parse_dates=["DateTime"])
            # add a month and hour column to the dataframe
            tmp["Month"] = tmp["DateTime"].dt.month
            tmp["Hour"] = tmp["DateTime"].dt.hour
            # drop the DateTime column
            tmp = tmp.drop(columns=["DateTime"])
            # group by month and hour and take the mean cost
            tmp = tmp.groupby(["Month", "Hour"]).mean().reset_index()
            # add tmp to combined_df
            combined_df = pd.concat([combined_df, tmp], ignore_index=True)
        # sort by month and hour
        combined_df = combined_df.sort_values(by=["Month", "Hour"]).reset_index(
            drop=True
        )
        # save the combined dataframe to a csv file
        combined_df.to_csv(
            os.path.join(timeseries_path, f"combined/tariff_{key}.csv"), index=False
        )
