import math
import pandas as pd
import numpy as np

# Constants
g = 9.81  # gravitational acceleration in m/s^2
pipeline_depth = 7.5  # Water depth at Pipeline in meters
distance_to_pipeline_m = 200 * 1852  # Convert 200 nautical miles to meters

# 1. Calculate Transit Time with Units in Meters and Seconds
def calculate_transit_time(period, distance=distance_to_pipeline_m):
    speed = period * 1.5
    transit_time = distance / speed  # Transit time in seconds


    return transit_time


# 2. Calculate Shoaling Coefficient with Units in Meters and Seconds
def calculate_shoaling_coefficient(wavePeriod):
    L = (g * (wavePeriod ** 2)) / (2 * math.pi)  # Wavelength in meters
    Cg0 = (g * wavePeriod) / (4 * math.pi)  # Deep-water group velocity in m/s
    Cg = (g * wavePeriod / (4 * math.pi)) * np.tanh((2 * math.pi * pipeline_depth) / L)  # Adjusted group velocity
    return np.sqrt(Cg0 / Cg)  # Shoaling coefficient (dimensionless)

# 3. Calculate Wave Refraction (Wave Direction in Degrees)
def calculate_wave_refraction(waveDirection, idealDirection=295):
    direction_map = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
    }
    
    # Convert wave direction string to degrees
    waveDirection_num = waveDirection.map(direction_map)
    
    # Calculate the angular difference from the ideal direction
    dd = abs(idealDirection - waveDirection_num)
    
    # Determine the refraction factor based on the angular difference
    refraction_factors = np.where(dd < 20, 1.0, np.where(dd < 45, 0.95, 0.85))
    return refraction_factors

# 4. Predict Pipeline Wave Height (Vectorized) with Consistent Units
def predict_pipeline_wave_height_vectorized(deepWVHT, wavePeriod, waveDirection, depth=pipeline_depth, breaking_depth_coefficient=1.3):
    # Calculate shoaling coefficients for all periods
    shoaling_coefficients = calculate_shoaling_coefficient(wavePeriod)
    
    # Adjust deep-water wave height for shoaling
    shallowWVHT = deepWVHT * shoaling_coefficients
    
    # Adjust for wave refraction
    refraction_factors = calculate_wave_refraction(waveDirection)
    shallowWVHT *= refraction_factors
    
    # Apply constant wave breaking depth factor
    shallowWVHT *= breaking_depth_coefficient
    
    return shallowWVHT
