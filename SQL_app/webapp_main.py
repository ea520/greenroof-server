from sqlalchemy import inspect
from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from . import crud, models
from .crud import WeatherSensor, MoistureSensor, TemperatureSensor, sensor_units
from .database import SessionLocal, engine

import datetime
import os
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from fastapi.templating import Jinja2Templates
from enum import Enum
import SQL_app.webpage_metadata.sensor_descriptions
import SQL_app.webpage_metadata.chart_data
import json
from fastapi.responses import FileResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Green Roof App",
    description=""
)
path = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=path + "/templates")

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class OptionTag:
    def __init__(self, value: str, units: str, text: Union[str, None] = None):
        if text is None:
            text = value.replace("_", " ").capitalize()
        self.value = value
        self.text = text
        self.units = units


# FRONTEND


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "sensor_descriptions": SQL_app.webpage_metadata.sensor_descriptions.weather_sensor_descriptions,
                                                     "temperature_descriptions": SQL_app.webpage_metadata.sensor_descriptions.temperature_sensor_descriptions,
                                                     "soil_moisture_descriptions": SQL_app.webpage_metadata.sensor_descriptions.soil_moisture_descriptions,
                                                     "title": "index",
                                                     "prefix": "."}
                                      )


@app.get("/temperature", response_class=HTMLResponse)
async def temperature(request: Request):
    sensors = [OptionTag(sensor.name, sensor_units[sensor])
               for sensor in TemperatureSensor]
    return templates.TemplateResponse("historic.html", {"request": request,
                                                        "sensors": sensors,
                                                        "sensor_type": "temperature",
                                                        "title": "Temperature Archive",
                                                        "prefix": "."
                                                        })


@app.get("/weather", response_class=HTMLResponse)
async def weather(request: Request):
    sensors = [OptionTag(sensor.name, sensor_units[sensor])
               for sensor in WeatherSensor]

    return templates.TemplateResponse("historic.html", {"request": request,
                                                        "sensors": sensors,
                                                        "sensor_type": "weather",
                                                        "title": "Weather Archive",
                                                        "prefix": "."})


@app.get("/soil", response_class=HTMLResponse)
async def read_item(request: Request):
    sensors = [OptionTag(sensor.name, sensor_units[sensor])
               for sensor in MoistureSensor]
    return templates.TemplateResponse("historic.html", {"request": request,
                                                        "sensors": sensors,
                                                        "sensor_type": "soil",
                                                        "title": "Soil Moisture Archive",
                                                        "prefix": "."})


