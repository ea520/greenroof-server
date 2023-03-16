import pandas as pd
from SQL_app import schemas
import os
import stat
import glob
import numpy as np
moisture_date_format = "%d/%m/%Y %H:%M:%S"
file_directory = os.path.dirname(os.path.abspath(__file__))
output_directory =  filename = os.path.join(file_directory, "database", "moisture")
moisture1_file_name = "/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_1.csv"
moisture2_file_name = "/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_2.csv"

daily_files = glob.glob(os.path.join(output_directory, "*"))
if len(daily_files) > 0:
    most_recent_date = max(daily_files)
    most_recent_date = os.path.basename(most_recent_date).replace(".csv", "")
    start_date = pd.Timestamp(most_recent_date) + pd.Timedelta("1D")
    set_start_date = False
else:
    set_start_date = True
    start_date = pd.Timestamp(0) # later set to the first date in the CSV file

def get_dataframe(filename):
    f = open(filename, "r")
    names = f.readline().strip("\r\n").split("\t")
    names[0] = "timestamp"
    names[1] = "power1"
    units = [f" ({unit})" if len(unit) else "" for unit in f.readline().strip("\r\n").split("\t")]
    names = [name + unit for name, unit in zip(names, units)]
    for line in f:
        date = line[:line.index('\t')]
        date = pd.to_datetime(date, format=moisture_date_format)
        if set_start_date:
            global start_date
            start_date = min(date, start_date).floor("1D")
        if date >= start_date:
            break
    moisture_data = pd.read_csv(f, sep="\t", na_values=["#+INF", "#-INF"], names=names)
    moisture_data["timestamp"] = pd.to_datetime(moisture_data["timestamp"],format=moisture_date_format)
    return moisture_data

moisture_data1 = get_dataframe(moisture1_file_name)
moisture_data2 = get_dataframe(moisture2_file_name)
moisture_data = pd.merge(moisture_data1, moisture_data2, on="timestamp")

while True:
    last_date = start_date + pd.Timedelta("1D")
    day_data = moisture_data.loc[(moisture_data["timestamp"] >= start_date) & (moisture_data["timestamp"] < last_date)] # type: pd.DataFrame
    # there exists no data at a later date so the day isn't over. Only save complete days
    if not np.any((moisture_data["timestamp"] >= last_date)):
        print(last_date)
        break
    if(len(day_data) > 0):
        filename = os.path.join(output_directory, f"{start_date.strftime('%Y-%m-%d')}.csv")
        day_data.to_csv(filename, index=False)
        os.chmod(filename, stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH) # make the file read only
    start_date = last_date