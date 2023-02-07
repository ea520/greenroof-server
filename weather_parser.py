"""
Every 5 mins, read the last few lines of the 
"""

import parse
import math
import time
import threading
from SQL_app.models import Base
from SQL_app.crud import create_data, base_model_to_base
from SQL_app.schemas import WeatherCreate, SoilMoisture1Create, SoilMoisture2Create
from SQL_app.database import SessionLocal, engine
from sqlalchemy.sql.expression import desc

# import paramiko.client
# import paramiko.ssh_exception
import time
import parse
import datetime
import pydantic
import sys
import linecache
from tqdm import tqdm
import logging
logging.basicConfig(
    filename='weather_parsing.log', 
    level=logging.DEBUG, 
    datefmt="[%Y-%m-%d %H:%M:%S]",
    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',)
FILENAMES = [
    "/home/ea520/greenroof-server/database/weather",
    "/home/ea520/greenroof-server/database/soil_moisture1",
    "/home/ea520/greenroof-server/database/soil_moisture2",
]


@parse.with_pattern(r"[^\s\\]*")  # at least 0 or more non-whitespace characters
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan


weather_format = "{datetime:tg}\t{power:float}\t{pressure:float}\t{rain:float}\t{sunshine}\t{wind_dir:float}\t{wind_speed:float}\t{average_humidity:float}\t{max_humidity:float}\t{min_humidity:float}\t{average_temp:float}\t{max_temp:float}\t{min_temp:float}\t{average_total_radiation:float}\t{max_total_radiation:float}\t{min_total_radiation:float}\t{average_diffuse_radiation:float}\t{max_diffuse_radiation:float}\t{min_diffuse_radiation:float}\t{evapotranspiration:float}\t{daily_cumulative_evapotranspiration:float}\t{daily_total_evapotranspiration:float}"
soil_moisture_1_format = "{datetime:tg}\t{power1:float}\t{soil_moisture01:float}\t{soil_moisture02:float}\t{soil_moisture03:float}\t{soil_moisture04:float}\t{soil_moisture05:float}\t{soil_moisture06:float}\t{soil_moisture07:float}\t{soil_moisture08:float}\t{soil_moisture09:float}\t{soil_moisture10:float}"
soil_moisture_2_format = "{datetime:tg}\t{power2:float}\t{soil_moisture11:float}\t{soil_moisture12:float}\t{soil_moisture13:float}\t{soil_moisture14:float}\t{soil_moisture15:float}\t{soil_moisture16:float}\t{soil_moisture17:float}\t{soil_moisture18:float}\t{soil_moisture19:float}\t{soil_moisture20:float}"

parsed_weather_format = parse.compile(weather_format, {"float": parse_float})
parsed_soil_moisture_1_format = parse.compile(
    soil_moisture_1_format, {"float": parse_float}
)
parsed_soil_moisture_2_format = parse.compile(
    soil_moisture_2_format, {"float": parse_float}
)


def insert_line(db, datatype: pydantic.BaseModel, line: str):
    data = format.parse(line)
    if data is not None:
        create_data(db, datatype(**data.named))
        return True
    return False


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    PARSED_FORMATS = [
        parsed_weather_format,
        parsed_soil_moisture_1_format,
        parsed_soil_moisture_2_format,
    ]
    DATATYPES = [WeatherCreate, SoilMoisture1Create, SoilMoisture2Create]
    while True:
        for filename, format, datatype in zip(FILENAMES, PARSED_FORMATS, DATATYPES):
            line_count = 0
            # Find the most recent date in the database
            latest_time_in_dataset = datetime.datetime(1970, 1, 1)
            try:
                latest_time_in_dataset = (
                    db.query(base_model_to_base.get(datatype))
                    .order_by(desc("datetime"))
                    .first()
                    .datetime
                )
            except AttributeError as e:
                logging.warning(str(e)+"\n\tProbably means the dataset hasn't been initialised.")

            line_count = sum(1 for line in open(filename))

            new_data = []
            # Loop through lines in the file starting at the end
            linecache.checkcache()
            table_name = base_model_to_base.get(datatype).__tablename__
            for n in range(line_count, 0, -1):
                line = (
                    linecache.getline(filename, n).replace("\r", "").replace("\n", "")
                )

                # Parse it
                data = format.parse(line)
                if data is None:
                    logging.warning(f"Couldn't parse line {n} of '{filename}':\n\t" + line)
                else:
                    print(f"Reading {table_name} data from", data["datetime"], end="\r")
                    # If it's newer than any data in the database, add it to a list of new data
                    if data["datetime"] > latest_time_in_dataset:
                        new_data.append(datatype(**data.named))
                    # Otherwise, you can finish reading the file line by line
                    else:
                        break
            # Add them to the database in chronological order
            for i, new_datum in tqdm(enumerate(reversed(new_data)), desc=f"Adding the new {table_name} data to the database", total=len(new_data), leave=None, position=0):
                create_data(db, new_datum)
                if i > 0 and not i % 1000:
                    db.commit()
            db.commit()
        time.sleep(5*60)
