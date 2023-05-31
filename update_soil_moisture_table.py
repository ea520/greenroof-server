from SQL_app.models import Base
from SQL_app.models import SoilMoisture
from SQL_app.database import SessionLocal, engine
import datetime
import logging
import parse
import math
import pandas as pd
import tempfile
import glob
import os
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


soil_moisture_1_format = "{timestamp:tg},{power_1:float},{soil_moisture_01:float},{soil_moisture_02:float},{soil_moisture_03:float},{soil_moisture_04:float},{soil_moisture_05:float},{soil_moisture_06:float},{soil_moisture_07:float},{soil_moisture_08:float},{soil_moisture_09:float},{soil_moisture_10:float},{power_2:float},{soil_moisture_11:float},{soil_moisture_12:float},{soil_moisture_13:float},{soil_moisture_14:float},{soil_moisture_15:float},{soil_moisture_16:float},{soil_moisture_17:float},{soil_moisture_18:float},{soil_moisture_19:float},{soil_moisture_20:float}"
compiled_format = parse.compile(soil_moisture_1_format, {"float": parse_float})

latest_stamp = db.query(SoilMoisture.timestamp).order_by(
    SoilMoisture.timestamp.desc()).first()

if latest_stamp is None:
    latest_stamp = datetime.datetime.fromtimestamp(0.)
else:
    latest_stamp = latest_stamp[0]

full_data_stamp = db.query(SoilMoisture.timestamp).order_by(
    SoilMoisture.timestamp.desc()).filter(SoilMoisture.power_1 != None).filter(SoilMoisture.power_2 != None).first()
if full_data_stamp is None:
    full_data_stamp = datetime.datetime.fromtimestamp(0.)
else:
    full_data_stamp = full_data_stamp[0]

files = set(os.path.basename(file) for file in glob.glob(
    "/home/ea520/greenroof-server/soil_moisture1/*.csv"))
files = files.intersection(os.path.basename(file) for file in glob.glob(
    "/home/ea520/greenroof-server/soil_moisture1/*.csv"))
latest_date = f"{full_data_stamp.year}-{full_data_stamp.month:02}-{full_data_stamp.day:02}"
for file in files:
    if file < latest_date:
        continue
    filename1 = "/home/ea520/greenroof-server/soil_moisture1/" + file
    filename2 = "/home/ea520/greenroof-server/soil_moisture2/" + file
    if not os.path.exists(filename1):
        with open(filename1, "w") as f:
            f.write("timestamp,Power,RF-SMC-01,RF-SMC-02,RF-SMC-03,RF-SMC-04,RF-SMC-05,RF-SMC-06,RF-SMC-07,RF-SMC-08,RF-SMC-09,RF-SMC-10")
    if not os.path.exists(filename1):
        with open(filename2, "w") as f:
            f.write("timestamp,Power,RF-SMC-11,RF-SMC-12,RF-SMC-13,RF-SMC-14,RF-SMC-15,RF-SMC-16,RF-SMC-17,RF-SMC-18,RF-SMC-19,RF-SMC-20")

    table1 = pd.read_csv(filename1)
    table2 = pd.read_csv(filename2)
    table1.rename(columns={"Power": "Power1"}, inplace=True)
    table2.rename(columns={"Power": "Power2"}, inplace=True)
    merged = pd.merge(table1, table2, how='outer')

    with tempfile.TemporaryFile("r+") as fp:
        merged.to_csv(fp, index=False, sep=",")
        fp.flush()
        fp.seek(0)
        to_insert = []
        for line in fp:
            line = line.strip("\n")
            parsed = compiled_format.parse(line)
            if parsed is None:
                continue
            if parsed["timestamp"] > latest_stamp:  # most recent time in the table
                to_insert.append(SoilMoisture(**parsed.named))
            # most recent time where no data is null
            elif parsed["timestamp"] > full_data_stamp:
                db.merge(SoilMoisture(**parsed.named))
                logging.log(logging.INFO,
                            f"Soil moisture updated with stamp {parsed['timestamp']}")
                db.commit()
        db.add_all(to_insert)
        if len(to_insert):
            logging.log(logging.INFO,
                        f"Updated {len(to_insert)} soil moistures with latest stamp {to_insert[-1].timestamp}")
        db.commit()
