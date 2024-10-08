from skyfield.api import EarthSatellite, load
from pytz import timezone
import math
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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


def points_within_circle(center, radius, points):
    within_circle = []
    for point in points:
        distance = math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2 + (point[2] - center[2])**2)
        if distance <= radius:
            within_circle.append(point)
    return len(within_circle)

points = []
with open('new_constellation.txt','r') as file:
    lines = file.readlines()

for i in range(0,len(lines),3):
    points.append(get_xyz(lines[i],lines[i+1],lines[i+2],[2024,4,20]))

ra = [5,10,15,20,25,30,35,40,45,50]
avg = []

for r in ra:
    links = []
    for i in range(len(points)):
        link = points_within_circle(points[i],r,points) - 1
        # print(link)
        links.append(link)
    avg.append(int(np.mean(links)))


res = []
for x in avg:
    if x>1:
        res.append(x)
print('No of ISL = ',min(res))



# print('No of ISL terminal(considering each satellite having dadicated link for Inter-satellite communication) = ',average_value)

# Plotting the bar graph
plt.bar(ra, avg, color='skyblue')
# plt.axhline(average_value, color='red', linestyle='--', label='Average Value')
plt.title('No. Of ISL Links vs radius (Transmission Range)')
plt.xlabel('satellite')
plt.ylabel('Average link count')
plt.grid(axis='y')
plt.show()

