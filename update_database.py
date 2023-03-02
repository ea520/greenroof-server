from SQL_app.models import Base
from SQL_app.models import Temperature, SoilMoisture, Weather
from SQL_app.database import SessionLocal, engine
from data_parsers.temperature_parser import get_temperatures
from data_parsers.soil_moisture_parser import get_soil_moisture_1, get_soil_moisture_2
from data_parsers.weather_parser import get_weather
import time
import datetime
import logging
from sqlalchemy import inspect
logging.basicConfig(filename='./logs/update_database.log',format='%(asctime)s %(message)s', level=logging.INFO)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

def insert_temps(temps: Temperature):
   return db.merge(temps)

def insert_weather(weather: Weather):
    return db.merge(weather)

# Special case because rows may be incomplete
def insert_moistures(moistures: SoilMoisture):
    # look if there's an entry at this time stamp
    old_data = db.query(SoilMoisture).filter(SoilMoisture.timestamp == moistures.timestamp).first()
    new_data = moistures
    
    # if there was an entry, merge the 2 entries to remove nulls
    # if any old values are not null, add those values to the new data
    if old_data is not None:
        new_data.power_1 = moistures.power_1 if old_data.power_1 is None else old_data.power_1
        new_data.power_2 = moistures.power_2 if old_data.power_2 is None else old_data.power_2
        fields = [f"soil_moisture_{i:02}" for i in range(1, 20+1)]
        for field in fields:
            old_value = getattr(old_data, field)
            if old_value is not None:
                setattr(new_data, field, old_value)
    # replace the row at this timestamp with a new row that has the extra data
    return db.merge(new_data)



def get_latest_moisture_time():
    timestamp = datetime.datetime.now()
    updated = False
    for el in inspect(SoilMoisture).columns:
        val = db.query(SoilMoisture.timestamp).order_by(SoilMoisture.timestamp.desc()).filter(el != None).first()
        if(val is not None and val[0] is not None):
            timestamp = min(timestamp, val[0])
            updated = True
    if not updated:
        timestamp = datetime.datetime.fromtimestamp(0.)
    return timestamp

def get_latest_weather_time():
    timestamp = datetime.datetime.now()
    val = db.query(Weather.timestamp).order_by(Weather.timestamp.desc()).filter(Weather.timestamp != None).first()
    if val is not None and val[0] is not None:
        return val[0]
    return datetime.datetime.fromtimestamp(0)

# get the most recent timestamp in the corresponding table for which a row has no nulls
latest_weather_time = get_latest_weather_time()
latest_moisture_time  = get_latest_moisture_time()

# create generators which go through text files line by line and output the next row of the table
temperatures = get_temperatures(datetime.datetime.fromtimestamp(0.))
moistures1 = get_soil_moisture_1(latest_moisture_time)
moistures2 = get_soil_moisture_2(latest_moisture_time)
weather = get_weather(latest_weather_time)


while True:
    # This is just to speed up initialising the tables
    # insert up to N rows before comitting
    # if you reach the end of the file, commit and move on
    N = 1000
    for _ in range(N):
        new_temp = next(temperatures)
        if new_temp is not None:
            s = f"New temperature ({new_temp.timestamp})"
            logging.info(s)
            print(s)
            insert_temps(new_temp)
        else:
            break
    db.commit()
    for _ in range(N):
        new_weather = next(weather)
        if new_weather is not None:
            s = f"New weather ({new_weather.timestamp})"
            logging.info(s)
            print(s)
            insert_weather(new_weather)
        else:
            break
    db.commit()
    for _ in range(N):
        new_moisture1 = next(moistures1)
        if new_moisture1 is not None:
            s = f"New soil moisture ({new_moisture1.timestamp})"
            logging.info(s)
            print(s)
            insert_moistures(new_moisture1)
        else:
            break
    db.commit()
    for _ in range(N):
        new_moisture2 = next(moistures2)
        if new_moisture2 is not None:
            s = f"New soil moisture ({new_moisture2.timestamp})"
            logging.info(s)
            print(s)
            insert_moistures(new_moisture2)
        else:
            break
    db.commit()
    # if there is no new data waiting, sleep for 5 mins
    if new_temp is new_weather is new_moisture1 is new_moisture2 is None:
        time.sleep(5*60)
    
    

