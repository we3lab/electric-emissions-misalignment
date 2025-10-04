from matplotlib.transforms import ScaledTranslation
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import pandas as pd
import math
import os

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo

# define plotting defaults
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 7,
        "axes.linewidth": 1,
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

regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]

# locate the data folders
corr_dir = os.path.join(basepath, "data/correlation")

month_season_map = {
    1: "Winter",
    2: "Winter",
    3: "Winter",
    4: "Winter",
    5: "Summer",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Summer",
    10: "Summer",
    11: "Winter",
    12: "Winter",
}

region_color_map = {
    "CAISO": "#66c2a5",
    "ERCOT": "#fc8d62",
    "ISONE": "#8da0cb",
    "MISO": "#a6d854",
    "NYISO": "#ffd92f",
    "PJM": "#e5c494",
    "SPP": "#b3b3b3",
}

shapes = ["s", "o", "D", "v", "P", "*", "X"]
regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]
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
region_shape_dict = dict(zip(regions, shapes))

new_aef_tariff_data = {"iso": [], "corr_coef": [], "month": [], "season": []}
new_mef_dam_data = {"iso": [], "corr_coef": [], "month": [], "season": []}

for region in regions:
    aef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_aef_pearson.csv"))
    mef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_mef_pearson.csv"))
    for month in range(1, 13):
        season = month_season_map[month]
        # AEF/tariff correlation
        for index, row in aef_corr_df.iterrows():
            if (math.isclose(row[months[month - 1]], 0, abs_tol=1e-8) or pd.isna(row[months[month - 1]])):
                pass  # zero correlation due to flat tariff
            else:
                new_aef_tariff_data["iso"].append(region)
                new_aef_tariff_data["season"].append(season)
                new_aef_tariff_data["month"].append(month)
                new_aef_tariff_data["corr_coef"].append(row[months[month - 1]])
        # MEF/DAM correlation
        for index, row in mef_corr_df[mef_corr_df["month"] == month].iterrows():
            new_mef_dam_data["iso"].append(region)
            new_mef_dam_data["season"].append(season)
            new_mef_dam_data["month"].append(month)
            new_mef_dam_data["corr_coef"].append(row["pearson_cc"])

## Create Subplots
# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(2, 2, figsize=(190 / 25.4, 120 / 25.4))

## Subplot A
df = pd.DataFrame(new_aef_tariff_data)
seasonal_colors = ["#5E9BA1", "#A1645E"]
bright_seasonal_colors = ["#71bac1", "#c17871"]
sns.set_palette(bright_seasonal_colors)
plot_a = sns.violinplot(
    data=df,
    x="iso",
    y="corr_coef",
    hue="season",
    linewidth=0.0,
    width=1.0,
    ax=ax[0, 0],
    inner="box",
    inner_kws={"box_width": 2.0},
)
ax[0, 0].set_xlabel("")
ax[0, 0].set_ylim(-1, 1)
ax[0, 0].set_ylabel("Pearson Correlation Coefficient")
# plt.title("AEF vs. Tariffs")
ax[0, 0].legend(loc="lower right", frameon=False)
# plt.gca().get_legend().remove()
ax[0, 0].axhline(0, linestyle="dotted", color="grey")

## Subplot B
df = pd.DataFrame(new_aef_tariff_data)
data_dict = {}
for iso in regions:
    iso_dict = {}
    for month in range(12, 0, -1):
        iso_dict[month] = df[(df["iso"] == iso) & (df["month"] == month)][
            "corr_coef"
        ].mean()
    data_dict[iso] = iso_dict
sns.heatmap(
    pd.DataFrame(data_dict),
    cbar_kws={"label": "Pearson Correlation Coefficient"},
    vmin=-0.5,
    vmax=0.5,
    cmap="PRGn",
    ax=ax[0, 1],
)
ax[0, 1].set_xlabel("")
ax[0, 1].set_ylabel("Month")
# ax.set_title("AEF vs. Tariff")
ax[0, 1].set_xticklabels(ax[0, 1].get_xticklabels(), rotation=0)

## Subplot C
df = pd.DataFrame(new_mef_dam_data)
seasonal_colors = ["#5E9BA1", "#A1645E"]
bright_seasonal_colors = ["#71bac1", "#c17871"]
sns.set_palette(bright_seasonal_colors)
plot_c = sns.violinplot(
    data=df,
    x="iso",
    y="corr_coef",
    hue="season",
    linewidth=0.0,
    width=1.0,
    ax=ax[1, 0],
    inner="box",
    inner_kws={"box_width": 2.0},
)
ax[1, 0].set_xlabel("")
ax[1, 0].set_ylim(-1, 1)
ax[1, 0].set_ylabel("Pearson Correlation Coefficient")
# plt.title("MEF vs. DAM Prices")
ax[1, 0].legend(loc="lower right", frameon=False)
ax[1, 0].axhline(0, linestyle="dotted", color="grey")

## Subplot D
df = pd.DataFrame(new_mef_dam_data)
data_dict = {}
for iso in regions:
    iso_dict = {}
    for month in range(12, 0, -1):
        iso_dict[month] = df[(df["iso"] == iso) & (df["month"] == month)][
            "corr_coef"
        ].mean()
    data_dict[iso] = iso_dict
sns.heatmap(
    pd.DataFrame(data_dict),
    cbar_kws={"label": "Pearson Correlation Coefficient"},
    vmin=-0.5,
    vmax=0.5,
    cmap="PRGn",
    ax=ax[1, 1],
)
ax[1, 1].set_xlabel("")
ax[1, 1].set_ylabel("Month")
# ax.set_title("MEF vs. DAM")
ax[1, 1].set_xticklabels(ax[1, 1].get_xticklabels(), rotation=0)

## Save Outputs
labels = ["a.", "b.", "c.", "d."]

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
            axis.transAxes + ScaledTranslation(-32 / 72, 0, fig.dpi_scale_trans)
        ),
        va="bottom",
        fontsize=10,
    )

fig.tight_layout()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Figure5.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure5.png"), bbox_inches="tight", dpi=300)
