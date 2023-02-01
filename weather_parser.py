"""
Every 5 mins, read the last few lines of the 
"""

import parse
import math
import time
import threading
from SQL_app.models import Base
from SQL_app.crud import create_data, base_model_to_base
from SQL_app.schemas import WeatherCreate, WaterLevel1Create, WaterLevel2Create
from SQL_app.database import SessionLocal, engine
from sqlalchemy.sql.expression import desc
import paramiko.client
import paramiko.ssh_exception
import time
import parse
import datetime
import pydantic
import sys

HOSTNAME_OR_IP = "gate.eng.cam.ac.uk"
USERNAME = "ea520"
FILENAMES = ["weather.txt", "water1.txt", "water2.txt"]

client = paramiko.client.SSHClient()
client.load_system_host_keys()
client.connect(hostname=HOSTNAME_OR_IP, username=USERNAME)

@parse.with_pattern(r"[^\s\\]*") # at least 0 or more non-whitespace characters
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan 
    

weather_format = "{datetime:tg}\t{power:float}\t{pressure:float}\t{rain:float}\t{sunshine}\t{wind_dir:float}\t{wind_speed:float}\t{average_humidity:float}\t{max_humidity:float}\t{min_humidity:float}\t{average_temp:float}\t{max_temp:float}\t{min_temp:float}\t{average_total_radiation:float}\t{max_total_radiation:float}\t{min_total_radiation:float}\t{average_diffuse_radiation:float}\t{max_diffuse_radiation:float}\t{min_diffuse_radiation:float}\t{evapotranspiration:float}\t{daily_cumulative_evapotranspiration:float}\t{daily_total_evapotranspiration:float}"
water_content_1_format = "{datetime:tg}\t{power1:float}\t{water_content01:float}\t{water_content02:float}\t{water_content03:float}\t{water_content04:float}\t{water_content05:float}\t{water_content06:float}\t{water_content07:float}\t{water_content08:float}\t{water_content09:float}\t{water_content10:float}"
water_content_2_format = "{datetime:tg}\t{power2:float}\t{water_content11:float}\t{water_content12:float}\t{water_content13:float}\t{water_content14:float}\t{water_content15:float}\t{water_content16:float}\t{water_content17:float}\t{water_content18:float}\t{water_content19:float}\t{water_content20:float}"

parsed_weather_format = parse.compile(weather_format,{"float": parse_float})
parsed_water_content_1_format = parse.compile(water_content_1_format,{"float": parse_float})
parsed_water_content_2_format = parse.compile(water_content_2_format,{"float": parse_float})

def insert_line(db, datatype: pydantic.BaseModel, line:str):
    data = format.parse(line)    
    if data is not None:
        create_data(db, datatype(**data.named))
        return True
    return False

if __name__=="__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    PARSED_FORMATS = [parsed_weather_format, parsed_water_content_1_format, parsed_water_content_2_format]
    DATATYPES = [WeatherCreate,WaterLevel1Create, WaterLevel2Create]
    while True:
        for filename, format, datatype in zip(FILENAMES, PARSED_FORMATS, DATATYPES):
            # IT DOESN'T MATTER IF A LINE IS APPENDED TO THE FILE AFTER THE WORD COUNT IS CALCULATED
            # THE ONLY CORRUPTED LINE SHOULD BE THE LAST ONE
            # IT IS ASSUMED THAT THE DATA IN THE FILE IS IN CHRONOLOGICAL ORDER WITH MOST RECENT LAST
            
            # Find the most recent date in the database
            latest_time_in_dataset = db.query(base_model_to_base.get(datatype)).order_by(desc("datetime")).first().datetime
            # Find the number of lines in the remote file
            try:
                line_count = int(client.exec_command(f"wc -l < '{filename}'", timeout=5*60)[1].read().decode("utf-8"))
            except paramiko.ssh_exception.SSHException as e:
                print(e)
                break
            
            new_data = []
            # Loop through lines in the file starting at the end
            for n in range(line_count, 0, -1):
                try:
                    # Get the n'th line
                    line = client.exec_command(f"sed '{n}q;d' '{filename}'",timeout=5*60)[1].read().decode("utf-8").replace("\r\n", "")
                except paramiko.ssh_exception.SSHException as e:
                    print(e)
                    break

                # Parse it
                data = format.parse(line)  
                if data is None and n < line_count:
                    print(f"Couldn't parse line {n} of '{filename}'",file=sys.stderr)
                else:
                    # If it's newer than any data in the database, add it to a list of new data
                    if data["datetime"] > latest_time_in_dataset:
                        new_data.append(datatype(**data.named))
                    # Otherwise, you can finish reading the file line by line
                    else:
                        break
            # Add them to the database in chronological order
            for new_datum in reversed(new_data):
                create_data(db, new_datum)
            db.commit()
        time.sleep(5*60)
