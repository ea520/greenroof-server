import requests
import pytest


@pytest.mark.parametrize("url", [
    "http://localhost:8001/API/raw/JSON/weather?duration=1000&q=rain",
    "http://localhost:8001/API/raw/JSON/moisture?start_time=3000-01-01T00:00:00&q=power_1",
    "http://localhost:8001/API/raw/JSON/temperature?end_time=1970-01-01T00:00:00&q=temperature_01&q=temperature_18",
    "http://localhost:8001/API/latest/JSON/weather?q=sunshine",
    "http://localhost:8001/API/latest/JSON/moisture?q=soil_moisture_01",
    "http://localhost:8001/API/latest/JSON/temperature/",
    "http://localhost:8001/API/hourly/JSON/weather?duration=1000&start_time=3000-01-01T00:00:00",
    "http://localhost:8001/API/hourly/JSON/moisture?start_time=3000-01-01T00:00:00&end_time=3001-01-01T00:00:00",
    "http://localhost:8001/API/hourly/JSON/temperature?end_time=1970-01-01T00:00:00&duration=1",
    "http://localhost:8001/API/daily/JSON/weather?duration=1000&start_time=3000-01-01T00:00:00",
    "http://localhost:8001/API/daily/JSON/moisture?start_time=3000-01-01T00:00:00&end_time=3001-01-01T00:00:00",
    "http://localhost:8001/API/daily/JSON/temperature?end_time=1970-01-01T00:00:00&duration=1",
])
def test_url_json(url):
    r = requests.get(url)
    assert r.status_code == 200


@pytest.mark.parametrize("url", [
    "http://localhost:8001/API/raw/CSV/weather?duration=1000&q=rain",
    "http://localhost:8001/API/raw/CSV/moisture?start_time=3000-01-01T00:00:00&q=power_1",
    "http://localhost:8001/API/raw/CSV/temperature?end_time=1970-01-01T00:00:00&q=temperature_01&q=temperature_18",
    "http://localhost:8001/API/hourly/CSV/weather?duration=1000&start_time=3000-01-01T00:00:00",
    "http://localhost:8001/API/hourly/CSV/moisture?start_time=3000-01-01T00:00:00&end_time=3001-01-01T00:00:00",
    "http://localhost:8001/API/hourly/CSV/temperature?end_time=1970-01-01T00:00:00&duration=1",
    "http://localhost:8001/API/daily/CSV/weather?duration=1000&start_time=3000-01-01T00:00:00",
    "http://localhost:8001/API/daily/CSV/moisture?start_time=3000-01-01T00:00:00&end_time=3001-01-01T00:00:00",
    "http://localhost:8001/API/daily/CSV/temperature?end_time=1970-01-01T00:00:00&duration=1",
])
def test_url_csv(url):
    r = requests.get(url)
    assert r.status_code == 200
