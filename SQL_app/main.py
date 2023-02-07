from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import WeatherSensor, WaterSensor
from .database import SessionLocal, engine

import datetime
import os
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
import pandas as pd
import io

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
path = os.path.dirname(os.path.abspath(__file__))

weather_webpage = open(path + "/html/weather.html").read()
soil_webpage = open(path + "/html/soil.html").read()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/greenroof/weather/{sensor}")
async def read_data(
    sensor: WeatherSensor,
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    if start_time is None and end_time is None:
        end_time = datetime.datetime.now()
        start_time = end_time - duration

    elif end_time is None:
        end_time = start_time + duration

    elif start_time is None:
        start_time = end_time - duration

    db_data = crud.get_data(db, models.Weather, sensor, start_time, end_time)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_data


@app.get("/greenroof/soil/{sensor}")
async def read_data(
    sensor: WaterSensor,
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    nvals: Union[int, None] = None,
    db: Session = Depends(get_db),
):

    if start_time is None and end_time is None:
        end_time = datetime.datetime.now()
        start_time = end_time - duration

    elif end_time is None:
        end_time = start_time + duration

    elif start_time is None:
        start_time = end_time - duration

    _type = (
        models.SoilMoisture1
        if sensor.name in schemas.SoilMoisture1Create.schema()["required"]
        else models.SoilMoisture2
    )
    db_data = crud.get_data(db, _type, sensor, start_time, end_time, nvals)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_data

@app.get("/greenroof/soil/{sensor}/csv")
async def read_data(
    sensor: WaterSensor,
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    nvals: Union[int, None] = None,
    db: Session = Depends(get_db),
):

    if start_time is None and end_time is None:
        end_time = datetime.datetime.now()
        start_time = end_time - duration

    elif end_time is None:
        end_time = start_time + duration

    elif start_time is None:
        start_time = end_time - duration

    _type = (
        models.SoilMoisture1
        if sensor.name in schemas.SoilMoisture1Create.schema()["required"]
        else models.SoilMoisture2
    )
    db_data = crud.get_data(db, _type, sensor, start_time, end_time, nvals)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    
    df = pd.DataFrame.from_dict(db_data)
    stream = io.StringIO()
    df.to_csv(stream, index = False)
    response = StreamingResponse(iter([stream.getvalue()]),media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response

@app.get("/greenroof/weather/", response_class=HTMLResponse)
async def read_item():
    return weather_webpage


@app.get("/greenroof/soil/", response_class=HTMLResponse)
async def read_item():
    return soil_webpage


@app.get("/greenroof/latest-date/weather")
async def read_data(db: Session = Depends(get_db)):
    dt = (
        db.query(models.Weather)
        .order_by(models.Weather.datetime.desc())
        .first()
        .datetime
    )
    return dt


@app.get("/greenroof/latest-date/soil")
async def read_data(db: Session = Depends(get_db)):
    dt1 = (
        db.query(models.SoilMoisture1)
        .order_by(models.SoilMoisture1.datetime.desc())
        .first()
        .datetime
    )
    dt2 = (
        db.query(models.SoilMoisture2)
        .order_by(models.SoilMoisture2.datetime.desc())
        .first()
        .datetime
    )
    return min(dt1, dt2)

@app.get("/greenroof/latest-date/soil")
async def read_data(db: Session = Depends(get_db)):
    dt1 = (
        db.query(models.SoilMoisture1)
        .order_by(models.SoilMoisture1.datetime.desc())
        .first()
        .datetime
    )
    dt2 = (
        db.query(models.SoilMoisture2)
        .order_by(models.SoilMoisture2.datetime.desc())
        .first()
        .datetime
    )
    return min(dt1, dt2)

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = path+"/html/favicon.ico"
    return FileResponse(favicon_path)