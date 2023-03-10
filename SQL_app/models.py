from sqlalchemy import  Column, String, Float, DateTime
from .database import Base


class Weather(Base):
    __tablename__ = "weather"
    timestamp = Column(DateTime, primary_key=True, index=True)
    power = Column(Float)
    pressure = Column(Float)
    rain = Column(Float)
    sunshine = Column(String)
    wind_dir = Column(Float)
    wind_speed = Column(Float)
    average_humidity = Column(Float)
    max_humidity = Column(Float)
    min_humidity = Column(Float)
    average_temp = Column(Float)
    max_temp = Column(Float)
    min_temp = Column(Float)
    average_total_radiation = Column(Float)
    max_total_radiation = Column(Float)
    min_total_radiation = Column(Float)
    average_diffuse_radiation = Column(Float)
    max_diffuse_radiation = Column(Float)
    min_diffuse_radiation = Column(Float)
    evapotranspiration = Column(Float)
    daily_cumulative_evapotranspiration = Column(Float)
    daily_total_evapotranspiration = Column(Float)


class SoilMoisture(Base):
    __tablename__ = "soil_moisture"
    timestamp = Column(DateTime, primary_key=True, index=True)
    power_1 = Column(Float)
    power_2 = Column(Float)
    soil_moisture_01 = Column(Float)
    soil_moisture_02 = Column(Float)
    soil_moisture_03 = Column(Float)
    soil_moisture_04 = Column(Float)
    soil_moisture_05 = Column(Float)
    soil_moisture_06 = Column(Float)
    soil_moisture_07 = Column(Float)
    soil_moisture_08 = Column(Float)
    soil_moisture_09 = Column(Float)
    soil_moisture_10 = Column(Float)
    soil_moisture_11 = Column(Float)
    soil_moisture_12 = Column(Float)
    soil_moisture_13 = Column(Float)
    soil_moisture_14 = Column(Float)
    soil_moisture_15 = Column(Float)
    soil_moisture_16 = Column(Float)
    soil_moisture_17 = Column(Float)
    soil_moisture_18 = Column(Float)
    soil_moisture_19 = Column(Float)
    soil_moisture_20 = Column(Float)


class Temperature(Base):
    __tablename__ = "temperature"
    timestamp = Column(DateTime, primary_key=True, index=True)
    temperature_01 = Column(Float)
    temperature_02 = Column(Float)
    temperature_03 = Column(Float)
    temperature_04 = Column(Float)
    temperature_05 = Column(Float)
    temperature_06 = Column(Float)
    temperature_07 = Column(Float)
    temperature_08 = Column(Float)
    temperature_09 = Column(Float)
    temperature_10 = Column(Float)
    temperature_11 = Column(Float)
    temperature_12 = Column(Float)
    temperature_13 = Column(Float)
    temperature_14 = Column(Float)
    temperature_15 = Column(Float)
    temperature_16 = Column(Float)
    temperature_17 = Column(Float)
    temperature_18 = Column(Float)