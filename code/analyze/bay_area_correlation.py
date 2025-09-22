import geopandas as gpd
import pandas as pd

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # should be the root of the repo

# locate the data folders
corr_dir = os.path.join(basepath, "data/correlation")
ca_corr_df = pd.read_csv(os.path.join(corr_dir, "caiso_mef_pearson.csv"))
sf_node_df = pd.read_csv(os.path.join(basepath, "data", "geospatial", "iso", "SFLMPLocations.csv"))
iso = gpd.read_file(os.path.join(basepath, "data", "iso", "Independent_System_Operators.shp")).astype({"ID": "int64"})
caiso = iso[iso["NAME"] == "CALIFORNIA INDEPENDENT SYSTEM OPERATOR"]

jan_df = ca_corr_df[ca_corr_df["month"] == 1]
apr_df = ca_corr_df[ca_corr_df["month"] == 4]
jul_df = ca_corr_df[ca_corr_df["month"] == 7]
oct_df = ca_corr_df[ca_corr_df["month"] == 10]

corr_gdf_a = gpd.GeoDataFrame(
    jan_df, geometry=gpd.points_from_xy(jan_df.longitude, jan_df.latitude), crs=caiso.crs
)
corr_gdf_b = gpd.GeoDataFrame(
    jul_df, geometry=gpd.points_from_xy(jul_df.longitude, jul_df.latitude), crs=caiso.crs
)

print("Max correlation in SF in January:",
    corr_gdf_a[corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())]["pearson_cc"].max()
)
print("Min correlation in SF in January:",
    corr_gdf_a[corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())]["pearson_cc"].min()
)
print("Average correlation in SF in January:",
    corr_gdf_a[corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())]["pearson_cc"].mean()
)

print("Min correlation in SF in July:",
    corr_gdf_b[corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())]["pearson_cc"].min()
)
print("Max correlation in SF in July:", 
    corr_gdf_b[corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())]["pearson_cc"].max()
)
print("Average correlation in SF in July:", 
    corr_gdf_b[corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())]["pearson_cc"].mean()
)

sf_jan_corr_df = corr_gdf_a[corr_gdf_a["location"].apply(lambda x: x in sf_node_df["name"].tolist())]
sf_jul_corr_df = corr_gdf_b[corr_gdf_b["location"].apply(lambda x: x in sf_node_df["name"].tolist())]

print(sf_jul_corr_df[sf_jul_corr_df["location"] == "ELCRRTO_1_N023"])
print(sf_jul_corr_df[sf_jul_corr_df["location"] == "GRIZZLY_7_N101"])
print(sf_jul_corr_df[sf_jul_corr_df["pearson_cc"] == -0.1808122779328591])