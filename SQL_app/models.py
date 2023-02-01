from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Weather(Base):
    __tablename__ = "weather"
    # id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime,primary_key=True, index=True)
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


class WaterLevel1(Base):
    __tablename__ = "waterlevel1"
    # id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime,primary_key=True, index=True)
    power1 = Column(Float)
    water_content01 = Column(Float)
    water_content02 = Column(Float)
    water_content03 = Column(Float)
    water_content04 = Column(Float)
    water_content05 = Column(Float)
    water_content06 = Column(Float)
    water_content07 = Column(Float)
    water_content08 = Column(Float)
    water_content09 = Column(Float)
    water_content10 = Column(Float)

class WaterLevel2(Base):
    __tablename__ = "waterlevel2"
    # id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime,primary_key=True, index=True)
    power2 = Column(Float)
    water_content11 = Column(Float)
    water_content12 = Column(Float)
    water_content13 = Column(Float)
    water_content14 = Column(Float)
    water_content15 = Column(Float)
    water_content16 = Column(Float)
    water_content17 = Column(Float)
    water_content18 = Column(Float)
    water_content19 = Column(Float)
    water_content20 = Column(Float)