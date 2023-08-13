# Green Roof Documentation

## Software details
The code resides in `/home/nrfis/blue_roof_code/`. I believe the folder can be moved without many problems. The virtual environment may need replacing (`python3.7 -m venv .venv && pip install --upgrade pip && pip install -r requirements.txt`). As well as the venv, the crontab file needs updating (use sudo crontab -e while logged in as nrfis and update the file).

The SQL database is in [/home/nrfis/blue_roof_code/database/sql_app.sqlite](database/sql_app.sqlite) but the tab/comma separated text files are found in `/home/nrfis/Documents/blue_roof/`. Moving these files would probably be more trouble than it's worth.

I now know that SQLite was probably not the best choice (it was fast to set up but is slower to run and has fewer features) so as an extension, I would look into setting up a PostgreSQL database instead as an extension.

### Updating the database

The cron job for updating the database on the server
```bash
$ sudo crontab -l
*/5 * * * * cd /home/nrfis/blue_roof_code/ && ./update_database.sh
```

[/home/nrfis/blue_roof_code/update_database.sh](update_database.sh) is a file for:
1. Converting the large database files into many smaller daily files
1. Parsing the files
1. Storing the data in the database

The large database files (direct from the weather stations) are copied from the windows mini-PC into `/home/nrfis/Documents/blue_roof/weather/weather.csv`,`/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_1.csv` and `/home/nrfis/Documents/blue_roof/soil_moisture/soil_moisture_2.csv` using SSH. 

Examples of the daily file names are `/home/nrfis/Documents/blue_roof/weather/daily/2023-01-01.csv`, `/home/nrfis/Documents/blue_roof/soil_moisture/daily1/2023-02-01.csv` and `/home/nrfis/Documents/blue_roof/soil_moisture/daily2/2023-02-01.csv`.

### Steps required for adding a new table to the database (e.g. water level):
1. Edit models.py
```python
class WaterLevel(Base):
    __tablename__ = "water_level" # name as it will appear in the database
    timestamp = Column(DateTime, primary_key=True, index=True)
    water_level_01 = Column(Float)
    ...
```
2. Parse the water level data and store it in the database (see update_*_table.py though the code may be overcomplicated)

3. Add API endpoints for data access (see [SQL_app/webapp_main.py](SQL_app/webapp_main.py))

4. Add pages to the website (see [SQL_app/webapp_main.py](SQL_app/webapp_main.py) and [SQL_app/templates](SQL_app/templates)).

Logs of the data updates and website accesses are found in the folder `logs`
## User details
### The website
The website is currently found at http://csic-server.eng.cam.ac.uk:8001 and is available only through the VPN. It should be pretty intuitive how to use it if you can access it. For undergrads, VPN access can be done by either using the computers in the DPO or by using a proxy.

#### Note on the proxy method
On my own linux machine, I created a file ~/.ssh/config with the contents shown below. On windows, I added the file to `C:\Users\username\.ssh\config` and replaced the ProxyJump line with `ProxyCommand ssh -q -W %h:22 gate`. 
```txt
# replace ea520 with your crsid
Host engineering
    HostName gate.eng.cam.ac.uk
    LocalForward localhost:8001 csic-server.eng.cam.ac.uk:8001
    User ea520

# the main account on the server
Host nrfis-computer
    HostName 129.169.72.175
    ProxyJump engineering
    User nrfis
```

With this, you can access the files on the server with `ssh nrfis@nrfis-computer`. To access the website, "ssh engineering" and now on your browser, you can access the website with http://localhost:8001 

#### The API
The API is found on http://csic-server.eng.cam.ac.uk:8001/docs. The endpoints are of the form http://csic-server.eng.cam.ac.uk:8001/{rate}/{format}/{table}/{options}. An automatically generated documentation site can be found at http://csic-server.eng.cam.ac.uk:8001/API. Here are some example API calls and responses:

##### Example 1
```bash
$ GET "http://csic-server.eng.cam.ac.uk:8001/API/raw/JSON/weather/?duration=1000&q=rain"
```
```JSON
{
    "timestamps": ["2023-06-20T00:55:00","2023-06-20T01:00:00"],
    "measurements":{"rain":[0.0,0.0]}
}
```
##### Example 2 (Python)
```python
>>> import requests
>>> URL = "http://csic-server.eng.cam.ac.uk:8001/API/daily/JSON/temperature?start_time=2023-01-01T00:00:00&end_time=2023-05-01T00:00:00&q=temperature_01&q=temperature_18"
>>> response = requests.get(URL)
>>> response.json()
>>> len(response.json()["measurements"]["temperature_01"])
90
```

##### Example 3 (Latest data)
```python
import requests
URL = "http://csic-server.eng.cam.ac.uk:8001/API/latest/JSON/moisture?q=soil_moisture_01"
response = requests.get(URL)
latest_measurements = response.json()
if(latest_measurements["soil_moisture_01"] < 20): # 20% is quite dry
    turn_on_sprinkler_01()
```

