import os
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo
tariff_path = os.path.join(basepath, "data", "tariffs", "bundled")

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

def is_seasonal(df, charge_type="energy"):
  idx = (df.utility == "electric") & (df.type == charge_type) & (df["basic_charge_limit (imperial)"] == 0)
  return (len(df.month_start[idx].unique()) != 1)

def is_tou(df, charge_type="energy"):
  idx = (df.utility == "electric") & (df.type == charge_type) & (df["basic_charge_limit (imperial)"] == 0)
  return (len(df.hour_start[idx].unique()) != 1)

meta_df = pd.read_csv(os.path.join(tariff_path, "metadata.csv"))

for charge_type in ["energy", "demand"]:
  rate_types = []
  for tariff_id in meta_df["label"]:
    try:
      bill_df = pd.read_csv(os.path.join(tariff_path, "processed_sheets", tariff_id + ".csv"))
      if is_seasonal(bill_df, charge_type=charge_type):
        if is_tou(bill_df, charge_type=charge_type):
          rate_types.append("Seasonal-TOU")
        else:
          rate_types.append("Seasonal-NonTOU")
      elif is_tou(bill_df, charge_type=charge_type):
        rate_types.append("Nonseasonal-TOU")
      else:
        rate_types.append("Flat")
    except FileNotFoundError:
      rate_types.append("")

  if charge_type == "energy":
    meta_df["Energy_Rate_Type"] = rate_types
  else:
    meta_df["Demand_Rate_Type"] = rate_types

combined_rate_types = []
for index, row in meta_df.iterrows():
    if (
        (row["Energy_Rate_Type"] == "Flat" and row["Demand_Rate_Type"] == "Flat")
        or (row["Energy_Rate_Type"] == "Flat" and row["Demand_Rate_Type"] == "")
        or (row["Energy_Rate_Type"] == "" and row["Demand_Rate_Type"] == "Flat")
    ):
        combined_rate_types.append("Flat")
    elif (
        row["Energy_Rate_Type"] == "Seasonal-TOU"
        or row["Demand_Rate_Type"] == "Seasonal-TOU"
        or (row["Energy_Rate_Type"] == "Seasonal-NonTOU") and (row["Demand_Rate_Type"] == "Nonseasonal-TOU")
        or (row["Energy_Rate_Type"] == "Nonseasonal-TOU") and (row["Demand_Rate_Type"] == "Seasonal-NonTOU")
    ):
        combined_rate_types.append("Seasonal-TOU")
    elif (
        (row["Energy_Rate_Type"] == "Seasonal-NonTOU" and row["Demand_Rate_Type"] == "Seasonal-NonTOU")
        or (row["Energy_Rate_Type"] == "Seasonal-NonTOU" and row["Demand_Rate_Type"] == "")
        or (row["Energy_Rate_Type"] == "Seasonal-NonTOU" and row["Demand_Rate_Type"] == "Flat")
        or (row["Energy_Rate_Type"] == "" and row["Demand_Rate_Type"] == "Seasonal-NonTOU")
        or (row["Energy_Rate_Type"] == "Flat" and row["Demand_Rate_Type"] == "Seasonal-NonTOU")
    ):
        combined_rate_types.append("Seasonal-NonTOU")
    elif (
        (row["Energy_Rate_Type"] == "Nonseasonal-TOU" and row["Demand_Rate_Type"] == "Nonseasonal-TOU")
        or (row["Energy_Rate_Type"] == "Nonseasonal-TOU" and row["Demand_Rate_Type"] == "")
        or (row["Energy_Rate_Type"] == "" and row["Demand_Rate_Type"] == "Nonseasonal-TOU")
        or (row["Energy_Rate_Type"] == "Nonseasonal-TOU" and row["Demand_Rate_Type"] == "Flat")
        or (row["Energy_Rate_Type"] == "Flat" and row["Demand_Rate_Type"] == "Nonseasonal-TOU")
    ):
        combined_rate_types.append("Nonseasonal-TOU")
    else:
        combined_rate_types.append("")

meta_df["Combined_Rate_Type"] = combined_rate_types

# drop rates with FileNotFoundError
meta_df = meta_df[~(meta_df["Combined_Rate_Type"] == "")]

##################
# Print Statistics
##################

print(meta_df["Combined_Rate_Type"].value_counts())
print(f"Flat tariffs are {100 * 424 / (1502 - 48)}%")
print(f"Seasonal-TOU tariffs are {100 * 733 / (1502 - 48)}%")
print(f"Seasonal-NonTOU tariffs are {100 * 163 / (1502 - 48)}%")
print(f"Nonseasonal-TOU tariffs are {100 * 134 / (1502 - 48)}%")

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
meta_df["Energy_Rate_Type"].value_counts().sort_index().plot(kind='bar', ax=ax[0])
ax[0].set_xticklabels([])
ax[0].set_xlabel("")
ax[0].set_ylabel("Count")
ax[0].set_ylim((0, 800))

###########
# Subplot B
###########
meta_df["Demand_Rate_Type"].value_counts().sort_index().plot(kind='bar', ax=ax[1])
ax[1].set_xticklabels([])
ax[1].set_xlabel("")
ax[1].set_ylabel("Count")
ax[1].set_ylim((0, 800))

###########
# Subplot C
###########
meta_df["Combined_Rate_Type"].value_counts().sort_index().plot(kind='bar', ax=ax[2])
ax[2].set_xlabel("")
ax[2].set_ylabel("Count")
ax[2].set_ylim((0, 800))

#############
# Save Output
#############
fig.tight_layout()
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
        transform=(
            axis.transAxes + ScaledTranslation(-50 / 72, 0, fig.dpi_scale_trans)
        ),
        va="bottom",
        fontsize=10,
    )
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Supplementary1.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Supplementary1.png"), bbox_inches="tight", dpi=300)
