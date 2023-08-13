from sqlalchemy import inspect
from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, models
from .crud import WeatherSensor, MoistureSensor, TemperatureSensor, sensor_units
from .database import SessionLocal, engine

import datetime
import os
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import numpy as np

from fastapi.templating import Jinja2Templates
from enum import Enum
import SQL_app.webpage_metadata.sensor_descriptions
import json
from fastapi.responses import FileResponse
from numbers import Number

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
app.mount("/static", StaticFiles(directory=path + "/static"), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "sensor_descriptions": SQL_app.webpage_metadata.sensor_descriptions.weather_sensor_descriptions,
                                                     "temperature_descriptions": SQL_app.webpage_metadata.sensor_descriptions.temperature_sensor_descriptions,
                                                     "soil_moisture_descriptions": SQL_app.webpage_metadata.sensor_descriptions.soil_moisture_descriptions,
                                                     "title": "index",
                                                     "prefix": "."}
                                      )


@app.get("/temperature", response_class=HTMLResponse, include_in_schema=False)
def temperature(request: Request):
    sensors = [
        OptionTag(f"temperature_{i:02}", "%", f"Sensor {i}") for i in range(1, 18 + 1)]

    return templates.TemplateResponse("historic.html", {"request": request,
                                                        "sensors": sensors,
                                                        "sensor_type": "temperature",
                                                        "title": "Temperature Archive",
                                                        "prefix": "."
                                                        })


@app.get("/weather", response_class=HTMLResponse, include_in_schema=False)
def weather(request: Request):
    sensors = [OptionTag("power", "V", "Data Logger Power"),
               OptionTag("wind_dir", "deg", "Wind Direction"),
               OptionTag("wind_speed", "m/s", "Wind Speed"),
               OptionTag("average_humidity", "%", "Reltaive Humidity"),
               OptionTag("average_diffuse_radiation",
                         "W/m2", "Diffuse Radiation"),
               OptionTag("average_total_radiation", "W/m2", "Total Radiation"),
               OptionTag("rain", "mm@5min", "Rainfall Intensity"),
               OptionTag("average_temp", "deg C", "Temperature"),
               OptionTag("daily_total_evapotranspiration",
                         "mm/day", "Evapotranspiration"),
               ]

    return templates.TemplateResponse("historic.html", {"request": request,
                                                        "sensors": sensors,
                                                        "sensor_type": "weather",
                                                        "title": "Weather Archive",
                                                        "prefix": "."})


@app.get("/moisture", response_class=HTMLResponse, include_in_schema=False)
def read_item(request: Request):
    sensors = [OptionTag("power_1", "V", "Data Logger 1 Power"),
               OptionTag("power_2", "V", "Data Logger 2 Power"),
               ]
    for i in range(1, 20 + 1):
        sensors.append(OptionTag(f"soil_moisture_{i:02}", "%", f"Sensor {i}"))
    return templates.TemplateResponse("historic.html", {"request": request,
                                                        "sensors": sensors,
                                                        "sensor_type": "moisture",
                                                        "title": "Soil Moisture Archive",
                                                        "prefix": "."})


@app.get("/live/temperature", response_class=HTMLResponse, include_in_schema=False)
def read_item(request: Request):
    return templates.TemplateResponse("live-temperature.html", {"request": request,

                                                                "sensor_type": "temperature",
                                                                "title": "Temperature",
                                                                "prefix": ".."})


@app.get("/live/weather", response_class=HTMLResponse, include_in_schema=False)
def read_item(request: Request):
    return templates.TemplateResponse("live-weather.html", {"request": request,

                                                            "sensor_type": "weather",
                                                            "title": "Weather",
                                                            "prefix": ".."})


@app.get("/live/moisture", response_class=HTMLResponse, include_in_schema=False)
def read_item(request: Request):
    return templates.TemplateResponse("live-moisture.html", {"request": request,

                                                             "sensor_type": "moisture",
                                                             "title": "Soil Moisture",
                                                             "prefix": ".."})

# BACKEND