## Potential problems
The database updates every 5 minutes so should work after a reboot however, currently, the website may not start when the machine starts up (I added a line in the crontab file but haven't tested it on reboot). The command for starting the server is
```bash
cd /home/nrfis/blue_roof_code
. /venv/bin/activate
nohup uvicorn SQL_app.webapp_main:app --port 8001 --host 0.0.0.0 > logs/app.out 2> logs/app.err
```
To kill the website it, I use htop and filter for SQL_app there you can see the PID and kill it. There are probably lots of other ways to do it.


There are no automatic measures currently in place to delete the data on the weather station so it's slowly filling up.



## Notes on the measured data   
### The sensors
The sensors positions on the roof can be found in [/home/nrfis/blue_roof_code/Layout-of-green-roof-sensors.pdf](Layout-of-green-roof-sensors.pdf)

### Weather Station
|Name|Description|
|-|-|
|<h4>Data logger power<h4>|The voltage of the data logger. If the power is low (far below 11V), readings at those times may be incorrect.|
|<h4>Pressure<h4>|The air pressure (hPa)|
|<h4>Rain<h4>|The intensity of rainfall (mm since last reading)|
|<h4>Sunshine<h4>|Whether the sun is shining (takes values "sun" and "no sun")|
|<h4>Wind dir<h4>|The bearing of the wind (probably relative to due north). Unclear whether it's meaningful when wind speed is 0|
|<h4>Wind speed<h4>|The speed of the wind in m/s|
|<h4>Average humidity<h4>|The average relative humidity over a 5 minute period|
|<h4>Max humidity<h4>|The maximum relative humidity over a 5 minute period|
|<h4>Min humidity<h4>|The minimum relative humidity over a 5 minute period|
|<h4>Average temperature<h4>|The average temperature (in ℃) over a 5 minute period|
|<h4>Max temperature<h4>|The average temperature (in ℃) over a 5 minute period|
|<h4>Min temperature<h4>|The average temperature (in ℃) over a 5 minute period|
|<h4>Average total radiation<h4>|The average solar radiation (in W m⁻²) over a 5 minute period|
|<h4>Max total radiation<h4>|The average solar radiation (in W m⁻²) over a 5 minute period|
|<h4>Min total radiation<h4>|The average solar radiation (in W m⁻²) over a 5 minute period|
|<h4>Average diffuse radiation<h4>|The average diffuse radiation (in W m⁻²) over a 5 minute period|
|<h4>Max diffuse radiation<h4>|The average diffuse radiation (in W m⁻²) over a 5 minute period|
|<h4>Min diffuse radiation<h4>|The average diffuse radiation (in W m⁻²) over a 5 minute period|
|<h4>Evapotranspiration<h4>|The Penman-monteith evapotranspiration (in mm) over the last hour|
|<h4>Daily cumulative evapotranspiration<h4>|The cumulative Penman-monteith evapotranspiration (in mm) over the day|
|<h4>Daily total evapotranspiration<h4>|The total Penman-monteith evapotranspiration (in mm) by the end of the day|

For the daily and hourly data, several filters are used for compressing data over a long time period into 1 number:
 - The wind direction uses the [circular mean](https://en.wikipedia.org/wiki/Circular_mean) of the raw data. 
 - The max and mins take the minima and maxima of the raw data. 
 - The rainfall and evapotranspiration take the sum of the raw data (calculating the total in the hour/day).
 - The sunshine takes the modal value
 - The rest uses the arithmetic mean of the raw data. This is done on the server as requested and not stored in the database so access may be slow if there's a lot of data being requested.

### Water level sensors
The water level sensors are located on the schematic that comes with this file.
GP2-SMC-05 in the diagram corresponds to soil_moisture_05.

### The temperature sensors
|Website/API name|ID in text files|Name on diagram|
|-|-|-|
|temperature_01|28-041750b045ff|RF-TMP-01 a?|
|temperature_02|28-0417500f45ff|-|
|temperature_03|28-041750a8b7ff|-|
|temperature_04|28-041750bb80ff|-|
|temperature_05|28-041750a7fdff|-|
|temperature_06|28-041750b9bcff|-|
|temperature_07|28-041750b5efff|-|
|temperature_08|28-041750a9daff|-|
|temperature_09|28-0417516800ff|-|
|temperature_10|28-041750a64eff|-|
|temperature_11|28-041751637cff|-|
|temperature_12|28-041750d35fff|-|
|temperature_13|28-0417516e82ff|-|
|temperature_14|28-04175173cfff|-|
|temperature_15|28-041750cccfff|-|
|temperature_16|28-0417516affff|-|
|temperature_17|28-041750a9dfff|-|
|temperature_18|28-04175176bfff|-|