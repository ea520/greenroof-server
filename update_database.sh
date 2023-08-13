#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
(
    # Wait for lock on /var/lock/.myscript.exclusivelock (fd 200) for 1 second
    flock -x -w 1 200 || exit 1
    . "$SCRIPT_DIR/.venv/bin/activate";
    # make files for the daily weather data
    bash "$SCRIPT_DIR/create_daily_data.sh";
    # update the data in the SQL database
    nice python3 "$SCRIPT_DIR/update_soil_moisture_table.py";
    nice python3 "$SCRIPT_DIR/update_temperature_table.py";
    nice python3 "$SCRIPT_DIR/update_weather_table.py";
) 200>/var/lock/.update_database.exclusivelock

