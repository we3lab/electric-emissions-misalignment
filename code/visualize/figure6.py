import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import pandas as pd
import numpy as np
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

regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]

colors = {'CAISO': '#66c2a5',
 'ERCOT': '#fc8d62',
 'ISONE': '#8da0cb',
 'MISO': '#a6d854',
 'NYISO': '#ffd92f',
 'PJM': '#e5c494',
 'SPP': '#b3b3b3'}

# Create a colormap
cmap = cm.get_cmap('Set2', len(regions))
# Create a dictionary to map regions to colors
# Normalize the colormap to the number of regions
norm = mcolors.Normalize(vmin=0, vmax=len(regions)-1)
# Create a dictionary to map regions to colors
region_color_map = {region: mcolors.to_hex(cmap(norm(i))) for i, region in enumerate(regions)}

corr_datapath = os.path.join("data", "correlation", "corr_coef_tariff_ratio.csv")
corr_data = pd.read_csv(corr_datapath)

# check the number of na values in the dataframe
print("Number of NaN values in the dataframe:", corr_data.isna().sum().sum())

dr_datapath = os.path.join("data", "dr", "on_off_peak_prices.csv")
dr_data = pd.read_csv(dr_datapath, encoding="latin1")

#################
# Create Subplots
#################

# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(3, 1, figsize=(90 / 25.4, 180 / 25.4))

###########
# Subplot A
###########

ax[0].hlines(0, 0, 1000, color='black', lw=2.5, ls='--')

for region in regions:
    ax[0].scatter(
        corr_data["tariff_ratio"][
            (corr_data["region"] == region)
            & ~(pd.isna(corr_data["pearson_cc"]))
            & ~(pd.isna(corr_data["tariff_ratio"]))
        ], 
        corr_data["pearson_cc"][
            (corr_data["region"] == region)
            & ~(pd.isna(corr_data["pearson_cc"]))
            & ~(pd.isna(corr_data["tariff_ratio"]))
        ], 
        color=region_color_map[region],
        label=region,
        alpha=0.5,
        s=5
    )

ax[0].set(
    ylabel="Correlation of\nTariff and AEF",
    xlabel="Peak-to-Off-Peak\nTariff Ratio",
    xlim=(1, 1025),
    ylim=(-1, 1),
    xscale="log"
)

ax[1].set(
    xlabel="Demand Response Price ($/kW)",
    ylabel="Correlation of\nTariff and AEF",
    ylim=(-1, 1),
    xlim=(0, 250),
)

###########
# Subplot B
###########

ax[1].hlines(0, xmin=0, xmax=250, color="black", lw=2, ls="--")

for region in regions:

    # filter data for the current region
    region_corr = corr_data[corr_data["region"] == region]
    # filter winter and summer correlation data
    winter_region_corr = region_corr[corr_data["month"]<5]
    winter_region_corr = region_corr[corr_data["month"]>=11]["pearson_cc"].dropna()
    summer_region_corr = region_corr[corr_data["month"]>=5]
    summer_region_corr = summer_region_corr[summer_region_corr["month"] < 11]["pearson_cc"].dropna()

    region_dr_data_df = dr_data[dr_data["iso/rto"] == region]
    winter_region_dr = region_dr_data_df["w_price"].dropna()
    summer_region_dr = region_dr_data_df["s_price"].dropna()

    pts = []
    for w_dr in winter_region_dr:
        for wc in winter_region_corr:
            pts.append([w_dr, wc])

    for s_dr in summer_region_dr:
        for sc in summer_region_corr:
            pts.append([s_dr, sc])

    pts = np.array(pts)

    anchor_point = (np.min(pts[:, 0]), np.min(pts[:, 1]))
    width = np.max(pts[:, 0]) - np.min(pts[:, 0])
    height = np.max(pts[:, 1]) - np.min(pts[:, 1])

    # draw a patch with points at the min and max 
    rect = mpl.patches.Rectangle(
        anchor_point, width, height, linewidth=1.5, edgecolor=colors[region], facecolor='none', alpha = 1, label=region
    )
    ax[1].add_patch(rect)

###########
# Subplot C
###########

