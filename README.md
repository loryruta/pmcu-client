A library made to retrieve PMCU data from an MQTT broker.

# Requirements:
* Ensure you have at least Python 3.5 or higher. 
* Install `paho-mqtt`.
* Download the library [here](http://gitlab.com/pmcontrolunit/webserver/snippets/1851169/raw?inline=false) and add it to your project.

# Usage:
```python
from pmcu_client import PMCUClient

# Defines a callback that will be issued when PMCU measurement is received.
def on_measurement(measurement):
    # Read further to view more information about `measurement` format.
    pass

broker_address = "<IP>"
broker_port = <PORT>

# Connects to the MQTT broker and listens for measurements.
client = PMCUClient(on_measurement)
client.listen(broker_address, broker_port)
```

# Data format:
Example of `measurement` structure:
```json
{
    "id": "pmcu/864713030064821",
    "imei": "864713030064821",
    "rh": 59.2,
    "temperature": 22.5,
    "location_quality": "gsm",
    "location_longitude": "11.107712",
    "location_latitude": "44.572208",
    "location_date": "2019/05/05",
    "location_time": "17:52:10",
    "pm_1_0_mass_concentration": 21.405275344848633,
    "pm_2_5_mass_concentration": 22.870800018310547,
    "pm_4_0_mass_concentration": 23.035221099853516,
    "pm_10_mass_concentration": 23.090166091918945,
    "pm_0_5_number_concentration": 144.33004760742188,
    "pm_1_0_number_concentration": 168.0661163330078,
    "pm_2_5_number_concentration": 168.87908935546875,
    "pm_4_0_number_concentration": 168.9160614013672,
    "pm_10_number_concentration": 168.9263916015625,
    "pm_typical_size": 0.5932186841964722
}
```

Here follows a description of each field.

| Field | Example Value | Description |
| --- | --- | --- |
| `id` | pmcu/864713030064821 | A unique identifier for the PMCU. |
| `imei` | 864713030064821 | The IMEI of the SIM that the PMCU is using. |
| `rh` | 71.1 RF | Humidity, measured in RF. |
| `temperature` | 23.7 °C | Temperature, measured in Celsius. |
| `pm_1_0_mass_concentration` | float μg/m³ | PM1.0 mass concentration. |
| `pm_2_5_mass_concentration` | float μg/m³ | PM2.5 mass concentration. |
| `pm_4_0_mass_concentration` | float μg/m³ | PM4.0 mass concentration. |
| `pm_10_mass_concentration` | float μg/m³ | PM10 mass concentration. |
| `pm_0_5_number_concentration` | float #/cm³ | PM0.5 number concentration. |
| `pm_1_0_number_concentration` | float #/cm³ | PM1.0 number concentration. |
| `pm_2_5_number_concentration` | float #/cm³ | PM2.5 number concentration. |
| `pm_4_0_number_concentration` | float #/cm³ | PM4.0 number concentration. |
| `pm_10_number_concentration` | float #/cm³ | PM10 number concentration. |
| `location_quality` | gps/gsm/invalid | The quality of the location data. |

If `location_quality: gps`:

| Field | Value | Description |
| --- | --- | --- |
| `location_latitude` | 48.07038 | Almost accurate latitude. |
| `location_longitude` | -01.1310 | Almost accurate longitude. |
| `location_number_of_satellites` | 3 | Number of satellites tracked. |
| `location_horizontal_dop` | 0.5 | Horizontal dilution of position (higher means lower precision). |
| `location_altitude` | 545.4 | Altitude above sea level, in meters. |
| `location_height_of_sea_level` | 46.9 | Height of sea level, in meters. |

If `location_quality: gsm`:

| Field | Value | Description |
| --- | --- | --- |
| `location_latitude` | 48.07038 | Inaccurate latitude. |
| `location_longitude` | -01.1310 | Inaccurate longitude. |
| `location_date` | 2019/02/05 | Accurate date in YYYY/MM/DD format. |
| `location_time` | 11:41:46 | Accurate time in hh/mm/ss format. |

If `location_quality: inavlid`, neither of these fields are present.
