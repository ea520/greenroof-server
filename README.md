# Green roof web server
## Creating the database
There is a sqlite database stored [here](./database/sql_app.sqlite)
### The steps required to make a new table for the database are as follows. Using water level sensors as an example.
1. Define the table layout in [this file](./SQL_app/models.py) e.g. 
```python
class WaterLevel(Base):
    __tablename__ = "water_levels"
    timestamp = Column(DateTime, primary_key=True, index=True)
    power = Column(Float)
    water_level1 = Column(Float)
    #...
    water_level10 = Column(Float)
```
2. Create a file e.g. data_parsers/water_level_parser.py.
This file should create a generator that returns the water level in chronological order. If no new data is available, it should yield `None`.
3. Update [this file](update_database.py) using your newly created generator add the new code to the file using `insert_temps` as a reference.
## Using the web API
### Things that likely won't change:
#### When requesting **weather**, the measurements available take the following names:
- power
- pressure
- rain
- sunshine
- wind_dir
- wind_speed
- average_humidity
- max_humidity
- min_humidity
- average_temp
- max_temp
- min_temp
- average_total_radiation
- max_total_radiation
- min_total_radiation
- average_diffuse_radiation
- max_diffuse_radiation
- min_diffuse_radiation
- evapotranspiration
- daily_cumulative_evapotranspiration
- daily_total_evapotranspiration

**Temperature** measurements take the form:
- temperature_01
- ...
- temperature_18

**Soil Moisture** measurements take the form:
- power_1
- power_2
- soil_moisture_01
- ...
- soil_moisture_20

#### Data will be available in JSON and CSV formats

#### There will be an option to obtain the most recent data available

#### There will be an option to obtain all of the data over a specific time interval

### Things that are subject to change

Requests are best exemplified by means of example:

To get all the rain and sunshine data before 2023-01-01, use the following request:

http://csic-server.eng.cam.ac.uk:8001/API/JSON/weather?end_time=2023-01-01T00:00:00&q=rain&q=sunshine

That would return the following JSON object
```json
{
    "timestamps":["2021-11-26T11:50:00","2021-11-26T11:55:00",...],
    "measurements":
    {
        "rain":[0.0,0.0],
        "sunshine":["sun","sun", ...]
    }
}
```

To get 1 day of temperature data in CSV format starting on 2023-01-01, one first needs to calculate 1 day in seconds (86400s). Furthermore, if only 10 measurements are required evenly spaced in the rows of the table, the request is then:

http://csic-server.eng.cam.ac.uk:8001/API/CSV/temperature?start_time=2023-02-01T00:00:00&duration=86400&q=temperature_01&q=temperature_10&cnt=24

That would return the following file:

```
timestamps,temperature_01 (deg C),temperature_10 (deg C)
2023-02-01 00:00:01.571537,20.5,5.562
2023-02-01 02:23:55.726518,20.5,5.437
...
2023-02-01 19:11:05.566047,20.375,4.687
2023-02-01 21:34:50.686465,20.437,4.937
```

To get the most recent soil moisture measurements use
http://csic-server.eng.cam.ac.uk:8001/API/latest/soil

That would return the following JSON object
```json
{
  "timestamp": "2023-03-01T16:40:00",
  "power_1": 10.7,
  "power_2": 10.7,
  "soil_moisture_01": 16.7,
  ...
  "soil_moisture_20": 24.8
}
```
The stamp is the time of the oldest reading (some data may have a more recent stamp).

## Updating the web API
1. Edit [this file](SQL_app/schemas.py) adding e.g.

```python
class WaterLevelBase(BaseModel):
    timestamp: datetime.datetime
    power: float
    water_level1: float
    ...
    water_level10: float
class WaterLevelCreate(WaterLevelBase):
    pass

class WaterLevel(WaterLevelBase):
    class Config:
        orm_mode = True
```
2. ...
## The web app