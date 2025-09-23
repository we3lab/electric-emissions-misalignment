from matplotlib.transforms import ScaledTranslation
import matplotlib.pyplot as plt
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
mef_path = os.path.join("data/MEFs")
aef_path = os.path.join("data/AEFs")

OVERLAY_POINTS = True

# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(2, 1, figsize=(90 / 25.4, 120 / 25.4))


## Subplot A
cmap = plt.get_cmap("twilight", 13)

# create a dict that assigns shapes for each region
shapes = ["s", "o", "D", "v", "P", "*", "X"]
shape_dict = dict(zip(regions, shapes))

# month modifier
month_mod = np.linspace(-4, 4, 12)

f_mef = os.path.join(mef_path, "average_mefs.csv")

for i, r in enumerate(regions):
    f_aef = os.path.join(aef_path, f"{r}aef.csv")
    df_aef = pd.read_csv(f_aef)

    if OVERLAY_POINTS:
        df_mef = pd.read_csv(f_mef)

        x_pts = []
        max_pts = []
        min_pts = []

        for m in range(12):
            month_mef = df_mef[(df_mef["month"] == m + 1) & (df_mef["isorto"] == r)]
            co2i_mef = month_mef["co2_eq_kg_per_MWh"]
            x_pt_l = 10 * (i + 1) + month_mod[m] - 0.5
            x_pt_r = 10 * (i + 1) + month_mod[m] + 0.5
            max_pt = np.max(co2i_mef)
            min_pt = np.min(co2i_mef)

            x_pts.append(x_pt_l)
            max_pts.append(max_pt)
            min_pts.append(min_pt)

            x_pts.append(x_pt_r)
            max_pts.append(max_pt)
            min_pts.append(min_pt)

        top = np.array(max_pts)
        bottom = np.array(min_pts)
        xs = np.array(x_pts)

        overlay_params = {
            "color": "k",
            "lw": 0.5,
            "where": "mid",
            "linestyle": "-",
            "alpha": 0.3,
        }

        ax[0].step(
            xs,
            top,
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            where=overlay_params["where"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )
        ax[0].step(
            xs,
            bottom,
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            where=overlay_params["where"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )
        # connect the top and bottom on the left and right
        ax[0].vlines(
            xs[0],
            bottom[0],
            top[0],
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )
        ax[0].vlines(
            xs[-1],
            bottom[-1],
            top[-1],
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )

    # for each month
    for m in range(12):
        month_aef = df_aef[df_aef["month"] == m + 1]
        co2i_aef = month_aef["co2_eq_kg_per_MWh"]
        ax[0].scatter(
            10 * np.ones_like(co2i_aef) * (i + 1) + month_mod[m],
            co2i_aef,
            color=mpl.colors.rgb2hex(cmap(m)),
            # edgecolor='black',
            marker="s",
            s=4,
            alpha=1,
        )

    ax[0].set(
        ylabel="Carbon Intensity (kg CO$_2$-eq/MWh)",
        xticks=10 * np.arange(1, len(regions) + 1),
        xticklabels=regions,
        ylim=(0, 800),
        yticks=np.arange(0, 900, 100),
    )

## Subplot B
cmap = plt.get_cmap("twilight", 13)

# create a dict that assigns shapes for each region
shapes = ["s", "o", "D", "v", "P", "*", "X"]
shape_dict = dict(zip(regions, shapes))

# month modifier
month_mod = np.linspace(-4, 4, 12)
f_mef = os.path.join(mef_path, "average_mefs.csv")

for i, r in enumerate(regions):
    f_aef = os.path.join(aef_path, f"{r}aef.csv")
    df_mef = pd.read_csv(f_mef)

    if OVERLAY_POINTS:
        df_aef = pd.read_csv(f_aef)

        x_pts = []
        max_pts = []
        min_pts = []
        for m in range(12):
            month_aef = df_aef[df_aef["month"] == m + 1]
            co2i_aef = month_aef["co2_eq_kg_per_MWh"]
            x_pt_l = 10 * (i + 1) + month_mod[m] - 0.5
            x_pt_r = 10 * (i + 1) + month_mod[m] + 0.5
            max_pt = np.max(co2i_aef)
            min_pt = np.min(co2i_aef)

            x_pts.append(x_pt_l)
            max_pts.append(max_pt)
            min_pts.append(min_pt)

            x_pts.append(x_pt_r)
            max_pts.append(max_pt)
            min_pts.append(min_pt)

        top = np.array(max_pts)
        bottom = np.array(min_pts)
        xs = np.array(x_pts)

        overlay_params = {
            "color": "k",
            "lw": 0.5,
            "where": "mid",
            "linestyle": "-",
            "alpha": 0.3,
        }

        ax[1].step(
            xs,
            top,
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            where=overlay_params["where"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )
        ax[1].step(
            xs,
            bottom,
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            where=overlay_params["where"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )
        # connect the top and bottom on the left and right
        ax[1].vlines(
            xs[0],
            bottom[0],
            top[0],
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )
        ax[1].vlines(
            xs[-1],
            bottom[-1],
            top[-1],
            lw=overlay_params["lw"],
            color=overlay_params["color"],
            ls=overlay_params["linestyle"],
            alpha=overlay_params["alpha"],
        )

    for m in range(12):
        month = df_mef[(df_mef["month"] == m + 1) & (df_mef["isorto"] == r)]
        co2i = month["co2_eq_kg_per_MWh"]
        ax[1].scatter(
            10 * np.ones_like(co2i) * (i + 1) + month_mod[m],
            co2i,
            color=mpl.colors.rgb2hex(cmap(m)),
            # edgecolor='black',
            marker="s",
            s=4,
            alpha=1,
        )

    ax[1].set(
        ylabel="Carbon Intensity (kg CO$_2$-eq/MWh)",
        xticks=10 * np.arange(1, len(regions) + 1),
        xticklabels=regions,
        ylim=(0, 800),
        yticks=np.arange(0, 900, 100),
    )

## Save Output
labels = ["a.", "b."]

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
fig.savefig(os.path.join(fig_path, "Figure2.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure2.png"), bbox_inches="tight", dpi=300)
