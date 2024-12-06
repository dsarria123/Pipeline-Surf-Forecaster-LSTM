import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import wget
import numpy as np


def connect_to_db():
    '''
    Connects engine to database
    '''
    try:
        DATABASE_URL = "postgresql+psycopg2://postgres:ilikepie123@localhost:5432/51101BuoyData"
        engine = create_engine(DATABASE_URL)
        return engine
    except SQLAlchemyError as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_latest_datetime(engine):
    query = 'SELECT MAX("datetime") FROM "51101BuoyData"'
    try:
        latest_datetime = pd.read_sql(query, engine)['max'][0]  
        return latest_datetime
    except Exception as e:
        print(f"Error fetching latest datetime: {e}")
        return None

def get_processed_data():
    try:
        url_standard_data = 'https://www.ndbc.noaa.gov/data/realtime2/51101.txt'
        url_spectral_wave_data = 'https://www.ndbc.noaa.gov/data/realtime2/51101.spec'

        # Download and load standard meteorological data
        standard_data = wget.download(url_standard_data)
        col_names = ['YY', 'MM', 'DD', 'hh', 'mm', 'WDIR', 'WSPD', 'GST', 'WVHT', 'DPD', 'APD', 'MWD', 'PRES', 'ATMP', 'WTMP', 'DEWP', 'VIS', 'PTDY', 'TIDE']
        mdata = pd.read_csv(standard_data, delim_whitespace=True, comment='#', names=col_names)

        # Download and load spectral wave data
        wave_data = wget.download(url_spectral_wave_data)
        col_names = ['YY', 'MM', 'DD', 'hh', 'mm', 'WVHT', 'SwH', 'SwP', 'WWH', 'WWP', 'SwD', 'WWD', 'Steepness', 'APD', 'MWD']
        sdata = pd.read_csv(wave_data, delim_whitespace=True, comment='#', names=col_names)

        # Convert the date-time columns into a single 'datetime' column
        sdata['datetime'] = pd.to_datetime(sdata[['YY', 'MM', 'DD', 'hh', 'mm']].rename(columns={'YY': 'year', 'MM': 'month', 'DD': 'day', 'hh': 'hour', 'mm': 'minute'}))
        mdata['datetime'] = pd.to_datetime(mdata[['YY', 'MM', 'DD', 'hh', 'mm']].rename(columns={'YY': 'year', 'MM': 'month', 'DD': 'day', 'hh': 'hour', 'mm': 'minute'}))

        # Drop the individual date and time columns
        sdata.drop(['YY', 'MM', 'DD', 'hh', 'mm'], axis=1, inplace=True)
        mdata.drop(['YY', 'MM', 'DD', 'hh', 'mm', 'WVHT', 'APD', 'MWD', 'TIDE', 'PTDY', 'VIS'], axis=1, inplace=True)

        # Replace 'MM' with NaN
        mdata.replace('MM', np.nan, inplace=True)
        sdata.replace('MM', np.nan, inplace=True)

        # Convert columns to numeric where necessary
        sdata_numeric_cols = ['WVHT', 'SwH', 'SwP', 'WWH', 'WWP','APD', 'MWD']
        mdata_numeric_cols = ['WDIR', 'WSPD', 'GST', 'DPD', 'PRES', 'ATMP', 'WTMP', 'DEWP']

        # Apply numeric conversion
        sdata[sdata_numeric_cols] = sdata[sdata_numeric_cols].apply(pd.to_numeric, errors='coerce')
        mdata[mdata_numeric_cols] = mdata[mdata_numeric_cols].apply(pd.to_numeric, errors='coerce')

        # Interpolate missing values for Dominant Wave Period
        mdata['DPD'] = mdata['DPD'].interpolate(method='linear')
        mdata['DPD'] = mdata['DPD'].fillna(method='bfill')

        # Merge the two datasets based on 'datetime'
        combined_data = pd.merge(sdata, mdata, on='datetime', how='left')

        return combined_data

    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def update_db(engine, combined_data):
    latest_datetime = get_latest_datetime(engine)
    
    if latest_datetime is not None:
        # Filter the new data based on the latest datetime
        new_data = combined_data[combined_data['datetime'] > latest_datetime]
    else:
        new_data = combined_data

    if not new_data.empty:
        try:
            # Insert new data into the database
            new_data.to_sql('51101BuoyData', engine, if_exists='append', index=False)
            print(f"{len(new_data)} new rows inserted")
        except Exception as e:
            print(f"Error while inserting data: {e}")
    else:
        print("No new data to insert.")

def main():
    engine = connect_to_db()
    if engine:
        combined_data = get_processed_data()
        if combined_data is not None:
            update_db(engine, combined_data)
            print("Database updated")
        else:
            print("Failed to process data")
    else:
        print("Failed to connect to database")

if __name__ == "__main__":
    main()
