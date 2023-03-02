import parse
import linecache
import math
from SQL_app.models import Weather
import datetime

@parse.with_pattern(r"[^\t]*")  # 0 or more non-whitespace characters
def parse_float(str):
    try:
        return float(str)
    except ValueError:
        # Should be empty string, "#+INF" or "#-INF"
        return math.nan


def get_weather(start_date):
    filename = "/home/nrfis/Documents/blue_roof/weather/weather.csv"
    weather_format = "{timestamp:tg}\t{power:float}\t{pressure:float}\t{rain:float}\t{sunshine}\t{wind_dir:float}\t{wind_speed:float}\t{average_humidity:float}\t{max_humidity:float}\t{min_humidity:float}\t{average_temp:float}\t{max_temp:float}\t{min_temp:float}\t{average_total_radiation:float}\t{max_total_radiation:float}\t{min_total_radiation:float}\t{average_diffuse_radiation:float}\t{max_diffuse_radiation:float}\t{min_diffuse_radiation:float}\t{evapotranspiration:float}\t{daily_cumulative_evapotranspiration:float}\t{daily_total_evapotranspiration:float}"
    compiled_format = parse.compile(weather_format, {"float": parse_float})
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
            yield Weather(**result.named)
        linenum+=1


if __name__ == "__main__":
    for weather in get_weather(datetime.datetime.fromtimestamp(0.)):
        if weather is not None:
            print(weather.timestamp)