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

combined_data = {"iso": [], "corr_coef": [], "month": [], "price_type": []}

for region in regions:
    aef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_aef_pearson.csv"))
    mef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_mef_pearson.csv"))
    for month in range(1, 13):
        # AEF/tariff correlation
        for index, row in aef_corr_df.iterrows():
            if (math.isclose(row[months[month - 1]], 0, abs_tol=1e-8) or pd.isna(row[months[month - 1]])):
                pass  # zero correlation due to flat tariff
            else:
                combined_data["iso"].append(region)
                combined_data["month"].append(month)
                combined_data["corr_coef"].append(row[months[month - 1]])
                combined_data["price_type"].append("Tariff/AEF")
        # MEF/DAM correlation
        for index, row in mef_corr_df[mef_corr_df["month"] == month].iterrows():
            combined_data["iso"].append(region)
            combined_data["month"].append(month)
            combined_data["corr_coef"].append(row["pearson_cc"])
            combined_data["price_type"].append("DAM/MEF")

## Create Subplots
# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(1, 1, figsize=(80 / 25.4, 60 / 25.4))

## Subplot A
df = pd.DataFrame(combined_data)
colors = ["#FFE599", "#FAB477"]
bright_colors = ["#FFDF84", "#FF8C5D"]
sns.set_palette(bright_colors)

ax.axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df,
    x="iso",
    y="corr_coef",
    hue="price_type",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax,
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax.set_xlabel("")
ax.set_ylim(-1, 1)
ax.set_ylabel("Pearson Correlation Coefficient")
# plt.title("AEF vs. Tariffs")
ax.legend(loc="lower right", frameon=False)

fig.tight_layout()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Figure5.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure5.png"), bbox_inches="tight", dpi=300)
