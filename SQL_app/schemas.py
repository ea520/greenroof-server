from typing import List, Union
import datetime
from pydantic import BaseModel


class WeatherBase(BaseModel):
    datetime: datetime.datetime
    power: float
    pressure: float
    rain: float
    sunshine: str
    wind_dir: float
    wind_speed: float
    average_humidity: float
    max_humidity: float
    min_humidity: float
    average_temp: float
    max_temp: float
    min_temp: float
    average_total_radiation: float
    max_total_radiation: float
    min_total_radiation: float
    average_diffuse_radiation: float
    max_diffuse_radiation: float
    min_diffuse_radiation: float
    evapotranspiration: float
    daily_cumulative_evapotranspiration: float
    daily_total_evapotranspiration: float


class WeatherCreate(WeatherBase):
    pass


class Weather(WeatherBase):
    class Config:
        orm_mode = True


class SoilMoisture1Base(BaseModel):
    datetime: datetime.datetime
    power1: float
    soil_moisture01: float
    soil_moisture02: float
    soil_moisture03: float
    soil_moisture04: float
    soil_moisture05: float
    soil_moisture06: float
    soil_moisture07: float
    soil_moisture08: float
    soil_moisture09: float
    soil_moisture10: float


class SoilMoisture1Create(SoilMoisture1Base):
    pass


class SoilMoisture1(SoilMoisture1Base):
    class Config:
        orm_mode = True


class SoilMoisture2Base(BaseModel):
    datetime: datetime.datetime
    power2: float
    soil_moisture11: float
    soil_moisture12: float
    soil_moisture13: float
    soil_moisture14: float
    soil_moisture15: float
    soil_moisture16: float
    soil_moisture17: float
    soil_moisture18: float
    soil_moisture19: float
    soil_moisture20: float


class SoilMoisture2Create(SoilMoisture2Base):
    pass


class SoilMoisture2(SoilMoisture2Base):
    class Config:
        orm_mode = True
