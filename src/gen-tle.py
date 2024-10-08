import random
from datetime import datetime,timedelta
import numpy as np
from tensorflow.keras.models import load_model

from skyfield.api import EarthSatellite, load
from pytz import timezone


class Satellite:
    def __init__(self,name,inclination,eccentricity,altitude):
        self.name = name
        self.sat_num,self.IDesignator = random.sample(range(10000,99999),2)
        self.epoch_time = self.get_epoch_time()
        self.n = 0.00001
        self.n_dot = 0
        
        #get_checksum

        self.altitude = altitude
        #line2
        self.inclination = inclination
        self.eccentricity = eccentricity
        self.mean_motion = self.Mean_motion(altitude) #get mean_motion()
        self.mean_anomaly = self.Mean_anomaly(self.mean_motion,3600) #get mean_anomaly()
        self.revs = self.get_revs(self.mean_motion,self.epoch_time)
        self.raan = self.get_raan(self.inclination,self.eccentricity,self.altitude,self.mean_motion)
        self.aop = self.get_aop(self.inclination,self.eccentricity,self.altitude,self.mean_motion)
        self.drag_term = self.get_drag(self.inclination,self.eccentricity,self.altitude,self.mean_motion)
        #get_checksum
    


    def set_epoch(self,epoch):
        self.epoch_time = epoch

    def checksum(self,line):
        sum=0
        if line == 1:
            sum = self.sat_num + self.IDesignator + float(self.epoch_time) + self.n + self.n_dot + float(self.drag_term[:5]) + float(self.drag_term[-1])
        if line == 2:
            sum = self.sat_num + self.inclination + self.eccentricity + self.aop + self.mean_motion + self.mean_anomaly+self.revs

        return int(sum)%10
    
    def Mean_motion(self,altitude):
        G = 6.674 * 10**-11  # Gravitational constant (m³/kg/s²)
        M = 5.972 * 10**24  # Mass of central body (kg)
        R = 6371000  # Radius of Earth (m)

        a = R + altitude*1000  
        
        T_squared = (4 * np.pi**2 * a**3) / (G * M)
        T = np.sqrt(T_squared)/3600

        return 24/T
    
    def get_line1(self):
        line1 = '1 {:5}U {:5}S   {:.8f}  .00001001  00000-0  {:7} 0  999{:1}'.format(self.sat_num,self.IDesignator,self.epoch_time,self.drag_term,self.checksum(1))
        return line1
    
    def get_line2(self):
        line2 = '2 {:5} 0{:.4f} {:.4f} {:7} {:.4f} {:.4f}  {:.8f} {:4}{:1}'.format(self.sat_num, self.inclination, self.raan, str(self.eccentricity)[2:], self.aop,self.mean_anomaly, self.mean_motion,self.revs,self.checksum(2))
        return line2

    def get_tle(self):
        tle = self.name + '\n' + self.get_line1() + '\n' + self.get_line2()
        return tle

    def Mean_anomaly(self,mean_motion_rev_per_day, elapsed_time_seconds):

        mean_motion_rad_per_sec = 2 * np.pi * mean_motion_rev_per_day / 86400
        mean_anomaly_rad = mean_motion_rad_per_sec * elapsed_time_seconds
        mean_anomaly_deg = np.degrees(mean_anomaly_rad)
        
        return mean_anomaly_deg % 360
    
    def get_epoch_time(self):
        now = datetime(2024,4,15)
        year = now.strftime("%y")
        day_of_year = now.strftime("%j")
        fraction_of_day = (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) / (24 * 3600)
        fraction_of_day = str(fraction_of_day)[2:]
        timestamp = f"{year}{day_of_year}.{fraction_of_day}"

        return float(timestamp)
    
    def get_raan(self,inclination, eccentricity, height, mean_motion):
        model = load_model('./model/raan.h5')
        input_data = np.array([[inclination, eccentricity, height, mean_motion]])
        prediction = model.predict(input_data)
        return prediction[0][0]%360
    
    def set_raan(self,raan):
        self.raan = raan
    
    def get_aop(self,inclination, eccentricity, height, mean_motion):
        model = load_model('./model/aop.h5')
        input_data = np.array([[inclination, eccentricity, height, mean_motion]])
        prediction = model.predict(input_data)
        return prediction[0][0]%360
    
    def get_drag(self,inclination, eccentricity, height, mean_motion):
        model = load_model('./model/drag.h5')
        input_data = np.array([[inclination, eccentricity, height, mean_motion]])
        prediction = model.predict(input_data)
        s = list("{:e}".format(float(prediction[0][0])))
        s.pop(1)
        res = s[:5]
        res.append('-')
        res.append(s[-1])
        return "".join(res)
    

    def get_revs(self,mm,epoch_time):
        now = datetime.now()
        year = now.strftime("%y")
        day_of_year = now.strftime("%j")
        fraction_of_day = (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) / (24 * 3600)
        fraction_of_day = str(fraction_of_day)[2:]
        timestamp = float(f"{year}{day_of_year}.{fraction_of_day}")

        delta = timestamp - epoch_time
        return int(mm*delta)
        

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


def get_constellation(eccentricity,altitude,inclination,orbit_count,sat_per_orbit):
    total_sat = orbit_count*sat_per_orbit
    raan_dif = 360/orbit_count
    init_sat = Satellite('test',inclination,eccentricity,altitude)
    init_raan = init_sat.raan
    orbital_period = 1/init_sat.mean_motion
    op_diff = orbital_period/sat_per_orbit
    

    constellation = []
    constellation.append(init_sat.get_tle())

    for i in range(orbit_count):
        for j in range(sat_per_orbit):
            sat = Satellite(f'test{i}{j}',inclination,eccentricity,altitude)
            sat.set_raan((init_raan + raan_dif*i)%360)
            sat.set_epoch(sat.epoch_time + j*op_diff)
            constellation.append(sat.get_tle())
    
    return constellation

s = Satellite('test',15.00000,0.0001231,1000)
print(s.get_tle())

l1 = s.get_line1()
l2 = s.get_line2()
print(get_xyz(s.name,l1,l2,[2024,4,20]))

constellation = get_constellation(0.0001231,1000,15.000000,5,20)
with open('new_constellation.txt','w') as file:
    for tle in constellation:
        file.write(tle+'\n')

print('constellation is saved to ./new_constellation.txt')


