from sqlalchemy.orm import Session, load_only, deferred
from . import models, schemas
from .database import Base
import datetime
from enum import Enum
from sqlalchemy.dialects.postgresql import insert

# Create an enum of all of the required sensor data for a row in the data table
# This includes the pressure etc. but not datetime
WeatherSensor = Enum(
    "WeatherSensor",
    (
        (name, name)
        for name in schemas.WeatherCreate.schema()["required"]
        if name != "datetime"
    ),
)
WaterSensor = Enum(
    "WaterSensor",
    (
        (name, name)
        for name in schemas.SoilMoisture1Create.schema()["required"]
        + schemas.SoilMoisture2Create.schema()["required"]
        if name != "datetime"
    ),
)


def get_data(
    db: Session,
    _type: Base,
    sensor: Enum,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    nvals: int,
    limit: int = 100000,
):
    ret = (
        db.query(_type)
        .options(load_only(_type.datetime, getattr(_type,sensor.name)))
        .filter(_type.datetime.between(start_time, end_time))
        .limit(limit)
        .all()
    )
    dates = tuple(r.datetime for r in ret)
    measurements = tuple(getattr(r, sensor.name) for r in ret)
    if nvals is not None:
        nmeasurements = len(dates)
        skip = nmeasurements//nvals + 1
        dates = tuple(date for i, date in enumerate(dates) if i % skip == 0)
        measurements = tuple(m for i, m in enumerate(measurements) if i % skip == 0)
    

    return {"datetimes": dates, sensor.name: measurements}


base_model_to_base = {
    schemas.WeatherCreate: models.Weather,
    schemas.SoilMoisture1Create: models.SoilMoisture1,
    schemas.SoilMoisture2Create: models.SoilMoisture2,
}


def create_data(db: Session, data: schemas.BaseModel):
    base = base_model_to_base.get(type(data))
    command = (
        insert(base).values(**data.dict())
        # .on_conflict_do_nothing(index_elements=["datetime"])
    )
    db.merge(base(**data.dict()))
    return db
