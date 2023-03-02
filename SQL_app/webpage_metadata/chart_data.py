weather_chart_info = {
    "Power":{
        "unit": "V",
        "sensor_names": ["power"],
        "begin_at_zero": True,
        "chart_type": "line"
    },
    "Pressure":{
        "unit": "hPa",
        "sensor_names": ["pressure"],
        "begin_at_zero": False,
        "chart_type": "line"
    },
    "Rain":{
        "unit": "mm @ 5min",
        "sensor_names": ["rain"],
        "begin_at_zero": True,
        "chart_type": "line"
    },
    # "Sunshine":{
    #     "unit": "",
    #     "sensor_names": ["sunshine"],
    #     "begin_at_zero": True,
    #     "chart_type": "line"
    # },
    "Wind direction":{
        "unit": chr(0x00B0),
        "sensor_names": ["wind_dir"],
        "begin_at_zero": True,
        "chart_type": "polar"
    },
    "Wind speed":{
        "unit": "m/s",
        "sensor_names": ["wind_speed"],
        "begin_at_zero": True,
        "chart_type": "line"
    },
    "Mean, max, min humidity":{
        "unit": "%",
        "sensor_names": ["average_humidity", "max_humidity", "min_humidity"],
        "begin_at_zero": True,
        "chart_type": "line",
        "representitive_sensor": "average_humidity" # if 1 number is required, which to use
    },
    "Mean, max, min temperature":{
        "unit": chr(0x2103),
        "sensor_names": ["average_temp", "max_temp", "min_temp"],
        "begin_at_zero": True,
        "chart_type": "line",
        "representitive_sensor": "average_temp"
    },
    "Mean, max, min total solar radiation":{
        "unit": "W/m2",
        "sensor_names": ["average_total_radiation", "max_total_radiation", "min_total_radiation"],
        "begin_at_zero": True,
        "chart_type": "line",
        "representitive_sensor": "average_total_radiation"
    },
    "Mean, max, min diffuse solar radiation":{
        "unit": "W/m2",
        "sensor_names": ["average_diffuse_radiation", "max_diffuse_radiation", "min_diffuse_radiation"],
        "begin_at_zero": True,
        "chart_type": "line",
        "representitive_sensor": "average_diffuse_radiation"
    },
    # "Hourly evapotranspiration":{
    #     "unit": "mm",
    #     "sensor_names": ["evapotranspiration"],
    #     "begin_at_zero": False,
    #     "chart_type": "line"
    # },
    # "Daily cumulative evapotranspiration":{
    #     "unit": "mm",
    #     "sensor_names": ["daily_cumulative_evapotranspiration"],
    #     "begin_at_zero": False,
    #     "chart_type": "line"
    # },
}

soil_moisture_chart_info = dict(
    (f"Soil Moisture {i}", 
     {
        "unit": "%",
        "sensor_names": [f"soil_moisture_{i:02}"],
        "begin_at_zero": True,
        "chart_type": "line"
    }) for i in range(1,21)
)


temperature_chart_info = dict(
    (f"Temp {i}", 
     {
        "unit": chr(0x2103),
        "sensor_names": [f"temperature_{i:02}"],
        "begin_at_zero": True,
        "chart_type": "line"
    }) for i in range(1,19)
)