import geopandas as gpd
import pandas as pd
import os

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # should be the root of the repo

# locate the data folders
corr_dir = os.path.join(basepath, "data", "correlation")
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

corr_gdf_a = gpd.GeoDataFrame(
    jan_df,
    geometry=gpd.points_from_xy(jan_df.longitude, jan_df.latitude),
    crs=caiso.crs,
)
corr_gdf_b = gpd.GeoDataFrame(
    jul_df,
    geometry=gpd.points_from_xy(jul_df.longitude, jul_df.latitude),
    crs=caiso.crs,
)

print(
    "Max correlation in SF in January:",
    corr_gdf_a[
        corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())
    ]["pearson_cc"].max(),
)
print(
    "Min correlation in SF in January:",
    corr_gdf_a[
        corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())
    ]["pearson_cc"].min(),
)
print(
    "Average correlation in SF in January:",
    corr_gdf_a[
        corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())
    ]["pearson_cc"].mean(),
)

print(
    "Min correlation in SF in July:",
    corr_gdf_b[
        corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())
    ]["pearson_cc"].min(),
)
print(
    "Max correlation in SF in July:",
    corr_gdf_b[
        corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())
    ]["pearson_cc"].max(),
)
print(
    "Average correlation in SF in July:",
    corr_gdf_b[
        corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())
    ]["pearson_cc"].mean(),
)

sf_jan_corr_df = corr_gdf_a[
    corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())
]
sf_jul_corr_df = corr_gdf_b[
    corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())
]

print(sf_jul_corr_df[sf_jul_corr_df["location"] == "ELCRRTO_1_N023"])
print(sf_jul_corr_df[sf_jul_corr_df["location"] == "GRIZZLY_7_N101"])

#############
# Nodal Flips
#############
def aef_tariff_node_flip(row):
    if row["Jan"] < 0:
        if row["Jul"] > 0:
            return True
    elif row["Jan"] > 0:
        if row["Jul"] < 0:
            return True
    return False

def mef_dam_node_flip(df, node_id):
    try:
        jan_corr = df[(df["location"] == node_id) & (df["month"] == 1)]["pearson_cc"].values[0]
        jul_corr = df[(df["location"] == node_id) & (df["month"] == 7)]["pearson_cc"].values[0]
        if jan_corr < 0:
            if jul_corr > 0:
                return True
        elif jan_corr > 0:
            if jul_corr < 0:
                return True
        return False
    except IndexError:
        return None

total_flipped = 0
total_nodes = 0

regions = ["CAISO", "ERCOT", "ISONE", "NYISO", "PJM", "SPP", "MISO"]

for region in regions:
    aef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_aef_pearson.csv"))
    
    aef_corr_df["Flipped"] = aef_corr_df.apply(aef_tariff_node_flip, axis=1)
    total_flipped += aef_corr_df["Flipped"].sum()
    total_nodes += len(aef_corr_df["Flipped"])

    print(f"For {region}, {aef_corr_df['Flipped'].sum()} tariffs flipped of {len(aef_corr_df['Flipped'])} tariffs that flipped")
    print(f"This is equivalent to {aef_corr_df['Flipped'].sum() / len(aef_corr_df['Flipped']) * 100}%")

print(f"Overall, {total_flipped} tariffs flipped out of {total_nodes} total tariffs")
print(f"This is equivalent to {total_flipped / total_nodes * 100}%")

total_flipped = 0
total_nodes = 0

for region in regions:
    mef_corr_df = pd.read_csv(os.path.join(corr_dir, region + "_mef_pearson.csv"))
    location_ids = mef_corr_df["location"].unique()
    region_flipped = 0
    region_nodes = 0
    for node_id in location_ids:
        flipped = mef_dam_node_flip(mef_corr_df, node_id)
        if flipped is not None:
            if flipped:
                region_flipped += 1
            region_nodes += 1

    total_flipped += region_flipped
    total_nodes += region_nodes

    print(f"For {region}, there were {region_flipped} of {region_nodes} nodes that flipped")
    print(f"This is equivalent to {region_flipped / region_nodes * 100}%")

print(f"Overall, there were {total_flipped} of {total_nodes} flipped")
print(f"This is equivalent to {total_flipped / total_nodes * 100}%")

region_flipped = 0
region_nodes = 0

mef_corr_df = pd.read_csv(os.path.join(corr_dir, "CAISO_mef_pearson.csv"))
for node_id in sf_node_df["name"]:
    flipped = mef_dam_node_flip(mef_corr_df, node_id)
    if flipped is not None:
        if flipped:
            region_flipped += 1
        region_nodes += 1

print(f"For SF Bay Area, there were {region_flipped} of {region_nodes} nodes that flipped")
print(f"This is equivalent to {region_flipped / region_nodes * 100}%")