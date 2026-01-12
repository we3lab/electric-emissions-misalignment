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

# locate the data folders
corr_dir = os.path.join(basepath, "data/correlation")

sector_color_map = {
    "Flat": "#66c2a5",
    "Manufact\n-uring": "#fc8d62",
    "Trades\n(non-food)": "#8da0cb",
    "Office": "#a6d854",
    "Water &\ntelecom": "#ffd92f",
    "Crops &\ntransport": "#e5c494",
}

sectors = ["Flat", "Manufact\n-uring", "Trades\n(non-food)", "Office", "Water &\ntelecom", "Crops &\ntransport"]
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

combined_data = {"iso": [], "corr_coef": [], "month": [], "sector": []}

for region in regions:
    for sector in sectors:
        if sector == "Flat":
            aef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_aef_pearson.csv"))
        elif sector == "Manufact\n-uring":
            aef_corr_df = pd.read_csv(os.path.join(corr_dir, "supplementary", region + "_aef_pearson (1).csv"))
        elif sector == "Trades\n(non-food)":
            aef_corr_df = pd.read_csv(os.path.join(corr_dir,  "supplementary", region + "_aef_pearson (2).csv"))
        elif sector == "Office":
            aef_corr_df = pd.read_csv(os.path.join(corr_dir, "supplementary", region + "_aef_pearson (5).csv"))
        elif sector == "Crops &\ntransport":
            aef_corr_df = pd.read_csv(os.path.join(corr_dir, "supplementary", region + "_aef_pearson (6).csv"))
        elif sector == "Water &\ntelecom":
            aef_corr_df = pd.read_csv(os.path.join(corr_dir, "supplementary", region + "_aef_pearson (8).csv"))
        else:
            raise ValueError(f"Sector {sector} not in sectors: {sectors}")
        
        for month in range(1, 13):
            # AEF/tariff correlation
            for index, row in aef_corr_df.iterrows():
                if (math.isclose(row[months[month - 1]], 0, abs_tol=1e-8) or pd.isna(row[months[month - 1]])):
                    pass  # zero correlation due to flat tariff
                else:
                    combined_data["iso"].append(region)
                    combined_data["month"].append(month)
                    combined_data["corr_coef"].append(row[months[month - 1]])
                    combined_data["sector"].append(sector)

df = pd.DataFrame(combined_data)

## Create Subplots
# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(4, 2, figsize=(190 / 25.4, 240 / 25.4))

## Subplot A: CAISO
sns.set_palette(sector_color_map.values())
ax[0,0].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "CAISO"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[0,0],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[0,0].set_xlabel("")
ax[0,0].set_ylim(-1, 1)
ax[0,0].set_ylabel("Pearson\nCorrelation Coefficient")
ax[0,0].legend(loc="lower right", frameon=False)

## Subplot B: ERCOT
ax[0,1].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "ERCOT"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[0,1],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[0,1].set_xlabel("")
ax[0,1].set_ylim(-1, 1)
ax[0,1].set_ylabel("Pearson\nCorrelation Coefficient")
ax[0,1].legend(loc="lower right", frameon=False)

## Subplot C: ISONE
ax[1,0].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "ISONE"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[1,0],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[1,0].set_xlabel("")
ax[1,0].set_ylim(-1, 1)
ax[1,0].set_ylabel("Pearson\nCorrelation Coefficient")
ax[1,0].legend(loc="lower right", frameon=False)

## Subplot D: MISO
ax[1,1].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "MISO"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[1,1],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[1,1].set_xlabel("")
ax[1,1].set_ylim(-1, 1)
ax[1,1].set_ylabel("Pearson\nCorrelation Coefficient")
ax[1,1].legend(loc="lower right", frameon=False)

## Subplot E: NYISO
ax[2,0].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "NYISO"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[2,0],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[2,0].set_xlabel("")
ax[2,0].set_ylim(-1, 1)
ax[2,0].set_ylabel("Pearson\nCorrelation Coefficient")
ax[2,0].legend(loc="lower right", frameon=False)

## Subplot F: PJM
ax[2,1].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "PJM"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[2,1],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[2,1].set_xlabel("")
ax[2,1].set_ylim(-1, 1)
ax[2,1].set_ylabel("Pearson\nCorrelation Coefficient")
ax[2,1].legend(loc="lower right", frameon=False)

## Subplot G: SPP
ax[3,0].axhline(0, linestyle="dotted", color="grey")
plot_a = sns.violinplot(
    data=df[df["iso"] == "SPP"],
    x="sector",
    y="corr_coef",
    hue="sector",
    linewidth=0.0,
    width=0.75,
    density_norm="width",
    ax=ax[3,0],
    inner="box",
    inner_kws={"box_width": 2.0, "marker": '.', "markersize": 3},
)
ax[3,0].set_xlabel("")
ax[3,0].set_ylim(-1, 1)
ax[3,0].set_ylabel("Pearson\nCorrelation Coefficient")
ax[3,0].legend(loc="lower right", frameon=False)

# Remove the frame from the unused subplot
ax[3,1].set_frame_on(False)
ax[3,1].tick_params(axis='x', which='both', length=0)
ax[3,1].tick_params(axis='x', labelbottom=False)
ax[3,1].tick_params(axis='y', which='both', length=0)
ax[3,1].tick_params(axis='y', labelleft=False)

## Save Outputs
labels = ["a.", "b.", "c.", "d.", "e.", "f.", "g."]

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
            axis.transAxes + ScaledTranslation(-36 / 72, 0, fig.dpi_scale_trans)
        ),
        va="bottom",
        fontsize=10,
    )

fig.tight_layout()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Supplementary7.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Supplementary7.png"), bbox_inches="tight", dpi=300)