@app.get("/live/temperature", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("live.html", {"request": request,
                                                    "sensors": SQL_app.webpage_metadata.chart_data.temperature_chart_info.keys(),
                                                    "sensor_type": "temperature",
                                                    "chart_info": json.dumps(SQL_app.webpage_metadata.chart_data.temperature_chart_info),
                                                    "title": "Temperature",
                                                    "prefix": ".."})


@app.get("/live/weather", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("live.html", {"request": request,
                                                    "sensors": SQL_app.webpage_metadata.chart_data.weather_chart_info.keys(),
                                                    "sensor_type": "weather",
                                                    "chart_info": json.dumps(SQL_app.webpage_metadata.chart_data.weather_chart_info),
                                                    "title": "Weather",
                                                    "prefix": ".."})


@app.get("/live/soil", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("live.html", {"request": request,
                                                    "sensors": SQL_app.webpage_metadata.chart_data.soil_moisture_chart_info.keys(),
                                                    "sensor_type": "soil",
                                                    "chart_info": json.dumps(SQL_app.webpage_metadata.chart_data.soil_moisture_chart_info),
                                                    "title": "Soil Moisture",
                                                    "prefix": ".."})


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("SQL_app/static/favicon.ico")


# BACKEND


def get_sensor_data(
    q: List[Enum] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
    model: Union[models.Base, None] = None
):
    # go through error cases
    all_none = duration is start_time is end_time is None
    all_set = duration is not None and start_time is not None and end_time is not None
    if all_none:
        raise HTTPException(
            status_code=400, detail="Time period is under-specified")
    elif all_set:
        raise HTTPException(
            status_code=400, detail="Time period is over-specified")
    # valid cases
    elif start_time is None and end_time is None:
        end_time = datetime.datetime.now()
        start_time = end_time - duration

    elif end_time is None:
        if duration is not None:
            end_time = start_time + duration
        else:
            end_time = datetime.datetime.now()

    elif start_time is None:
        if duration is not None:
            start_time = end_time - duration
        else:
            start_time = datetime.datetime.fromtimestamp(0.)

    db_data = crud.get_data(db, model, q, start_time, end_time, cnt)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_data


def get_sensor_data_csv(q: List[Enum] = Query(),
                        start_time: datetime.datetime = None,
                        end_time: Union[datetime.datetime, None] = None,
                        duration: Union[datetime.timedelta, None] = None,
                        cnt: Union[int, None] = None,
                        db: Session = Depends(get_db),
                        model: Union[models.Base, None] = None):
    db_data = get_sensor_data(q, start_time, end_time,
                              duration, cnt, db, model)
    if (db_data is not None):
        table = dict()
        table["timestamps"] = db_data["timestamps"]

        for key in q:
            unit = sensor_units[key]
            unit = unit.replace(
                sensor_units[WeatherSensor.average_temp], "deg C")
            unit = unit.replace(
                sensor_units[WeatherSensor.average_total_radiation], "W/m")
            unit = unit.replace(sensor_units[WeatherSensor.wind_speed], "m/s")
            table[f"{key.name} ({unit})"] = db_data["measurements"][key.name]
        df = pd.DataFrame.from_dict(table)
        df["timestamps"] = pd.to_datetime(df["timestamps"])
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(
            iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=data.csv"
        return response
    else:
        raise HTTPException(status_code=404, detail="Data not found")


@app.get("/API/JSON/weather/")
async def get_weather_data(
    q: List[WeatherSensor] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data(q, start_time, end_time, duration, cnt, db, models.Weather)


@app.get("/API/JSON/soil")
async def get_soil_data(
    q: List[MoistureSensor] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data(q, start_time, end_time, duration, cnt, db, models.SoilMoisture)


@app.get("/API/JSON/temperature")
async def get_temperature_data(
    q: List[TemperatureSensor] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data(q, start_time, end_time, duration, cnt, db, models.Temperature)


@app.get("/API/CSV/weather")
async def get_weather_data_csv(
    q: List[WeatherSensor] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data_csv(q, start_time, end_time, duration, cnt, db, models.Weather)


@app.get("/API/CSV/soil")
async def get_soil_data_csv(
    q: List[MoistureSensor] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data_csv(q, start_time, end_time, duration, cnt, db, models.SoilMoisture)


@app.get("/API/CSV/temperature")
async def get_temperature_data_csv(
    q: List[TemperatureSensor] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    cnt: Union[int, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data_csv(q, start_time, end_time, duration, cnt, db, models.Temperature)


def get_latest_measurements(_type: models.Base, db: Session = Depends(get_db)):
    ret = dict(timestamp=datetime.datetime.fromtimestamp(0.))
    for el in inspect(_type).columns:
        val = db.query(_type.timestamp, el).order_by(
            _type.timestamp.desc()).filter(el != None).first()
        ret[el.key] = val[1]
    return _type(**ret)


@app.get("/API/latest/weather")
async def latest_weather(db: Session = Depends(get_db)):
    return get_latest_measurements(models.Weather, db)


@app.get("/API/latest/soil")
async def latest_soil(db: Session = Depends(get_db)):
    return get_latest_measurements(models.SoilMoisture, db)


@app.get("/API/latest/temperature")
async def latest_temperature(db: Session = Depends(get_db)):
    return get_latest_measurements(models.Temperature, db)
