import math
from sqlalchemy.orm import Session, load_only, deferred
from . import models, schemas
from .database import Base
import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import insert

# Create an enum of all of the required sensor data for a row in the data table
# This includes the pressure etc. but not timestamp

WeatherSensor = Enum(
    "WeatherSensor",
    (
        (name, name)
        for name in schemas.WeatherCreate.__fields__.keys()
        if name != "timestamp"
    ),
)
MoistureSensor = Enum(
    "MoistureSensor",
    (
        (name, name)
        for name in schemas.SoilMoistureCreate.__fields__.keys()
        if name != "timestamp"
    ),
)

TemperatureSensor = Enum(
    "TemperatureSensor",
    (
        (name, name)
        for name in schemas.TemperatureCreate.__fields__.keys()
        if name != "timestamp"
    ),
)

sensor_units = {
    WeatherSensor.power: "V",
    WeatherSensor.pressure: "hPa",
    WeatherSensor.rain: "mm/5mins",
    WeatherSensor.sunshine: "",
    WeatherSensor.wind_dir: "deg",
    WeatherSensor.wind_speed: "m s" + chr(0x207B) + chr(0x00B9),
    WeatherSensor.average_humidity: "%",
    WeatherSensor.max_humidity: "%",
    WeatherSensor.min_humidity: "%",
    WeatherSensor.average_temp: chr(0x2103),
    WeatherSensor.max_temp: chr(0x2103),
    WeatherSensor.min_temp: chr(0x2103),
    WeatherSensor.average_total_radiation: "W m" + chr(0x207B) + chr(0x00B2),
    WeatherSensor.max_total_radiation: "W m" + chr(0x207B) + chr(0x00B2),
    WeatherSensor.min_total_radiation: "W m" + chr(0x207B) + chr(0x00B2),
    WeatherSensor.average_diffuse_radiation: "W m" + chr(0x207B) + chr(0x00B2),
    WeatherSensor.max_diffuse_radiation: "W m" + chr(0x207B) + chr(0x00B2),
    WeatherSensor.min_diffuse_radiation: "W m" + chr(0x207B) + chr(0x00B2),
    WeatherSensor.evapotranspiration: "mm/hr",
    WeatherSensor.daily_cumulative_evapotranspiration: "mm",
    WeatherSensor.daily_total_evapotranspiration: "mm/day",

    MoistureSensor.power_1: "V",
    MoistureSensor.power_2: "V",
    MoistureSensor.soil_moisture_01: "%",
    MoistureSensor.soil_moisture_02: "%",
    MoistureSensor.soil_moisture_03: "%",
    MoistureSensor.soil_moisture_04: "%",
    MoistureSensor.soil_moisture_05: "%",
    MoistureSensor.soil_moisture_06: "%",
    MoistureSensor.soil_moisture_07: "%",
    MoistureSensor.soil_moisture_08: "%",
    MoistureSensor.soil_moisture_09: "%",
    MoistureSensor.soil_moisture_10: "%",
    MoistureSensor.soil_moisture_11: "%",
    MoistureSensor.soil_moisture_12: "%",
    MoistureSensor.soil_moisture_13: "%",
    MoistureSensor.soil_moisture_14: "%",
    MoistureSensor.soil_moisture_15: "%",
    MoistureSensor.soil_moisture_16: "%",
    MoistureSensor.soil_moisture_17: "%",
    MoistureSensor.soil_moisture_18: "%",
    MoistureSensor.soil_moisture_19: "%",
    MoistureSensor.soil_moisture_20: "%",

    TemperatureSensor.temperature_01: chr(0x2103),
    TemperatureSensor.temperature_02: chr(0x2103),
    TemperatureSensor.temperature_03: chr(0x2103),
    TemperatureSensor.temperature_04: chr(0x2103),
    TemperatureSensor.temperature_05: chr(0x2103),
    TemperatureSensor.temperature_06: chr(0x2103),
    TemperatureSensor.temperature_07: chr(0x2103),
    TemperatureSensor.temperature_08: chr(0x2103),
    TemperatureSensor.temperature_09: chr(0x2103),
    TemperatureSensor.temperature_10: chr(0x2103),
    TemperatureSensor.temperature_11: chr(0x2103),
    TemperatureSensor.temperature_12: chr(0x2103),
    TemperatureSensor.temperature_13: chr(0x2103),
    TemperatureSensor.temperature_14: chr(0x2103),
    TemperatureSensor.temperature_15: chr(0x2103),
    TemperatureSensor.temperature_16: chr(0x2103),
    TemperatureSensor.temperature_17: chr(0x2103),
    TemperatureSensor.temperature_18: chr(0x2103),
}


def get_data(
    db: Session,
    _type: Base,
    sensors: Enum,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    cnt: int,
):
    ret = (
        db.query(_type)
        .options(load_only(_type.timestamp, *(getattr(_type, sensor.name) for sensor in sensors)))
        .filter(_type.timestamp.between(start_time, end_time))
        .all()
    )
    dates = list(r.timestamp for r in ret)
    measurements = dict((sensor.name, list(getattr(r, sensor.name)
                        for r in ret)) for sensor in sensors)
    # measurements["wind_dir"] is a list of all the wind directions
    ret = dict()
    ret["timestamps"] = dates
    ret["measurements"] = measurements
    if cnt is not None:
        num_measurements = len(dates)
        skip = num_measurements//cnt + 1
        ret["timestamps"] = ret["timestamps"][::skip]
        for key in ret["measurements"]:
            ret["measurements"][key] = ret["measurements"][key][::skip]
    return ret


base_model_to_base = {
    schemas.WeatherCreate: models.Weather,
    schemas.SoilMoistureCreate: models.SoilMoisture,
    schemas.TemperatureCreate: models.Temperature,
}


def create_data(db: Session, data: schemas.BaseModel):
    base = base_model_to_base.get(type(data))
    old_data = db.query(base).filter(base.timestamp == data.timestamp).first()
    if (old_data is None):
        old_data = base(timestamp=data.timestamp)
    new_data = data.dict()
    for key in new_data:
        if (isinstance(new_data[key], float) and not math.isnan(new_data[key])):
            setattr(old_data, key, new_data[key])
        elif (isinstance(new_data[key], str)):
            setattr(old_data, key, new_data[key])

    db.merge(old_data)
    return db
