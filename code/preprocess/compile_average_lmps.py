import pandas as pd
import glob
import os

regions = ["CAISO", "ERCOT", "ISONE", "MISO", "NYISO", "PJM", "SPP"]

for region in regions:
    basepath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # should be the root of the repo
    folderpath = os.path.join(basepath, region)

    month_to_str = {
        1:'Jan',
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'Jun',
        7:'Jul',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec',
    }

    files = glob.glob(folderpath + '/*.csv')
    if len(files) != 12:
        print(len(files))
        raise ValueError('There are not 12 files in the folder')

    regional_data = pd.DataFrame(columns=['month','hour','USD_per_MWh'])
    regional_data['month'] = regional_data['month'].astype(int)
    regional_data['hour'] = regional_data['hour'].astype(int)
    regional_data['USD_per_MWh'] = regional_data['USD_per_MWh'].astype(float)

    for month in range(1,13):
        # grab the file that contains the month
        for f in files:
            if month_to_str[month] in f:
                df = pd.read_csv(f, parse_dates=["timestamp_local", "timestamp_utc"])
                lmp = []
                for hour in range(0,24):
                    print(df[df["timestamp_local"].dt.hour == hour]["LMP"].mean())
                    lmp.append(df[df["timestamp_local"].dt.hour == hour]["LMP"].mean())

                month_data = np.ones((24,1))*month
                hour_data = np.arange(24)

                # append
                regional_data = pd.concat([regional_data,pd.DataFrame(np.hstack([month_data.reshape(-1,1),hour_data.reshape(-1,1),np.array(lmp).reshape(-1,1)]),columns=['month','hour','USD_per_MWh'])],axis=0)

    # save the data
    regional_data = regional_data.reset_index(drop=True)
    regional_data.to_csv(os.path.join(basepath, 'data', 'LMPs', region + 'costs.csv', index=False))