for region in regions:
    # filter data for the current region
    region_corr = corr_data[corr_data["region"] == region]

    # filter winter and summer correlation data
    winter_region_corr = region_corr[corr_data["month"]<5]
    winter_region_corr = region_corr[corr_data["month"]>=11]["tariff_ratio"].dropna()
    summer_region_corr = region_corr[corr_data["month"]>=5]
    summer_region_corr = summer_region_corr[summer_region_corr["month"] < 11]["tariff_ratio"].dropna()

    # filter demand response data for the current region
    region_dr_data_df = dr_data[dr_data["iso/rto"] == region]
    winter_region_dr = region_dr_data_df["w_price"].dropna()
    summer_region_dr = region_dr_data_df["s_price"].dropna()

    pts = []
    for w_dr in winter_region_dr:
        for wc in winter_region_corr:
            pts.append([w_dr, wc])

    for s_dr in summer_region_dr:
        for sc in summer_region_corr:
            pts.append([s_dr, sc])

    pts = np.array(pts)

    anchor_point = (np.min(pts[:, 0]), np.min(pts[:, 1]))
    width = np.max(pts[:, 0]) - np.min(pts[:, 0])
    height = np.max(pts[:, 1]) - np.min(pts[:, 1])

    print(f"Region: {region}, Anchor Point: {anchor_point}, Width: {width}, Height: {height}")

    # create a rectangle patch
    rect = mpl.patches.Rectangle(anchor_point, width, height, linewidth=1.5, edgecolor=colors[region], facecolor='none', label=region)
    # add the patch to the Axes
    ax[2].add_patch(rect)

ax[2].set(
    xlabel="Demand Response Price ($/kW)",
    ylabel="Peak-to-Off-Peak\nTariff Ratio",
    ylim=(0, 1100),
    xlim=(0, 250),
    yscale="log",
)

# TODO: for some reason this block had to be run twice to have changes reflected in the plot...
for region in regions:
    # filter data for the current region
    region_corr = corr_data[corr_data["region"] == region]

    # filter winter and summer correlation data
    winter_region_corr = region_corr[corr_data["month"]<5]
    winter_region_corr = region_corr[corr_data["month"]>=11]["tariff_ratio"].dropna()
    summer_region_corr = region_corr[corr_data["month"]>=5]
    summer_region_corr = summer_region_corr[summer_region_corr["month"] < 11]["tariff_ratio"].dropna()

    # filter demand response data for the current region
    region_dr_data_df = dr_data[dr_data["iso/rto"] == region]
    winter_region_dr = region_dr_data_df["w_price"].dropna()
    summer_region_dr = region_dr_data_df["s_price"].dropna()

    pts = []
    for w_dr in winter_region_dr:
        for wc in winter_region_corr:
            pts.append([w_dr, wc])

    for s_dr in summer_region_dr:
        for sc in summer_region_corr:
            pts.append([s_dr, sc])

    pts = np.array(pts)

    anchor_point = (np.min(pts[:, 0]), np.min(pts[:, 1]))
    width = np.max(pts[:, 0]) - np.min(pts[:, 0])
    height = np.max(pts[:, 1]) - np.min(pts[:, 1])

    print(f"Region: {region}, Anchor Point: {anchor_point}, Width: {width}, Height: {height}")

    # create a rectangle patch
    rect = mpl.patches.Rectangle(anchor_point, width, height, linewidth=1.5, edgecolor=colors[region], facecolor='none', label=region)
    # add the patch to the Axes
    ax[2].add_patch(rect)

ax[2].set(
    xlabel="Demand Response Price ($/kW)",
    ylabel="Peak-to-Off-Peak\nTariff Ratio",
    ylim=(0, 1100),
    xlim=(0, 250),
    yscale="log",
)

#############
# Save Output
#############
fig.tight_layout()
ax[1].legend(loc="upper left", bbox_to_anchor=(0.0, 2.6), frameon=False, ncol=4, columnspacing=0.25)
fig.align_labels()

from matplotlib.transforms import ScaledTranslation

labels = ["a.", "b.", "c."]

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
        transform=(axis.transAxes + ScaledTranslation(-50/72, 0, fig.dpi_scale_trans)),
        va='bottom',
        fontsize=10
    )
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Figure7.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure7.png"), bbox_inches="tight", dpi=300)