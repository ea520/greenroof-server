from SQL_app.models import Base
from SQL_app.models import Temperature
from SQL_app.database import SessionLocal, engine
import datetime
import logging
import logging.handlers
import glob
import os
import parse
import math
import re
base = os.path.dirname(os.path.abspath(__file__))
logfile = base + "/logs/update_database.log"
logging.basicConfig(filename=logfile,
                    format='%(asctime)s %(message)s', level=logging.INFO)
handler = logging.handlers.RotatingFileHandler(logfile, mode='a', maxBytes=1 * 1024 * 1024,
                                               backupCount=5, encoding=None, delay=False)
logger = logging.getLogger().addHandler(handler)
Base.metadata.create_all(bind=engine)
db = SessionLocal()


# hh-hhhhhhhhhh where h is a character 0-f whitespace allowed either side
@parse.with_pattern(r"\s*[0-9a-f]{2}-[0-9a-f]{12}\s*")
# @parse.with_pattern(r"[^,]*")  # hh-hhhhhhhhhh where h is a character 0-f whitespace allowed either side
def parse_identifier(str):
    assert re.match("^\s*[0-9a-f]{2}-[0-9a-f]{12}\s*$", str) is not None
    return


@parse.with_pattern(r"[^,]*")   # 0 or more non-whitespace characters
def parse_float(str):
    try:
        val = float(str)
        return math.nan if val >= 84. else val
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan


temperature_format = "{timestamp:ti}," + ",".join(
    f"{{:identifier}},{{temperature_{i:02}:float}}" for i in range(1, 18 + 1))
compiled_format = parse.compile(temperature_format, extra_types={
                                "identifier": parse_identifier, "float": parse_float})

stamp = db.query(Temperature.timestamp).order_by(
    Temperature.timestamp.desc()).first()
if stamp is None:
    stamp = datetime.datetime.fromtimestamp(0.)
else:
    stamp = stamp[0]

weather_files = glob.glob(
    "/home/nrfis/Documents/blue_roof/temp/data/tempdata_*.csv")
latest_date = f"{stamp.year}{stamp.month:02}{stamp.day:02}"
reamining_files = [
    file for file in weather_files if os.path.basename(file) > "tempdata_" + latest_date]
reamining_files = sorted(reamining_files)
for file in reamining_files:
    lines = [line.strip("\n") for line in open(file).readlines()[2:]]
    parsed_lines = [compiled_format.parse(line) for line in lines]
    to_insert = []
    for line in parsed_lines:
        if line is not None and line["timestamp"] > stamp:
            to_insert.append(Temperature(**line.named))
    db.add_all(to_insert)
    if len(to_insert):
        logging.log(logging.INFO,
                    f"Updated {len(to_insert)} temperatures with latest stamp {to_insert[-1].timestamp}")

    db.commit()
