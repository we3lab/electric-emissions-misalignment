from matplotlib.transforms import ScaledTranslation
from shapely.affinity import translate
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import os

# change to root of repository
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
basepath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # should be the root of the repo

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

region_order = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM","SPP", "Other"]

## NOTE: Unlike the other notebooks where all subplots are created in `matplotlib`,
#  Subplot A is created separately due to spacing issues with `geopandas`

## Subplot A
fig, ax = plt.subplots(1, 1, figsize=(90 / 25.4, 90 / 25.4))
ax = [ax]
dr_data_path = os.path.join("data", "dr")
program_data = pd.read_csv(os.path.join(dr_data_path, "us_program_data.csv"), encoding="latin1")

# Group by state and count # of programs
state_program_counts = program_data.groupby('state').size().reset_index(name='num_programs')
result = state_program_counts.copy()

# Create a list of all US states you want to include
all_states = ['KS', 'LA', 'ME', 'NV', 'RI', 'WY']

# Combine the existing states with the new states and sort alphabetically
combined_states = sorted(set(result['state'].tolist() + all_states))

# Reindex the DataFrame to include all states, filling new rows with NaN
result_with_all_states = result.set_index('state').reindex(combined_states).reset_index()

# Sort the DataFrame by state
result_with_all_states = result_with_all_states.sort_values('state')

# Display the resulting dataset
print(result_with_all_states)

# Display the updated dataset
print(result_with_all_states)

max_prices_and_penalties = result_with_all_states

# Define the folder and file name
map_name = "cb_2018_us_state_500k.shp"

# Construct the full file path
map_path = os.path.join(basepath, "data", "geospatial", "state", map_name)

# Check if the file exists
if os.path.exists(map_path):
    try:
        # Try to read the shapefile to ensure it's usable
        us_states = gpd.read_file(map_path)
        print(f"File '{map_name}' exists and is usable.")
    except Exception as e:
        print(f"File '{map_name}' exists but is not usable. Error: {e}")
else:
    print(f"File '{map_name}' does not exist in the folder '{map_path}'.")

# Remove territories and keep only 50 states
us_states = us_states[us_states['STUSPS'].isin(['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                                                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                                                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                                                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                                                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'])]


# Merge program counts with shapefile data
merged_data = us_states.merge(state_program_counts, left_on='STUSPS', right_on='state', how='left')

# Define makeColorColumn to assign colors based on a column's values
def makeColorColumn(data, column, vmin, vmax, cmap='viridis'):
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.get_cmap(cmap)
    data['value_determined_color'] = data[column].apply(lambda x: mcolors.to_hex(cmap(norm(x))) if pd.notnull(x) else '#D3D3D3')
    return data

# Replace the price-related columns with the number of programs
def create_map(data, column, title, cmap='viridis'):
    # Set parameters
    variable = column
    vmin, vmax = data[column].min(), data[column].max()
    data = makeColorColumn(data, variable, vmin, vmax, cmap=cmap)

    # Create "visframe" as a re-projected GeoDataFrame using EPSG 2163 for CONUS
    visframe = data.to_crs({'init': 'epsg:2163'})

    # turn axis line off
    ax[0].axis('off')

    # Plot CONUS states (excluding Alaska and Hawaii)
    for row in visframe.itertuples():
        if row.STUSPS not in ['AK', 'HI']:
            vf = visframe[visframe['STUSPS'] == row.STUSPS]
            c = data[data['STUSPS'] == row.STUSPS]['value_determined_color'].iloc[0]
            vf.plot(color=c, linewidth=1, ax=ax[0], edgecolor="black")

    # Set limits for continental US
    ax[0].set_xlim(-2800000, 2800000)
    ax[0].set_ylim(-2800000, 1000000)

    # Add Alaska (scaled and repositioned)
    alaska = visframe[visframe['STUSPS'] == "AK"].scale(xfact=0.50, yfact=0.50, origin=(0, 0))
    alaska = alaska.translate(xoff=-470000, yoff=-3500000)
    alaska.plot(color=data[data["STUSPS"] == "AK"]["value_determined_color"].iloc[0],
                linewidth=1, ax=ax[0], edgecolor="black")

    # Add Hawaii (scaled and repositioned)
    hawaii = visframe[visframe['STUSPS'] == "HI"].scale(xfact=1, yfact=1, origin=(0, 0))
    hawaii = hawaii.translate(xoff=5000000, yoff=-1500000)
    hawaii.plot(color=data[data["STUSPS"] == "HI"]["value_determined_color"].iloc[0],
                linewidth=1, ax=ax[0], edgecolor="black")

    # Add colorbar legend to the side
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax[0], orientation="horizontal", shrink=0.33, pad=0)
    cbar.set_label("Number of Programs", rotation=0, fontweight="bold")
    cbar.ax.set_xticks(np.linspace(vmin, vmax, num=5))
    cbar.ax.set_xticklabels([f"{int(x)}" for x in np.linspace(vmin, vmax, num=5)])

# Create a map showing the number of programs in each state
create_map(merged_data, "num_programs", "Number of Programs by State", cmap="Blues")

## Save Subplot A
labels = ["a."]

# from https://matplotlib.org/stable/gallery/text_labels_and_annotations/label_subplots.html
for label, axis in zip(labels, ax):
    # Use ScaledTranslation to put the label
    # - at the top left corner (axes fraction (0, 1)),
    # - offset 20 pixels left and 7 pixels up (offset points (-20, +7)),
    # i.e. just outside the axes.
    axis.text(
        0.0, 
        1.0, 
        label, 
        transform=(axis.transAxes + ScaledTranslation(-6/72, -12/72, fig.dpi_scale_trans)),
        va='bottom',
        fontsize=10
    )

