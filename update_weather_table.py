from SQL_app.models import Base
from SQL_app.models import Weather
from SQL_app.database import SessionLocal, engine
import datetime
import logging
import glob
import os
import parse
import math
logging.basicConfig(filename='/home/ea520/greenroof-server/logs/update_database.log',
                    format='%(asctime)s %(message)s', level=logging.INFO)
Base.metadata.create_all(bind=engine)
db = SessionLocal()


@parse.with_pattern(r"[^,]*")  # 0 or more non-whitespace characters
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan


stamp = db.query(Weather.timestamp).order_by(
    Weather.timestamp.desc()).first()
if stamp is None:
    stamp = datetime.datetime.fromtimestamp(0.)
else:
    stamp = stamp[0]

weather_files = glob.glob("/home/ea520/greenroof-server/weather/*.csv")
latest_date = f"{stamp.year}-{stamp.month:02}-{stamp.day:02}"
reamining_files = [
    file for file in weather_files if os.path.basename(file) > latest_date]


for file in reamining_files:
    weather_format = "{timestamp:tg},{power:float},{pressure:float},{rain:float},{sunshine},{wind_dir:float},{wind_speed:float},{average_humidity:float},{max_humidity:float},{min_humidity:float},{average_temp:float},{max_temp:float},{min_temp:float},{average_total_radiation:float},{max_total_radiation:float},{min_total_radiation:float},{average_diffuse_radiation:float},{max_diffuse_radiation:float},{min_diffuse_radiation:float},{evapotranspiration:float},{daily_cumulative_evapotranspiration:float},{daily_total_evapotranspiration:float}"
    compiled_format = parse.compile(weather_format, {"float": parse_float})
    lines = [line.strip("\n") for line in open(file).readlines()[2:]]
    parsed_lines = [compiled_format.parse(line) for line in lines]
    to_insert = []
    for line in parsed_lines:
        if line is not None and line["timestamp"] > stamp:
            to_insert.append(Weather(**line.named))
    db.add_all(to_insert)
    if len(to_insert):
        logging.log(logging.INFO,
                    f"Weather updated with stamp {to_insert[-1].timestamp}")
    db.commit()
