import os
import pandas as pd
date_length = 10  # the number of characters in a date xx/xx/xxxx
data_start = 3  # the line number where the data starts


def update_daily_text_files(input_filename, output_folder):
    # filename = "/home/nrfis/Documents/blue_roof/weather/weather.csv"

    dates = os.popen(
        f'tail -n +{data_start} "{input_filename}" | uniq -w{date_length} | cut -c-{date_length}').readlines()

    dates = [date.strip() for date in dates]
    # output_folder = "/home/ea520/greenroof-server/weather/"

    table_header = open(input_filename).readline().strip()
    table_header = "timestamp," + table_header.replace("\t", ",")

    for date in dates:
        day, month, year = date.split("/")
        output_file = output_folder + f"{year}-{month}-{day}" + ".csv"
        if (not os.path.exists(output_file) or date == dates[-1]):
            filedate = f"{year}-{month}-{day}"
            os.popen(
                f"echo '{table_header}' > /tmp/daily-data-{filedate} && \
                  grep {date} {input_filename} | tr '\t' ',' >> /tmp/daily-data-{filedate} && \
                  mv /tmp/daily-data-{filedate} {output_file}")


update_daily_text_files("/home/nrfis/Documents/blue_roof/weather/weather.csv",
                        "/home/ea520/greenroof-server/weather/")
update_daily_text_files("/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_1.csv",
                        "/home/ea520/greenroof-server/soil_moisture1/")
update_daily_text_files("/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_2.csv",
                        "/home/ea520/greenroof-server/soil_moisture2/")
