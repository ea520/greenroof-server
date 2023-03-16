import pandas as pd
from SQL_app import schemas
import os
import stat
import glob
import numpy as np
weather_date_format = "%d/%m/%Y %H:%M:%S"
file_directory = os.path.dirname(os.path.abspath(__file__))
output_directory =  filename = os.path.join(file_directory, "database", "weather")
weather_file_name = "/home/nrfis/Documents/blue_roof/weather/weather.csv"

daily_files = glob.glob(os.path.join(output_directory, "*"))
if len(daily_files) > 0:
    most_recent_date = max(daily_files)
    most_recent_date = os.path.basename(most_recent_date).replace(".csv", "")
    start_date = pd.Timestamp(most_recent_date) + pd.Timedelta("1D")
else:
    start_date = None # later set to the first date in the CSV file

with open(weather_file_name, "r") as f:
    names = f.readline().strip("\r\n").split("\t")
    names[0] = "timestamp"
    units = [f" ({unit})" if len(unit) else "" for unit in f.readline().strip("\r\n").split("\t")]
    names = [name + unit for name, unit in zip(names, units)]
    for line in f:
        date = line[:line.index('\t')]
        date = pd.to_datetime(date, format=weather_date_format)
        if start_date is None:
            start_date = date.floor("1D")
        if date >= start_date:
            break
    weather_data = pd.read_csv(f, sep="\t", na_values=["#+INF", "#-INF"], names=names)
    weather_data["timestamp"] = pd.to_datetime(weather_data["timestamp"],format=weather_date_format)
    while True:
        last_date = start_date + pd.Timedelta("1D")
        day_data = weather_data.loc[(weather_data["timestamp"] >= start_date) & (weather_data["timestamp"] < last_date)] # type: pd.DataFrame
        # there exists no data at a later date so the day isn't over. Only save complete days
        if not np.any((weather_data["timestamp"] >= last_date)):
            print(last_date)
            break
        if(len(day_data) > 0):
            filename = os.path.join(output_directory, f"{start_date.strftime('%Y-%m-%d')}.csv")
            day_data.to_csv(filename, index=False)
            os.chmod(filename, stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH) # make the file read only
        start_date = last_date