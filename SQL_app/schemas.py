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



class WaterLevel1Base(BaseModel):
    datetime: datetime.datetime
    power1: float
    water_content01: float
    water_content02: float
    water_content03: float
    water_content04: float
    water_content05: float
    water_content06: float
    water_content07: float
    water_content08: float
    water_content09: float
    water_content10: float

class WaterLevel1Create(WaterLevel1Base):
    pass

class WaterLevel1(WaterLevel1Base):
    class Config:
        orm_mode = True


class WaterLevel2Base(BaseModel):
    datetime: datetime.datetime
    power2: float
    water_content11: float
    water_content12: float
    water_content13: float
    water_content14: float
    water_content15: float
    water_content16: float
    water_content17: float
    water_content18: float
    water_content19: float
    water_content20: float

class WaterLevel2Create(WaterLevel2Base):
    pass

class WaterLevel2(WaterLevel2Base):
    class Config:
        orm_mode = True
