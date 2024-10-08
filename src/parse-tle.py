import pandas as pd
from pyorbital.orbital import Orbital
from datetime import datetime
import math
from skyfield.api import EarthSatellite, load
from pytz import timezone

def intersatellite_distance(x1,x2,y1,y2,z1,z2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)

def get_xyz(name,line1,line2,date):
    ts = load.timescale()
    satellite = EarthSatellite(line1, line2, name=name)

    tz = timezone('Asia/Kolkata')
    time = tz.localize(datetime(date[0], date[1], date[2]))
    time = ts.utc(time)

    position = satellite.at(time)
    subpoint = position.subpoint()

    lon = subpoint.longitude.degrees
    lat = subpoint.latitude.degrees
    alt = subpoint.elevation.km

    return (lon,lat,alt)

# Function to parse TLE data
def parse_tle(tle_files,date):
    df = pd.DataFrame({
            'Name': [],
            'Catalog Number': [],
            'Epoch Time': [],
            'Inclination': [],
            'RAAN': [],
            'Eccentricity': [],
            'Argument of Perigee': [],
            'Mean Anomaly': [],
            'Mean Motion': [],
            'Constellation':[],
            'Plane':[],
            'Latitude':[],
            'Longitude':[],
            'Altitude':[],
            'Drag':[],
            'Mean_derivative_1':[]
        })

    for tle_file in tle_files:
        with open(tle_file, 'r') as file:
            lines = file.readlines()

        # Extracting relevant information from TLE lines
        names = [lines[i].strip() for i in range(0, len(lines), 3)]
        tle_data = [(lines[i+1].strip(), lines[i+2].strip()) for i in range(0, len(lines), 3)]

        # Splitting TLE data into components
        catalog_numbers = [tle[1][2:7] for tle in tle_data]
        epoch_times = [tle[0][18:32] for tle in tle_data]
        inclinations = [tle[1][8:16] for tle in tle_data]
        raans = [tle[1][17:25] for tle in tle_data]
        eccentricities = [float('0.'+tle[1][26:33]) for tle in tle_data]
        arguments_of_perigee = [tle[1][34:42] for tle in tle_data]
        mean_anomalies = [tle[1][43:51] for tle in tle_data]
        mean_motions = [tle[1][52:63] for tle in tle_data]
        constellation = [(((tle_file.split('/'))[-1]).split('-'))[0].lower()]
        constellation = constellation*len(raans)
        plane = [int(float(i.strip())) for i in inclinations]

        xyz = [get_xyz(names[i], tle_data[i][0], tle_data[i][1],date) for i in range(0,len(names))]
        lat = [xyz[i][0] for i in range(len(xyz))]
        lon = [xyz[i][1] for i in range(len(xyz))]
        alt = [xyz[i][2] for i in range(len(xyz))]

        drags = [tle[0][54:59] for tle in tle_data]
        radiation = [tle[0][60] for tle in tle_data]

        drags = [float(f'{drags[i][0]}.{drags[i][1:]}e-{radiation[i]}') for i in range(len(drags))]
        md = [float(tle[0][34:43]) for tle in tle_data]

        print(tle_file)
        # Create DataFrame
        df2 = pd.DataFrame({
            'Name': names,
            'Catalog Number': catalog_numbers,
            'Epoch Time': epoch_times,
            'Inclination': inclinations,
            'RAAN': raans,
            'Eccentricity': eccentricities,
            'Argument of Perigee': arguments_of_perigee,
            'Mean Anomaly': mean_anomalies,
            'Mean Motion': mean_motions,
            'Constellation':constellation,
            'Plane':plane,
            'Latitude':lat,
            'Longitude':lon,
            'Altitude':alt,
            'Drag':drags,
            'Mean_derivative_1':md
        })

        # df =  df.append(df2)
        df = pd.concat([df,df2])
    return df

# Example usage
tle_file = ['./data/intelesat-tle.txt','./data/GLOBALSTAR-tle.txt','./data/iridium-next-tle.txt','./data/ONEWEB-tle.txt','./data/ORBCOMM-tle.txt','./data/STARLINK-tle.txt','./data/satnogs-tle.txt']  # Replace with the path to your TLE data file
# tle_file = ['./data/STARLINK-tle.txt']
df = parse_tle(tle_file,[2023,3,14])
for i in range (5):
    df2 = parse_tle(tle_file,[2023,3,14+i])
    df = pd.concat([df,df2])
print(df.columns)
df.to_csv("tle.csv")
