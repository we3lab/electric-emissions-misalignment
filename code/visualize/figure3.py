import os
import copy
import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
from eeco.costs import get_charge_dict, calculate_cost

basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo

# define plotting defaults
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 7,
        "axes.linewidth": 1.5,
        "lines.linewidth": 2,
        "lines.markersize": 5,
        "xtick.major.size": 3,
        "xtick.major.width": 1,
        "ytick.major.size": 3,
        "ytick.major.width": 1,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "ytick.labelsize": 7,
        "xtick.labelsize": 7,
    }
)


def calculate_charge_summary(df, datetime_range):
    effective_start_date = datetime_range[0]
    effective_end_date = datetime_range[-1]

    # get the charge dictionary
    charge_dict = get_charge_dict(
        effective_start_date, effective_end_date, df, resolution="15m"
    )

    # define a dummy 1MW flat load
    flat_load = np.ones(len(datetime_range) - 1) * 1000
    consumption = np.sum(flat_load) * 0.25

    # calculate costs
    total_monthly_cost, _ = calculate_cost(
        charge_dict=charge_dict,
        consumption_data_dict={"electric": flat_load},
        resolution="15m",
        prev_demand_dict=None,
        consumption_estimate=consumption,
        desired_utility="electric",
        desired_charge_type=None,
    )
    total_average_cost_kwh = total_monthly_cost / (consumption)

    # define some dictionaries to store the results
    charge_ratios = {"energy": 0, "demand": 0}
    charge_means = {"energy": 0, "demand": 0}
    charge_maxs = {"energy": 0, "demand": 0}
    charge_tiers = {"energy": 0, "demand": 0}

    # loop through charge types
    for charge_type in ["energy", "demand"]:
        relevant_keys = [key for key in charge_dict.keys() if charge_type in key]
        # when this was missing we had massive errors because natural gas is more expensive
        relevant_keys = [key for key in relevant_keys if "electric" in key]

        # extract the number of tiers
        tiers = []
        for key in relevant_keys:
            tier = int(key.split("_")[-1])
            if tier not in tiers:
                tiers.append(tier)

        charge_tiers[charge_type] = len(tiers)

        for tier in tiers:
            aggregate_charge = np.zeros(len(charge_dict[relevant_keys[0]]))

            for key in relevant_keys:
                aggregate_charge += np.array(charge_dict[key])

            max_charge = max(aggregate_charge)
            if max_charge > charge_maxs[charge_type]:
                charge_maxs[charge_type] = max_charge

            if min(aggregate_charge) != 0:
                ratio = max_charge / min(aggregate_charge)
            else:
                ratio = 0

            if ratio > charge_ratios[charge_type]:
                charge_ratios[charge_type] = ratio

            charge_means[charge_type] = np.nanmean(aggregate_charge)

    # compile results
    charge_summary = {
        "charge_label": df["label"].iloc[0],
        "total_monthly_cost": total_monthly_cost,
        "total_average_cost_kwh": total_average_cost_kwh,
        "energy_charge_ratio": charge_ratios["energy"],
        "demand_charge_ratio": charge_ratios["demand"],
        "mean_energy_charge": charge_means["energy"],
        "mean_demand_charge": charge_means["demand"],
        "max_energy_charge": charge_maxs["energy"],
        "max_demand_charge": charge_maxs["demand"],
        "energy_tiers": charge_tiers["energy"],
        "demand_tiers": charge_tiers["demand"],
    }

    return charge_summary


## Loop through all tariffs
# get a list of all the tariffs
tariff_list = glob.glob(
    os.path.join(basepath, "data", "tariffs", "processed_sheets", "*.csv")
)

# define a placeholder dataframe to store the results
df_charges_summer = pd.DataFrame(
    columns=[
        "total_monthly_cost",
        "total_average_cost_kwh",
        "energy_charge_ratio",
        "demand_charge_ratio",
        "mean_energy_charge",
        "mean_demand_charge",
        "max_energy_charge",
        "max_demand_charge",
        "energy_tiers",
        "demand_tiers",
    ]
)
df_charges_winter = df_charges_summer.copy()

