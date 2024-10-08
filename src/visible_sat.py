from skyfield.api import Topos, load
from datetime import datetime, timedelta

def count_serving_satellites(observer_lat, observer_lon, observer_elevation, altitude_threshold, tle_file,t):
    satellites = load.tle_file(tle_file)

    observer = Topos(observer_lat, observer_lon, elevation_m=observer_elevation)

    # Get current time
    

    # Look up satellite positions
    serving_satellites = []
    for satellite in satellites:
        satellite_name = satellite.name
        # tle = satellite[1:]
        # sat = load.tle_file(None, lines=tle)[satellite_name]
        sat=satellite
        difference = sat - observer
        # print(difference)
        topocentric = difference.at(t)
        alt, _, _ = topocentric.altaz()
        altitude = alt.degrees
        # print(altitude)
        if altitude > altitude_threshold:
            # print(altitude)
            serving_satellites.append(satellite_name)

    return serving_satellites

# Example usage
observer_latitude = 21.246694  # Latitude of observer location (e.g., San Francisco)
observer_longitude = 81.322146  # Longitude of observer location (e.g., San Francisco)
observer_elevation = 30  # Elevation of observer location in meters
altitude_threshold = 5  # Minimum altitude threshold for serving satellites in kilometers
tle_file = 'new_constellation.txt'  # Path to the TLE file containing satellite data

ts = load.timescale()
t = ts.now()

times = [i*10 for i in range(12)]
sats = []

for i in range (12):
    future_time = t.utc_datetime() + timedelta(days=0.006944*i) # every 10 min
    time = ts.utc(future_time.year, future_time.month, future_time.day, future_time.hour, future_time.minute, future_time.second)
    # times.append(time)
    serving_satellites = count_serving_satellites(observer_latitude, observer_longitude, observer_elevation, altitude_threshold, tle_file,time)
    sats.append(len(serving_satellites))
print("Number of serving satellites:", len(serving_satellites))
print("Serving satellites:", serving_satellites)


print(times)
print(sats)


import matplotlib.pyplot as plt


# Plotting the bar graph
plt.bar(times, sats, color='skyblue')
plt.axhline(max(sats), color='red', linestyle='--', label='Average Value')
plt.title('No of serving satellite vs relative time (min)')
plt.xlabel('Relative Time (min)')
plt.ylabel('Number of serving satellite')
plt.grid(axis='y')
plt.show()