def get_sensor_data(
    q: List[Enum] = Query(),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
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
    db_data = crud.get_data(db, model, q, start_time, end_time)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_data


def dict_to_csv(q: List[Enum], input_dict: dict):
    if (input_dict is not None):
        table = dict()
        table["timestamps"] = input_dict["timestamps"]

        for key in q:
            unit = sensor_units[key]
            unit = unit.replace(
                sensor_units[WeatherSensor.average_temp], "deg C")
            unit = unit.replace(
                sensor_units[WeatherSensor.average_total_radiation], "W/m")
            unit = unit.replace(sensor_units[WeatherSensor.wind_speed], "m/s")
            if len(unit) > 0:
                unit = f" ({unit})"
            table[f"{key.name}{unit}"] = input_dict["measurements"][key.name]
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


def get_sensor_data_csv(q: List[Enum] = Query(),
                        start_time: datetime.datetime = None,
                        end_time: Union[datetime.datetime, None] = None,
                        duration: Union[datetime.timedelta, None] = None,
                        db: Session = Depends(get_db),
                        model: Union[models.Base, None] = None):
    db_data = get_sensor_data(q, start_time, end_time,
                              duration, db, model)
    return dict_to_csv(q, db_data)


@app.get("/API/raw/JSON/weather/")
def get_weather_data(
    q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data(q, start_time, end_time, duration, db, models.Weather)


@app.get("/API/raw/JSON/moisture")
def get_moisture_data(
    q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data(q, start_time, end_time, duration, db, models.SoilMoisture)


@app.get("/API/raw/JSON/temperature")
def get_temperature_data(
    q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data(q, start_time, end_time, duration, db, models.Temperature)


@app.get("/API/raw/CSV/weather")
def get_weather_data_csv(
    q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data_csv(q, start_time, end_time, duration, db, models.Weather)


@app.get("/API/raw/CSV/moisture")
def get_moisture_data_csv(
    q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data_csv(q, start_time, end_time, duration, db, models.SoilMoisture)


@app.get("/API/raw/CSV/temperature")
def get_temperature_data_csv(
    q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
    start_time: datetime.datetime = None,
    end_time: Union[datetime.datetime, None] = None,
    duration: Union[datetime.timedelta, None] = None,
    db: Session = Depends(get_db),
):
    return get_sensor_data_csv(q, start_time, end_time, duration, db, models.Temperature)


def get_latest_measurements(_type: models.Base, q: List[Enum], db: Session = Depends(get_db)):
    # ret = dict(timestamp=datetime.datetime.fromtimestamp(0.))
    ret = dict()
    query_strings = [query.name for query in q]
    for el in inspect(_type).columns:
        if el.name in query_strings:
            val = db.query(_type.timestamp, el).order_by(
                _type.timestamp.desc()).filter(el.isnot(None)).first()
            if val is None:
                open("foo.txt", "w").write(f"{val}, {el.key}")
            ret[el.key] = dict(timestamp=val[0], value=val[1])
    return _type(**ret)


@ app.get("/API/latest/JSON/weather")
def latest_weather(db: Session = Depends(get_db),
                   q: List[WeatherSensor] = Query(default=list(WeatherSensor))):
    return get_latest_measurements(models.Weather, q, db)


@ app.get("/API/latest/JSON/moisture")
def latest_moisture(db: Session = Depends(get_db), q: List[MoistureSensor] = Query(default=list(MoistureSensor))):
    return get_latest_measurements(models.SoilMoisture, q, db)


@ app.get("/API/latest/JSON/temperature")
def latest_temperature(db: Session = Depends(get_db), q: List[TemperatureSensor] = Query(default=list(TemperatureSensor))):
    return get_latest_measurements(models.Temperature, q, db)


def get_weather_by_timestep(
        timestep: str = "H",  # argument to pandas datetime floor
        q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):

    sensor_data = get_sensor_data(
        q, start_time, end_time, duration, db, models.Weather)
    if (len(sensor_data["timestamps"]) == 0):
        return sensor_data
    sensor_dataframe = pd.DataFrame(
        dict(timestamps=sensor_data["timestamps"], **sensor_data["measurements"]))
    wind_directions = None
    if "wind_dir" in sensor_dataframe:
        wind_directions = sensor_dataframe["wind_dir"]
    hour = sensor_dataframe["timestamps"].dt.floor(timestep)
    # result = sensor_dataframe.groupby(hour).mean()
    ret = dict()
    # ret["timestamps"] = list(result[result.keys()[0]].keys())
    ret["measurements"] = dict()

    for key in sensor_dataframe.keys():
        if key == "timestamps":
            filtered = sensor_dataframe[key].groupby(hour).min()
            ret["timestamps"] = filtered.tolist()
            continue
        elif "min" in key:
            filtered = sensor_dataframe[key].groupby(hour).min()
        elif "max" in key:
            filtered = sensor_dataframe[key].groupby(hour).max()
        elif key in ("rain", "evapotranspiration"):
            filtered = sensor_dataframe[key].groupby(hour).sum()
        elif "sunshine" == key:
            filtered = sensor_dataframe[key].groupby(
                hour).agg(lambda x: pd.Series.mode(x)[0])
        elif "wind_dir" == key:
            new_df = pd.DataFrame(dict(timestamps=sensor_data["timestamps"], sines=np.sin(
                np.deg2rad(wind_directions)), cosines=np.cos(np.deg2rad(wind_directions))))
            filtered_sines = new_df["sines"].groupby(hour).mean()
            filtered_cosines = new_df["cosines"].groupby(hour).mean()
            filtered = np.rad2deg(
                np.arctan2(filtered_sines.values, filtered_cosines.values))
            filtered[filtered < 0] += 360.

        else:
            filtered = sensor_dataframe[key].groupby(hour).mean()
        ret["measurements"][key] = [
            None if (isinstance(x, Number) and np.isnan(x)) else x for x in filtered.tolist()]
    return ret


@ app.get("/API/hourly/JSON/weather")
def hourly_weather(
        q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    return get_weather_by_timestep("H", q, start_time, end_time, duration, db)


def get_moisture_by_timestep(
        timestep: str = "H",  # argument to pandas datetime floor
        q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    sensor_data = get_sensor_data(
        q, start_time, end_time, duration, db, models.SoilMoisture)
    if (len(sensor_data["timestamps"]) == 0):
        return sensor_data
    sensor_dataframe = pd.DataFrame(
        dict(timestamps=sensor_data["timestamps"], **sensor_data["measurements"]))
    hour = sensor_dataframe["timestamps"].dt.floor(timestep)
    result = sensor_dataframe.groupby(hour).mean()
    ret = dict()
    ret["timestamps"] = list(result[result.keys()[0]].keys())
    ret["measurements"] = dict()
    for key in result.keys():
        ret["measurements"][key] = list(val if not pd.isna(
            val) else None for val in result[key].values)
    return ret


@ app.get("/API/hourly/JSON/moisture")
def hourly_moisture(
        q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    return get_moisture_by_timestep("H", q, start_time, end_time, duration, db)


def get_temperature_by_timestep(
        timestep: str = "H",  # argument to pandas datetime floor
        q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    sensor_data = get_sensor_data(
        q, start_time, end_time, duration, db, models.Temperature)
    if (len(sensor_data["timestamps"]) == 0):
        return sensor_data
    sensor_dataframe = pd.DataFrame(
        dict(timestamps=sensor_data["timestamps"], **sensor_data["measurements"]))
    hour = sensor_dataframe["timestamps"].dt.floor(timestep)
    result = sensor_dataframe.groupby(hour).mean()
    ret = dict()
    ret["timestamps"] = list(result[result.keys()[0]].keys())
    ret["measurements"] = dict()
    for key in result.keys():
        ret["measurements"][key] = list(val if not pd.isna(
            val) else None for val in result[key].values)
    return ret


@ app.get("/API/hourly/JSON/temperature")
def hourly_temperature(
        q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    return get_temperature_by_timestep("H", q, start_time, end_time, duration, db)


@ app.get("/API/hourly/CSV/weather")
def hourly_weather_CSV(
        q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    hourly_dict = hourly_weather(q, start_time, end_time, duration, db)
    return dict_to_csv(q, hourly_dict)


@ app.get("/API/hourly/CSV/moisture")
def hourly_moisture_CSV(
        q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    hourly_dict = hourly_moisture(q, start_time, end_time, duration, db)
    return dict_to_csv(q, hourly_dict)


@ app.get("/API/hourly/CSV/temperature")
def hourly_temperature_CSV(
        q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    hourly_dict = hourly_temperature(q, start_time, end_time, duration, db)
    return dict_to_csv(q, hourly_dict)


@ app.get("/API/daily/JSON/weather")
def daily_weather(
        q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    return get_weather_by_timestep("D", q, start_time, end_time, duration, db)


@ app.get("/API/daily/JSON/moisture")
def daily_moisture(
        q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    return get_moisture_by_timestep("D", q, start_time, end_time, duration, db)


@ app.get("/API/daily/JSON/temperature")
def daily_temperature(
        q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    return get_temperature_by_timestep("D", q, start_time, end_time, duration, db)


@ app.get("/API/daily/CSV/weather")
def daily_weather_CSV(
        q: List[WeatherSensor] = Query(default=list(WeatherSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    hourly_dict = daily_weather(q, start_time, end_time, duration, db)
    return dict_to_csv(q, hourly_dict)


@ app.get("/API/daily/CSV/moisture")
def daily_moisture_CSV(
        q: List[MoistureSensor] = Query(default=list(MoistureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    hourly_dict = daily_moisture(q, start_time, end_time, duration, db)
    return dict_to_csv(q, hourly_dict)


@ app.get("/API/daily/CSV/temperature")
def daily_temperature_CSV(
        q: List[TemperatureSensor] = Query(default=list(TemperatureSensor)),
        start_time: datetime.datetime = None,
        end_time: Union[datetime.datetime, None] = None,
        duration: Union[datetime.timedelta, None] = None,
        db: Session = Depends(get_db)):
    hourly_dict = daily_temperature(q, start_time, end_time, duration, db)
    return dict_to_csv(q, hourly_dict)
