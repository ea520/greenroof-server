from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Weather(Base):
    __tablename__ = "weather"
    # id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, primary_key=True, index=True)
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


class SoilMoisture1(Base):
    __tablename__ = "soil_moisture1"
    datetime = Column(DateTime, primary_key=True, index=True)
    power1 = Column(Float)
    soil_moisture01 = Column(Float)
    soil_moisture02 = Column(Float)
    soil_moisture03 = Column(Float)
    soil_moisture04 = Column(Float)
    soil_moisture05 = Column(Float)
    soil_moisture06 = Column(Float)
    soil_moisture07 = Column(Float)
    soil_moisture08 = Column(Float)
    soil_moisture09 = Column(Float)
    soil_moisture10 = Column(Float)


class SoilMoisture2(Base):
    __tablename__ = "soil_moisture2"
    datetime = Column(DateTime, primary_key=True, index=True)
    power2 = Column(Float)
    soil_moisture11 = Column(Float)
    soil_moisture12 = Column(Float)
    soil_moisture13 = Column(Float)
    soil_moisture14 = Column(Float)
    soil_moisture15 = Column(Float)
    soil_moisture16 = Column(Float)
    soil_moisture17 = Column(Float)
    soil_moisture18 = Column(Float)
    soil_moisture19 = Column(Float)
    soil_moisture20 = Column(Float)