# define the date ranges for the sample case
summer_daterange = pd.date_range(start="2024-07-05", end="2024-08-05", freq="15min")
winter_daterange = pd.date_range(start="2024-01-05", end="2024-02-05", freq="15min")
# loop through the tariff list and concat the results to the dataframe
for tariff in tariff_list:
    # read the tariff sheet
    df = pd.read_csv(tariff)

    # try to calculate and append the charge summary for summer and winter separately
    # try:
    charge_summary = calculate_charge_summary(df, summer_daterange)
    df_charges_summer = pd.concat(
        [df_charges_summer, pd.DataFrame(charge_summary, index=[tariff])],
        ignore_index=True,
    )
    # except:
    #     print("Failure for tariff:", tariff)
    #     pass
    try:
        charge_summary = calculate_charge_summary(df, winter_daterange)
        df_charges_winter = pd.concat(
            [df_charges_winter, pd.DataFrame(charge_summary, index=[tariff])],
            ignore_index=True,
        )
    except:
        print("Failure for tariff:", tariff)
        pass

# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(4, 2, figsize=(190 / 25.4, 240 / 25.4))

## Subplot A: Summer Energy Charges
ax[0, 0].scatter(
    df_charges_summer["mean_energy_charge"].values,
    df_charges_summer["energy_charge_ratio"],
    color="#A1645E",
    alpha=0.7,
    label="Summer",
    edgecolor="black",
)
ax[0, 0].axhline(y=1, color="black", linestyle="--", linewidth=2, label="Flat charge")
ax[0, 0].set(
    xlabel="Mean energy charge\n($/kWh)",
    ylabel="Peak Energy Charge Premium\n(max/min)",
    xlim=(0, 1.25),
    ylim=(0, 100),
)
ax_inset = ax[0, 0].inset_axes(
    [0.4, 0.4, 0.55, 0.55]
)  # x, y, width, height (fractions of parent axes)
ax_inset.scatter(
    df_charges_summer["mean_energy_charge"].values,
    df_charges_summer["energy_charge_ratio"],
    color="#A1645E",
    alpha=0.7,
    label="Summer",
    edgecolor="black",
)
ax_inset.axhline(y=1, color="black", linestyle="--", linewidth=2, label="Flat charge")

mean_energy_99 = df_charges_summer["mean_energy_charge"].quantile(0.99)
energy_ratio_99 = np.round(df_charges_summer["energy_charge_ratio"].quantile(0.99))

ax_inset.set(
    # xlim=np.round((0, mean_energy_99),3),
    xlim=np.round((0, 0.5), 3),
    # xticks=np.arange(0, mean_energy_99*1.01, 0.2),
    xticks=np.arange(0, 0.6, 0.25),
    ylim=(1, energy_ratio_99),
    yticks=np.arange(1, energy_ratio_99 + 1, 1),
)

## Subplot B: Winter Energy Charges
ax[0, 1].scatter(
    df_charges_winter["mean_energy_charge"].values,
    df_charges_winter["energy_charge_ratio"],
    color="#5E9BA1",
    alpha=1,
    label="Winter",
    edgecolor="black",
)
ax[0, 1].axhline(y=1, color="black", linestyle="--", linewidth=2, label="Flat charge")
ax[0, 1].set(
    xlabel="Mean energy charge\n($/kWh)",
    ylabel="Peak Energy Charge Premium\n(max/min)",
    xlim=(0, 1.25),
    ylim=(0, 40),
)

ax_inset = ax[0, 1].inset_axes(
    [0.4, 0.4, 0.55, 0.55]
)  # x, y, width, height (fractions of parent axes)
ax_inset.scatter(
    df_charges_winter["mean_energy_charge"].values,
    df_charges_winter["energy_charge_ratio"],
    color="#5E9BA1",
    alpha=1,
    label="Winter",
    edgecolor="black",
)

mean_energy_99 = df_charges_winter["mean_energy_charge"].quantile(0.99)
energy_ratio_99 = np.round(df_charges_winter["energy_charge_ratio"].quantile(0.99))

ax_inset.set(
    # xlim=np.round((0, mean_energy_99),3),
    xlim=np.round((0, 0.5), 3),
    # xticks=np.arange(0, mean_energy_99*1.01, 0.2),
    xticks=np.arange(0, 0.6, 0.25),
    ylim=(1, energy_ratio_99),
    yticks=np.arange(1, energy_ratio_99 + 1, 1),
)

## Subplot C: Summer Demand Charges
# replace all the demand charge ratios < 1 with -1
df_charges_summer["demand_charge_ratio"] = df_charges_summer[
    "demand_charge_ratio"
].replace({0: -1})

