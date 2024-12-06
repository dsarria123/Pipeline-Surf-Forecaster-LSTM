# DSC412-project


# Wave Prediction for Pipeline using LSTM and 51101 Buoy data

This project aims to predict surf conditions (wave height, period, and direction) using historical and real-time data from NOAA buoy 51101 by Pipeline. By leveraging a Long Short-Term Memory (LSTM) model, the goal is to provide surfers with reliable, spot-specific wave forecasts by incorporating wave transit time adjustments to translate offshore buoy data to nearshore conditions. The SQL database is updated monthly with the latest NOAA buoy data, and the model is continuously improved as part of an ongoing project. The model uses historical meteorological and wave data from NOAA Station 51101.

- **Tools & Libraries**:
  - **Python**: Core programming and model development.
  - **PostgreSQL**: For continuous data collection and storage of NOAA buoy data.
  - **Pandas & NumPy**: For data cleaning and manipulation.
  - **Keras (TensorFlow)**: To build and train the LSTM model.
  - **NOAA API**: To access historical and real-time buoy data.


### Methodology

1. **Data Collection** (updateSqlDatabase.py): 
   - Historical data from NOAA is collected using the updateSqlDatabase.py script, which retrieves the data from the API and stores it in a PostgreSQL database, including meteorological and wave parameters (e.g., wind speed, wave height).

2. **Data Preprocessing**: (preprocessing.py, transformations.py)
   - Data is standardized and cleaned, with timestamps created for each entry.
   - Wave transit time adjustments are applied to align the buoy data with the specific surf spot conditions.

4. **Model Development**: (modelipynb)
   - An LSTM neural network is trained on past wave and weather data to predict future surf conditions at the surf spot.


