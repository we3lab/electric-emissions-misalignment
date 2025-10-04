from matplotlib.transforms import ScaledTranslation
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry.point import Point
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely import box
import pandas as pd
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

vmin = -0.25
vmax = 0.25

# locate the data folders
corr_dir = os.path.join(basepath, "data", "correlation")

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

# SF map coordinates
x_min = -122.80
x_max = -121.80
y_min = 37.4
y_max = 38.2

ca_corr_df = pd.read_csv(os.path.join(corr_dir, "caiso_mef_pearson.csv"))
sf_node_df = pd.read_csv(
    os.path.join(basepath, "data", "geospatial", "iso", "SFLMPLocations.csv")
)
iso = gpd.read_file(
    os.path.join(
        basepath, "data", "geospatial", "iso", "Independent_System_Operators.shp"
    )
).astype({"ID": "int64"})
caiso = iso[iso["NAME"] == "CALIFORNIA INDEPENDENT SYSTEM OPERATOR"]
# convert CRS to one using meters for scale bar
# caiso = caiso.to_crs(32619)

missing_count = 0
found_count = 0
latitude = []
longitude = []
for index, row in ca_corr_df.iterrows():
    node_data = sf_node_df[sf_node_df["name"] == row["location"]]
    if not node_data.empty:
        found_count += 1
        latitude.append(node_data["latitude"].values[0])
        longitude.append(node_data["longitude"].values[0])
    else:
        missing_count += 1
        latitude.append(0)
        longitude.append(0)

ca_corr_df["latitude"] = latitude
ca_corr_df["longitude"] = longitude
print("missing_count:", int(missing_count / 12))
print("found_count:", int(found_count / 12))

jan_df = ca_corr_df[ca_corr_df["month"] == 1]
apr_df = ca_corr_df[ca_corr_df["month"] == 4]
jul_df = ca_corr_df[ca_corr_df["month"] == 7]
oct_df = ca_corr_df[ca_corr_df["month"] == 10]

## Create Subplots
# create all plots on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(2, 1, figsize=(90 / 25.4, 150 / 25.4))

# https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html
points = gpd.GeoSeries(
    [Point(-121.90, 37.5), Point(-122.80, 37.5)], crs=caiso.crs
)  # Geographic WGS 84 - degrees
points = points.to_crs(32619)  # Projected WGS 84 - meters
distance_meters = points[0].distance(points[1])

## Subplot A
caiso.plot(ax=ax[0], color="white", edgecolor="k")
corr_gdf_a = gpd.GeoDataFrame(
    jan_df,
    geometry=gpd.points_from_xy(jan_df.longitude, jan_df.latitude),
    crs=caiso.crs,
)
plot_a = corr_gdf_a.plot(
    ax=ax[0],
    column="pearson_cc",
    edgecolor="black",
    cmap=plt.cm.PiYG,
    vmin=vmin,
    vmax=vmax,
)
# from https://gis.stackexchange.com/questions/471203/setting-the-background-color-when-plotting-in-geopandas
background = gpd.GeoDataFrame(geometry=[box(x_min, y_min, x_max, y_max)], crs=caiso.crs)
background.plot(ax=ax[0], color="cornflowerblue", zorder=0)
ax[0].set_xlim(x_min, x_max)
ax[0].set_xlabel("Longitude ($^\circ$)")
ax[0].set_ylim(y_min, y_max)
ax[0].set_ylabel("Latitude ($^\circ$)")

# add scalebar from https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html
ax[0].set_aspect(1)
ax[0].add_artist(ScaleBar(distance_meters))

## Subplot B
caiso.plot(ax=ax[1], color="white", edgecolor="k")
corr_gdf_b = gpd.GeoDataFrame(
    jul_df,
    geometry=gpd.points_from_xy(jul_df.longitude, jul_df.latitude),
    crs=caiso.crs,
)
plot_b = corr_gdf_b.plot(
    ax=ax[1],
    column="pearson_cc",
    edgecolor="black",
    cmap=plt.cm.PiYG,
    vmin=vmin,
    vmax=0,
)
# from https://gis.stackexchange.com/questions/471203/setting-the-background-color-when-plotting-in-geopandas
background = gpd.GeoDataFrame(geometry=[box(x_min, y_min, x_max, y_max)], crs=caiso.crs)
background.plot(ax=ax[1], color="cornflowerblue", zorder=0)
ax[1].set_xlim(x_min, x_max)
ax[1].set_xlabel("Longitude ($^\circ$)")
ax[1].set_ylim(y_min, y_max)
ax[1].set_ylabel("Latitude ($^\circ$)")

# add scalebar from https://geopandas.org/en/stable/gallery/matplotlib_scalebar.html
ax[1].set_aspect(1)
ax[1].add_artist(ScaleBar(distance_meters))

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
            axis.transAxes + ScaledTranslation(-36 / 72, 0, fig.dpi_scale_trans)
        ),
        va="bottom",
        fontsize=10,
    )

fig.tight_layout()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Supplementary1.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Supplementary1.png"), bbox_inches="tight", dpi=300)

## Add Colorbar
sm = plt.cm.ScalarMappable(cmap=plt.cm.PiYG, norm=plt.Normalize(vmin=vmin, vmax=vmax))
cbar = fig.colorbar(
    sm,
    ticks=[-0.25, -0.125, 0.0, 0.125, 0.25],
    ax=ax[1],
    shrink=0.5,
    orientation="horizontal",
)
cbar.set_label("Pearson Correlation Coefficient", rotation=0)

fig.tight_layout()
fig.savefig(
    os.path.join(fig_path, "Supplementary1_cbar.svg"), bbox_inches="tight", dpi=300
)
fig.savefig(
    os.path.join(fig_path, "Supplementary1_cbar.png"), bbox_inches="tight", dpi=300
)