ax[1, 0].scatter(
    df_charges_summer["max_demand_charge"].values,
    df_charges_summer["demand_charge_ratio"].values,
    color="#A1645E",
    alpha=1,
    edgecolor="black",
    label="Summer",
)

ax[1, 0].set(
    xlabel="Max demand charge\n($/kW)",
    ylabel="Peak Demand Charge Premium\n(max/min)",
    xlim=(0, 100),
    ylim=(0, 120),
)

ax[1, 0].axhline(y=1, color="black", linestyle="--", linewidth=2, label="Flat charge")

max_demand_99 = df_charges_summer["max_demand_charge"].quantile(0.99)
demand_ratio_99 = np.round(df_charges_summer["demand_charge_ratio"].quantile(0.99))
ax_inset = ax[1, 0].inset_axes(
    [0.4, 0.4, 0.55, 0.55]
)  # x, y, width, height (fractions of parent axes)
ax_inset.scatter(
    df_charges_summer["max_demand_charge"].values,
    df_charges_summer["demand_charge_ratio"],
    color="#A1645E",
    alpha=1,
    label="Summer",
    edgecolor="black",
)

ax_inset.set(
    xlim=np.round((0, max_demand_99), 3),
    # xticks=np.arange(0, max_demand_99*1.01, 20),
    xticks=np.arange(0, 60.1, 20),
    ylim=(1, demand_ratio_99),
    # yticks=np.arange(0, demand_ratio_99+1, 4),
    yticks=np.arange(0, 15.1, 3),
)

## Subplot D: Winter Demand Charges
# replace all the demand charge ratios < 1 with -1
df_charges_winter["demand_charge_ratio"] = df_charges_winter[
    "demand_charge_ratio"
].replace({0: -1})

ax[1, 1].scatter(
    df_charges_winter["max_demand_charge"].values,
    df_charges_winter["demand_charge_ratio"].values,
    color="#5E9BA1",
    alpha=1,
    edgecolor="black",
    label="Winter",
)

ax[1, 1].set(
    xlabel="Max demand charge\n($/kW)",
    ylabel="Peak Demand Charge Premium\n(max/min)",
    xlim=(0, 100),
    ylim=(0, 100),
)

ax[1, 1].axhline(y=1, color="black", linestyle="--", linewidth=2, label="Flat charge")

max_demand_99 = df_charges_winter["max_demand_charge"].quantile(0.99)
demand_ratio_99 = np.round(df_charges_winter["demand_charge_ratio"].quantile(0.99))

ax_inset = ax[1, 1].inset_axes(
    [0.4, 0.4, 0.55, 0.55]
)  # x, y, width, height (fractions of parent axes)
ax_inset.scatter(
    df_charges_winter["max_demand_charge"].values,
    df_charges_winter["demand_charge_ratio"],
    color="#5E9BA1",
    alpha=1,
    label="Winter",
    edgecolor="black",
)
ax_inset.set(
    xlim=np.round((0, max_demand_99), 3),
    # xticks=np.arange(0, max_demand_99*1.01, 20),
    xticks=np.arange(0, 60.1, 20),
    ylim=(1, demand_ratio_99),
    # yticks=np.arange(0, demand_ratio_99+1, 4),
    yticks=np.arange(0, 15.1, 3),
)

## Subplot E: Charge Tiers
# create a matrix that represents the frequency of the energy and demand charge tiers
tier_matrix = np.zeros((6, 9))
for index, row in df_charges_summer.iterrows():
    tier_matrix[int(row["demand_tiers"]), int(row["energy_tiers"])] += 1

cax = ax[2, 0].matshow(tier_matrix, cmap="bone_r", vmin=0, vmax=1000)

# fig.colorbar(cax)

ax[2, 0].set_xticks(np.arange(0, 4.5, 1))
ax[2, 0].set_yticks(np.arange(0, 3.5, 1))
ax[2, 0].set(xlim=(-0.5, 4.5), ylim=(-0.5, 3.5))

ax[2, 0].xaxis.tick_bottom()
ax[2, 0].set(xlabel="Energy Charge Tiers", ylabel="Demand Charge Tiers\n")
# set a color bar label
cbar = fig.colorbar(cax)
cbar.set_label("Number of Tariffs", rotation=90, labelpad=0)

# Subplot H: DAM Variation
# locate the data folders
lmp_path = os.path.join(basepath, "data", "DAMs")

