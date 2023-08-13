from SQL_app.models import Base
from SQL_app.models import SoilMoisture
from SQL_app.database import SessionLocal, engine
import datetime
import logging
import logging.handlers
import parse
import math
import pandas as pd
import tempfile
import glob
import os
base = os.path.dirname(os.path.abspath(__file__))
logfile = base + "/logs/update_database.log"
logging.basicConfig(filename=logfile,
                    format='%(asctime)s %(message)s', level=logging.INFO)
handler = logging.handlers.RotatingFileHandler(logfile, mode='a', maxBytes=1 * 1024 * 1024,
                                               backupCount=5, encoding=None, delay=False)
logger = logging.getLogger().addHandler(handler)
Base.metadata.create_all(bind=engine)
db = SessionLocal()


@parse.with_pattern(r"[^,]*")  # 0 or more non-whitespace characters
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF" but don't bother checking
        return math.nan


# define the format of a line of data
soil_moisture_1_format = "{timestamp:tg},{power_1:float},{soil_moisture_01:float},{soil_moisture_02:float},{soil_moisture_03:float},{soil_moisture_04:float},{soil_moisture_05:float},{soil_moisture_06:float},{soil_moisture_07:float},{soil_moisture_08:float},{soil_moisture_09:float},{soil_moisture_10:float},{power_2:float},{soil_moisture_11:float},{soil_moisture_12:float},{soil_moisture_13:float},{soil_moisture_14:float},{soil_moisture_15:float},{soil_moisture_16:float},{soil_moisture_17:float},{soil_moisture_18:float},{soil_moisture_19:float},{soil_moisture_20:float}"
compiled_format = parse.compile(soil_moisture_1_format, {"float": parse_float})

# the most recent time stamp in the database
latest_stamp = db.query(SoilMoisture.timestamp).order_by(
    SoilMoisture.timestamp.desc()).first()

# if the database is empty, make the latest timestamp 1970-01-01
if latest_stamp is None:
    latest_stamp = datetime.datetime.fromtimestamp(0.)
else:
    latest_stamp = latest_stamp[0]

# soil moisture comes from 2 dataloggers which aren't necessarily in sync so the data at most recent timestamp
# may contain several "nulls" where half of the data is yet to come
# the timestamp where both rows contain all the data is therefore of interest.
full_data_stamp = db.query(SoilMoisture.timestamp).order_by(
    SoilMoisture.timestamp.desc()).filter(SoilMoisture.power_1 != None).filter(SoilMoisture.power_2 != None).first()
if full_data_stamp is None:
    full_data_stamp = datetime.datetime.fromtimestamp(0.)
else:
    full_data_stamp = full_data_stamp[0]

# find the the intersection of the 2 sets of files (files in both folders with the same basename)
files = set(os.path.basename(file) for file in glob.glob(
    "/home/nrfis/Documents/blue_roof/soil_moisture/daily1/*.csv"))
files = files.intersection(os.path.basename(file) for file in glob.glob(
    "/home/nrfis/Documents/blue_roof/soil_moisture/daily2/*.csv"))
# a string representation of the most recent date in the database where all the data is there
latest_date = f"{full_data_stamp.year}-{full_data_stamp.month:02}-{full_data_stamp.day:02}"
# sort the filenames
files = sorted(list(files))
for file in files:
    if file < latest_date:
        # these files have already been parsed and put in the database
        continue
    filename1 = "/home/nrfis/Documents/blue_roof/soil_moisture/daily1/" + file
    filename2 = "/home/nrfis/Documents/blue_roof/soil_moisture/daily2/" + file
    # I don't think this case should exist but just in case
    if not os.path.exists(filename1):
        with open(filename1, "w") as f:
            f.write("timestamp,Power,RF-SMC-01,RF-SMC-02,RF-SMC-03,RF-SMC-04,RF-SMC-05,RF-SMC-06,RF-SMC-07,RF-SMC-08,RF-SMC-09,RF-SMC-10")
    if not os.path.exists(filename1):
        with open(filename2, "w") as f:
            f.write("timestamp,Power,RF-SMC-11,RF-SMC-12,RF-SMC-13,RF-SMC-14,RF-SMC-15,RF-SMC-16,RF-SMC-17,RF-SMC-18,RF-SMC-19,RF-SMC-20")

    # make a merged database of the data from the 2 files
    table1 = pd.read_csv(filename1)
    table2 = pd.read_csv(filename2)
    table1.rename(columns={"Power": "Power1"}, inplace=True)
    table2.rename(columns={"Power": "Power2"}, inplace=True)
    merged = pd.merge(table1, table2, how='outer')

    with tempfile.TemporaryFile("r+") as fp:
        merged.to_csv(fp, index=False, sep=",")
        # write this pandas database into a temporary file
        fp.flush()
        fp.seek(0)
        to_insert = []
        for line in fp:
            line = line.strip("\n")
            # parse the line
            parsed = compiled_format.parse(line)
            if parsed is None:
                # failed to parse
                continue
            if parsed["timestamp"] > latest_stamp:  # most recent time in the table
                to_insert.append(SoilMoisture(**parsed.named))

            # most recent time where no data is null
            elif parsed["timestamp"] > full_data_stamp:
                # update the database with the rest of the data added to the row
                old_data = db.query(SoilMoisture).filter(
                    SoilMoisture.timestamp == parsed["timestamp"]).first()
                fields = [f"soil_moisture_{i:02}" for i in range(
                    1, 20 + 1)] + ["power_1", "power_2"]
                for field in fields:
                    old_value = getattr(old_data, field)
                    if old_value is not None:
                        parsed.named[field] = old_value
                db.merge(SoilMoisture(**parsed.named))
                logging.log(logging.INFO,
                            f"Soil moisture updated with stamp {parsed['timestamp']}")
                db.commit()
        db.add_all(to_insert)
        if len(to_insert):
            logging.log(logging.INFO,
                        f"Updated {len(to_insert)} soil moistures with latest stamp {to_insert[-1].timestamp}")
        db.commit()
