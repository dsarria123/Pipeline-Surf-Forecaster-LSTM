import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
from tensorflow.keras.optimizers import Adam



def preprocess(buoy_data):

# Convert `datetime` column to datetime format
	buoy_data['datetime'] = pd.to_datetime(buoy_data['datetime'])

# Handle missing values
	numeric_columns = buoy_data.select_dtypes(include=['float64', 'int64']).columns
	buoy_data[numeric_columns] = buoy_data[numeric_columns].interpolate()

# Drop column with all missing values
	buoy_data = buoy_data.drop(['DEWP'], axis=1)

# Encode categorical columns using LabelEncoder
	categorical_columns = ['SwD', 'WWD', 'Steepness']
	label_encoders = {}
	for col in categorical_columns:
		le = LabelEncoder()
		buoy_data[col] = le.fit_transform(buoy_data[col].astype(str))
		label_encoders[col] = le

# Extract time-of-year features and apply sine/cosine transformations
	buoy_data['month'] = buoy_data['datetime'].dt.month
	buoy_data['day_of_year'] = buoy_data['datetime'].dt.dayofyear

# Sine/Cosine transformations for cyclical encoding
	buoy_data['month_sin'] = np.sin(2 * np.pi * buoy_data['month'] / 12)
	buoy_data['month_cos'] = np.cos(2 * np.pi * buoy_data['month'] / 12)
	buoy_data['day_sin'] = np.sin(2 * np.pi * buoy_data['day_of_year'] / 365)
	buoy_data['day_cos'] = np.cos(2 * np.pi * buoy_data['day_of_year'] / 365)

# Drop columns that are not needed anymore
	buoy_data = buoy_data.drop(['datetime', 'month', 'day_of_year'], axis=1)


	return buoy_data