fnames_lmp = [f for f in glob.glob(os.path.join(lmp_path, "*.csv"))]

df_breakdown = pd.DataFrame(
    columns=["region", "month", "maxval", "minval", "ratio", "mean"]
)

cmap = plt.get_cmap("twilight", 13)

regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]

# create a dict that assigns shapes for each region
shapes = ["s", "o", "D", "v", "P", "*", "X"]
shape_dict = dict(zip(regions, shapes))

# month modifier
month_mod = np.linspace(-4, 4, 12)

for i, r in enumerate(regions):
    # get the lmp for the region
    lmp_file = os.path.join(lmp_path, f"{r}costs.csv")

    if "OTHER" in lmp_file:
        # skip if the region is not in the filename
        pass
    else:
        df = pd.read_csv(lmp_file)
        # for each month
        for m in range(12):
            month = df[df["month"] == m + 1]
            price = month["USD_per_MWh"]
            ax[3, 1].scatter(
                10 * np.ones_like(price) * (i + 1) + month_mod[m],
                price,
                color=mpl.colors.rgb2hex(cmap(m)),
                marker="s",
                s=2.5,
                alpha=0.25,
            )

ax[3, 1].hlines(
    y=0, xmin=3, xmax=10 * (len(fnames_lmp) + 0.5) + 2, color="black", ls="--", lw=2
)

ax[3, 1].set(
    ylabel="DAM Price\n($/MWh)",
    xlim=(3, 10 * (len(fnames_lmp) + 0.5) + 2),
    xticks=10 * np.arange(1, len(fnames_lmp) + 1),
    xticklabels=regions,
    ylim=(-100, 1200),
    yticks=np.hstack([np.array([-100]), np.arange(0, 1301, 200)]),
)

## Subplot G: Time-averaged Tariff
tariff_path = "data/tariffs/timeseries"
regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]

# get directory of cwd
metadata_path = os.path.join(basepath, "data", "tariffs", "metadata.csv")
metadata = pd.read_csv(metadata_path)
tariff_gpd = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(metadata.longitude, metadata.latitude), data=metadata
)

combined_tariff_files = glob.glob(os.path.join(basepath, tariff_path, "combined/*.csv"))

months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# create a dictionary with regions as keys
region_dict = {region: {m: [] for m in months} for region in regions}

for f in tqdm(combined_tariff_files):
    tariff_id = f.split("_")[1].split(".")[0]
    costdata = pd.read_csv(f)

    # get the region from the tariff_gpd dataframe
    region = tariff_gpd[tariff_gpd["label"] == tariff_id]["ISO"].values[0]

    # place cost data into the dictionary
    if region not in region_dict:
        continue

    for m in months:
        # get the cost data for the month
        month_data = np.mean(costdata[costdata["Month"] == m]["Cost"].values)
        # add the cost data to the dictionary
        region_dict[region][m].append(month_data)

month_mod = np.linspace(-4, 4, 13)
for i, region in enumerate(regions):
    for m, data in region_dict[region].items():
        # check if the month data is empty
        if len(data) == 0:
            continue            
        # remove all nan values from the data
        month_data = [x for x in data if not np.isnan(x)]
        # month_data = np.concatenate(data).reshape(-1, 1)
        ax[3,0].scatter(
            10*np.ones_like(month_data) * (i+1) + month_mod[m], 
            month_data, 
            color=mpl.colors.rgb2hex(cmap(m)), 
            marker='s',
            s=2.5,
            alpha=0.25
        )

ax[3,0].set_xticks(np.arange(10, 10*(len(regions)+1), 10))
ax[3,0].set_xticklabels(regions)
ax[3,0].set(
    xlim=(5,None),  
    ylim=(-100, 1200),
    yticks=np.hstack([np.array([-100]), np.arange(0, 1301, 200)]),
    ylabel='Time-averaged Tariff Cost\n($/MWh)',
)

## Subplot F: DAM vs. Tariff
tariff_path = os.path.join(
    basepath,
    "data",
    "tariffs",
    "timeseries",
    "combined",
)
timeseries_fps = glob.glob(tariff_path + "/*.csv")

metadata_path = os.path.join(
    basepath,
    "data",
    "tariffs",
    "metadata.csv",
)
metadata = pd.read_csv(metadata_path)

