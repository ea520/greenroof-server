weather_sensor_descriptions={
    "Data logger power": "The voltage of the data logger. If the power is low (far below 11V), readings at those times may be incorrect.",
    "Pressure": "The air pressure (hPa)",
    "Rain": "The intensity of rainfall (mm since last reading)",
    "Sunshine": 'Whether the sun is shining (takes values "sun" and "no sun")',
    "Wind dir": "The bearing of the wind (probably relative to due north). Unclear whether it's meaningful when wind speed is 0",
    "Wind speed": "The speed of the wind in m/s",

    "Average humidity": "The average relative humidity over a 5 minute period",
    "Max humidity": "The maximum relative humidity over a 5 minute period",
    "Min humidity": "The minimum relative humidity over a 5 minute period",

    "Average temperature": f"The average temperature (in {chr(0x2103)}) over a 5 minute period",
    "Max temperature": f"The average temperature (in {chr(0x2103)}) over a 5 minute period",
    "Min temperature": f"The average temperature (in {chr(0x2103)}) over a 5 minute period",

    "Average total radiation": f"The average solar radiation (in W m{chr(0x207B) + chr(0x00B2)}) over a 5 minute period",
    "Max total radiation": f"The average solar radiation (in W m{chr(0x207B) + chr(0x00B2)}) over a 5 minute period",
    "Min total radiation": f"The average solar radiation (in W m{chr(0x207B) + chr(0x00B2)}) over a 5 minute period",


    "Average diffuse radiation": f"The average diffuse radiation (in W m{chr(0x207B) + chr(0x00B2)}) over a 5 minute period",
    "Max diffuse radiation": f"The average diffuse radiation (in W m{chr(0x207B) + chr(0x00B2)}) over a 5 minute period",
    "Min diffuse radiation": f"The average diffuse radiation (in W m{chr(0x207B) + chr(0x00B2)}) over a 5 minute period",

    "Evapotranspiration": f"The Penman-monteith evapotranspiration (in mm) over the last hour",
    "Daily cumulative evapotranspiration": f"The cumulative Penman-monteith evapotranspiration (in mm) over the day",
    "Daily total evapotranspiration": f"The total Penman-monteith evapotranspiration (in mm) by the end of the day",
}

temperature_sensor_descriptions={
    "Temperature xx": f"The tempertature (in {chr(0x2103)}) of the roof at the position of xx",
}

soil_moisture_descriptions={
    "Data logger power 1, Data logger power 2": f"The voltage of the datalogger. Logger 1 records the water levels 1-10. Logger 2 records water levels 11-20",
    "Soil moisture xx": "The soil moisture on the roof at location xx as a percentage. This is ratio of the volume of water in the soil to the total voume of the soil."
}