import math
import pandas as pd
import numpy as np

def calculate_shoaling_coefficient(wavePeriod):
    g = 9.81
    h = 7.5  # Water depth at Pipeline
    L = (g * (wavePeriod ** 2)) / (2 * math.pi)
    Cg0 = (g * wavePeriod) / (4 * math.pi)
    Cg = (g * wavePeriod / (4 * math.pi)) * np.tanh((2 * math.pi * h) / L)
    return np.sqrt(Cg0 / Cg)

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

def predict_pipeline_wave_height_vectorized(deepWVHT, wavePeriod, waveDirection, depth=7.5, breaking_depth_coefficient=1.3):
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

# Load data
df = pd.read_csv('testing/cleaned_data.csv')
filtered_td = df[df['WVHT'] > 2.7]
td10 = filtered_td.head(10)

# Calculate predicted wave height
td10['predictedWVHT'] = predict_pipeline_wave_height_vectorized(
    td10['WVHT'],
    td10['SwP'],
    td10['SwD']
)

print(td10)