enum_month = {
    "1": "Jan",
    "2": "Feb",
    "3": "Mar",
    "4": "Apr",
    "5": "May",
    "6": "Jun",
    "7": "Jul",
    "8": "Aug",
    "9": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}


def get_lmp_month(iso, month, basepath):
    lmp_path = os.path.join(basepath, "data", "DAMs")
    lmp_fp = os.path.join(lmp_path, iso, f"{iso}_DAM_2023_{month}_HOUR.csv")
    if not os.path.exists(lmp_fp):
        raise FileNotFoundError(
            f"LMP file for {iso} in {month} does not exist at {lmp_fp}"
        )
    lmp_df = pd.read_csv(lmp_fp)
    return lmp_df["LMP"].values


def get_tariff_month(tariff_path, month_num):
    tariff_ts = pd.read_csv(tariff_path)
    # subset the to the month of interest
    tariff_ts_month = tariff_ts[tariff_ts["Month"] == month_num]
    return tariff_ts_month["Cost"].values


peak_off_peak_sum = []
peak_off_peak_win = []
means_sum = []
means_win = []

for t in timeseries_fps:
    tmp = copy.copy(t)
    tariff_id = tmp.replace(".", "_").split("_")[-2]
    metadata_row = metadata[metadata["label"] == tariff_id]
    iso = metadata_row["ISO"].values[0]

    if iso is not np.nan:
        for m in range(1, 13):
            lmp = get_lmp_month(iso, enum_month[str(m)], basepath)
            tariff = get_tariff_month(t, m)

            if np.min(lmp) == 0 or np.min(tariff) == 0:
                lmp_peakoffpeak = np.nan
                tariff_peakoffpeak = np.nan
            else:
                lmp_peakoffpeak = np.max(lmp) / (np.min(lmp))
                tariff_peakoffpeak = np.max(tariff) / (np.min(tariff))

            lmp_mean = np.mean(lmp)
            tariff_mean = np.mean(tariff)
            if m < 5 or m > 10:  # Winter months
                peak_off_peak_win.append([lmp_peakoffpeak, tariff_peakoffpeak])
                means_win.append([lmp_mean, tariff_mean])
            else:  # Summer months
                peak_off_peak_sum.append([lmp_peakoffpeak, tariff_peakoffpeak])
                means_sum.append([lmp_mean, tariff_mean])

peak_off_peak_win = np.array(peak_off_peak_win)
peak_off_peak_sum = np.array(peak_off_peak_sum)
means_win = np.array(means_win)
means_sum = np.array(means_sum)

ax[2, 1].scatter(
    peak_off_peak_win[:, 0],
    peak_off_peak_win[:, 1],
    alpha=0.5,
    color="#479DA3",
    lw=1,
    edgecolors="k",
    label="Winter Months (Nov-Apr)",
)
ax[2, 1].scatter(
    peak_off_peak_sum[:, 0],
    peak_off_peak_sum[:, 1],
    alpha=0.5,
    color="#AB605B",
    lw=1,
    edgecolors="k",
    label="Summer Months (May-Oct)",
)
ax[2, 1].hlines(1, -2000, 1000, color="k", linestyle="--", linewidth=2)
ax[2, 1].vlines(0, 0.9, 1000, color="k", linestyle="--", linewidth=2)
ax[2, 1].set(
    xlabel="DAM Peak Price Premium\n(max/min)",
    ylabel="Tariff Peak Charge Premium\n(max/min)",
    yscale="log",
    xlim=(-1500, 400),
    xticks=np.arange(-1500, 501, 500),
    ylim=(0.9, 1000),
)

ax[2, 1].legend(loc="upper left", frameon=False)

## Save Output
labels = ["a.", "b.", "c.", "d.", "e.", "f.", "g.", "h."]

# from https://matplotlib.org/stable/gallery/text_labels_and_annotations/label_subplots.html
for label, axis in zip(labels, ax.flatten()):
    # Use ScaledTranslation to put the label
    # - at the top left corner (axes fraction (0, 1)),
    # - offset 20 pixels left and 7 pixels up (offset points (-20, +7)),
    # i.e. just outside the axes.
    axis.text(
        0.0,
        1.0,
        label,
        transform=(
            axis.transAxes + ScaledTranslation(-42 / 72, 0, fig.dpi_scale_trans)
        ),
        va="bottom",
        fontsize=10,
    )

fig.tight_layout()
fig.align_labels()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Figure3.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure3.png"), bbox_inches="tight", dpi=300)
