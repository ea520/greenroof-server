from typing import List, Union, Optional
import datetime
from pydantic import BaseModel

class WeatherBase(BaseModel):
    timestamp: datetime.datetime
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


class SoilMoistureBase(BaseModel):
    timestamp: datetime.datetime
    power_1: Optional[float] = float("nan")
    power_2: Optional[float] = float("nan")
    soil_moisture_01: Optional[float] = float("nan")
    soil_moisture_02: Optional[float] = float("nan")
    soil_moisture_03: Optional[float] = float("nan")
    soil_moisture_04: Optional[float] = float("nan")
    soil_moisture_05: Optional[float] = float("nan")
    soil_moisture_06: Optional[float] = float("nan")
    soil_moisture_07: Optional[float] = float("nan")
    soil_moisture_08: Optional[float] = float("nan")
    soil_moisture_09: Optional[float] = float("nan")
    soil_moisture_10: Optional[float] = float("nan")
    soil_moisture_11: Optional[float] = float("nan")
    soil_moisture_12: Optional[float] = float("nan")
    soil_moisture_13: Optional[float] = float("nan")
    soil_moisture_14: Optional[float] = float("nan")
    soil_moisture_15: Optional[float] = float("nan")
    soil_moisture_16: Optional[float] = float("nan")
    soil_moisture_17: Optional[float] = float("nan")
    soil_moisture_18: Optional[float] = float("nan")
    soil_moisture_19: Optional[float] = float("nan")
    soil_moisture_20: Optional[float] = float("nan")

class SoilMoistureCreate(SoilMoistureBase):
    pass


class SoilMoisture(SoilMoistureBase):
    class Config:
        orm_mode = True


class TemperatureBase(BaseModel):
    timestamp: datetime.datetime
    temperature_01: float
    temperature_02: float
    temperature_03: float
    temperature_04: float
    temperature_05: float
    temperature_06: float
    temperature_07: float
    temperature_08: float
    temperature_09: float
    temperature_10: float
    temperature_11: float
    temperature_12: float
    temperature_13: float
    temperature_14: float
    temperature_15: float
    temperature_16: float
    temperature_17: float
    temperature_18: float


class TemperatureCreate(TemperatureBase):
    pass


class Temperature(TemperatureBase):
    class Config:
        orm_mode = True