fig.tight_layout()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Figure4a.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure4a.png"), bbox_inches="tight", dpi=300)

## Subplot B
# create subplots B + C on a single subplot
# 1-column width = 80 mm
# 2-column width = 190 mm
# max height is 240 mm
fig, ax = plt.subplots(2, 1, figsize=(90 / 25.4, 120 / 25.4))

data = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname((__vsc_ipynb_file__))), 'data/dr/us_program_data.csv'))

# Group by iso/rto and calculate the necessary statistics
iso_rto_durations = data.groupby(['iso/rto'])[['min_dur', 'max_dur']].mean().reset_index()

# make any nan min duration 0 and and nan max duration 24
iso_rto_durations['min_dur'] = iso_rto_durations['min_dur'].fillna(1)
iso_rto_durations['max_dur'] = iso_rto_durations['max_dur'].fillna(6.28)

# Create a new column for the duration height
iso_rto_durations['dur_height'] = iso_rto_durations['max_dur'] - iso_rto_durations['min_dur']

# replace row iso/rto name other with Other
iso_rto_durations['iso/rto'] = iso_rto_durations['iso/rto'].replace('other', 'Other')

# reorder rows to make sure the order is correct
iso_rto_durations['iso/rto'] = pd.Categorical(iso_rto_durations['iso/rto'], categories=region_order, ordered=True)
# Sort the DataFrame by the 'iso/rto' column
iso_rto_durations = iso_rto_durations.sort_values('iso/rto')
iso_rto_durations.reset_index(drop=True, inplace=True)

ax[0].bar(
    iso_rto_durations['iso/rto'], 
    iso_rto_durations['dur_height'], 
    bottom=iso_rto_durations['min_dur'], 
    color='#77A8CD', 
    edgecolor='black', 
)

ax[0].set_ylabel('Event duration\n(hours)')
# rotate the x-axis labels
x_labels = ax[0].get_xticklabels()
for i, label in enumerate(x_labels):
    label_text = label.get_text()
    if label_text == "ERCOT":
        x_labels[i].set_text("$^*$ERCOT")
    elif label_text == "NYISO":
        x_labels[i].set_text("$^*$NYISO")
    elif label_text == "Other":
        x_labels[i].set_text("$^{**}$Other")
ax[0].set_xticks(ax[0].get_xticks(), x_labels, rotation=60, ha='center')
ax[0].set_yticks(np.arange(0, 9, 2))

## Subplot C
# Load the data
prices = pd.read_csv(os.path.join(dr_data_path, "on_off_peak_prices.csv"), encoding="latin1")

# Replace 'year_round' with both 'summer' and 'winter'
prices_expanded = pd.concat([
    prices,
    prices[prices['season'] == 'year_round'].assign(season='summer'),
    prices[prices['season'] == 'year_round'].assign(season='winter')
])

# Group by 'iso/rto' and calculate the maximum values
result = prices_expanded.groupby('iso/rto').agg(
    max_winter_price=('w_price', 'max'),
    max_summer_price=('s_price', 'max'),
    max_penalty=('penalty', 'max')
).reset_index()

# Display the resulting dataset
print(result)

# Multiply relevant columns by 1000 to convert from dollars per kW to dollars per MW
result[['max_summer_price', 'max_winter_price', 'max_penalty']] = (
    result[['max_summer_price', 'max_winter_price', 'max_penalty']] * 1000
)

# Scale the prices to $1000 per MW
result[['max_summer_price', 'max_winter_price', 'max_penalty']] = (
    result[['max_summer_price', 'max_winter_price', 'max_penalty']] / 1000
)

# Display the updated dataset
print(result)

# Assign the processed DataFrame to a variable for further use
result_with_all_states = result

# Use the result_with_all_states DataFrame from the first cell
data = result_with_all_states
data['iso/rto'] = data['iso/rto'].replace('other', 'Other')

region_order = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM","SPP", "Other"]

# reorder rows to make sure the order is correct
data['iso/rto'] = pd.Categorical(data['iso/rto'], categories=region_order, ordered=True)
# Sort the DataFrame by the 'iso/rto' column
data = data.sort_values('iso/rto')
data.reset_index(drop=True, inplace=True)

# Calculate the overall maximum price for each ISO/RTO
# plot a grouped bar chart on the max summer, max winter, and max penalty 

x = np.arange(len(data['iso/rto']))*3  # the label locations
width = 2.2  # the width of the bars

summer = ax[1].bar(x, data['max_summer_price'], width, color='#E2ECF7', edgecolor='black')
# winter = ax.bar(x + 0.5*width, data['max_winter_price'], width, label='Winter Price', color='#5E9BA1', edgecolor='black')
# penalty = ax.bar(x + width, data['max_penalty'], width, label='Penalty', color='grey', edgecolor='black')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax[1].set_ylabel('Maximum Price ($/kW)')

ax[1].set_xticks(x, data['iso/rto'])

ax[1].set_yticks(np.arange(0, 260, 50))
ax[1].set_ylim(0, 250)
x_labels = ax[1].get_xticklabels()
for i, label in enumerate(x_labels):
    print(label.get_text())
    if label.get_text() == "Other":
        x_labels[i].set_text("$^{**}$Other")
ax[1].set_xticks(ax[1].get_xticks(), labels=x_labels, rotation=60, ha='center')

## Save Subplots B and C
labels = ["b.", "c."]

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
        transform=(axis.transAxes + ScaledTranslation(-24/72, 12/72, fig.dpi_scale_trans)),
        va='bottom',
        fontsize=10
    )

fig.tight_layout()
fig_path = os.path.join(basepath, "figures")
fig.savefig(os.path.join(fig_path, "Figure4bc.svg"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(fig_path, "Figure4bc.png"), bbox_inches="tight", dpi=300)