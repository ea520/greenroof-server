from sqlalchemy.orm import Session, load_only
from . import models, schemas
from .database import Base
import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import insert


# Create an enum of all of the required sensor data for a row in the data table
# This includes the pressure etc. but not datetime
WeatherSensor = Enum("WeatherSensor", ((name, name) for name in schemas.WeatherCreate.schema()["required"] if name!="datetime"))
WaterSensor = Enum("WaterSensor", ((name, name) for name in schemas.WaterLevel1Create.schema()["required"] + schemas.WaterLevel2Create.schema()["required"] if name!="datetime"))

def get_data(db: Session, type: Base,  sensor: Enum, start_time: datetime.datetime, end_time: datetime.datetime, limit: int = 100000):
    ret= db.query(type)\
           .options(load_only("datetime", sensor.name))\
           .filter(type.datetime.between(start_time, end_time))\
           .limit(limit)\
           .all()
    dates = tuple(r.datetime for r in ret)
    measurements = tuple(getattr(r, sensor.name) for r in ret)
    return {"datetimes":dates, sensor.name:measurements}

base_model_to_base = {
    schemas.WeatherCreate: models.Weather,
    schemas.WaterLevel1Create: models.WaterLevel1,
    schemas.WaterLevel2Create: models.WaterLevel2
}

def create_data(db: Session, data: schemas.BaseModel):
    base = base_model_to_base.get(type(data))
    insert(base).values(**data.dict()).on_conflict_do_nothing(index_elements=['datetime'])
    return db