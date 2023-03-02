import parse
import linecache
import math
from SQL_app.models import SoilMoisture


@parse.with_pattern(r"[^\s\\]*")
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan

soil_moisture_1_format = "{timestamp:tg}\t{power_1:float}\t{soil_moisture_01:float}\t{soil_moisture_02:float}\t{soil_moisture_03:float}\t{soil_moisture_04:float}\t{soil_moisture_05:float}\t{soil_moisture_06:float}\t{soil_moisture_07:float}\t{soil_moisture_08:float}\t{soil_moisture_09:float}\t{soil_moisture_10:float}"
soil_moisture_2_format = "{timestamp:tg}\t{power_2:float}\t{soil_moisture_11:float}\t{soil_moisture_12:float}\t{soil_moisture_13:float}\t{soil_moisture_14:float}\t{soil_moisture_15:float}\t{soil_moisture_16:float}\t{soil_moisture_17:float}\t{soil_moisture_18:float}\t{soil_moisture_19:float}\t{soil_moisture_20:float}"

compiled_soil_moisture_1_format = parse.compile(soil_moisture_1_format, {"float": parse_float})
compiled_soil_moisture_2_format = parse.compile(soil_moisture_2_format, {"float": parse_float})


def _get_soil_moisture(filename, compiled_format, start_date):
    linenum = 3 # line 1 and 2 are for headers and units
    line_count = sum(1 for line in open(filename))
    for i in range(line_count, 0, -1):
        linenum = i
        line = linecache.getline(filename, linenum).replace("\n", "")
        result = compiled_format.parse(line)
        if(result is not None):
            ts = result["timestamp"]
            if ts < start_date:
                break
    while True:
        line_count = sum(1 for line in open(filename))
        linecache.checkcache()
        line = linecache.getline(filename, linenum).replace("\n", "")
        result = compiled_format.parse(line)
        if result is None:
            if(linenum < line_count):
                print(filename, linenum)
            yield None
            linenum = min(linenum, line_count)
        else:
            yield SoilMoisture(**result.named)
        linenum+=1

def get_soil_moisture_1(start_date):
    filename = "/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_1.csv"
    compiled_format = compiled_soil_moisture_1_format
    return _get_soil_moisture(filename, compiled_format, start_date)

def get_soil_moisture_2(start_date):
    filename = "/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_2.csv"
    compiled_format = compiled_soil_moisture_2_format
    return _get_soil_moisture(filename, compiled_format, start_date)

if __name__ == "__main__":
    import datetime, time
    for temp in get_soil_moisture_2(datetime.datetime.fromisoformat("2022-05-01 10:00:00")):
        if temp is not None:
            print(temp.timestamp)
            time.sleep(1)