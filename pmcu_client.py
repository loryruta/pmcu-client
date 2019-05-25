import struct

import paho.mqtt.client as mqtt


def nmea_coordinate_to_decimal(coordinate, direction):
    divider = coordinate.find(".") - 2
    result = int(coordinate[0:divider]) + (float(coordinate[divider:]) / 60.0)
    if direction == "S" or direction == "W":
        result *= -1
    return result


def decode_gga_sentence(gga_sentence):
    gga_sentence = gga_sentence.split(",")

    fix_quality = int(gga_sentence[5])
    if fix_quality == 0:
        return None

    return {
        "location_quality": "gps",
        "location_latitude": nmea_coordinate_to_decimal(gga_sentence[1], gga_sentence[2]),
        "location_longitude": nmea_coordinate_to_decimal(gga_sentence[3], gga_sentence[4]),
        "location_number_of_satellites": int(gga_sentence[6]),
        "location_horizontal_dop": float(gga_sentence[7]),
        "location_altitude": float(gga_sentence[8]),
        "location_height_of_sea_level": float(gga_sentence[10]),
    }


def decode_gsm_location(gsm_location):
    start_at = gsm_location.find("+CIPGSMLOC: ")
    if start_at != 0:
        return None

    fields = gsm_location[(start_at + 12):].split(",")
    if len(fields) != 5:
        return None

    return {
        "location_quality": "gsm",
        "location_longitude": fields[1],
        "location_latitude": fields[2],
        "location_date": fields[3],
        "location_time": fields[4]
    }


def decode_pm_data(pm_data):
    def parse_float(data):
        return struct.unpack("!f", data[0:4])[0]

    return {
        "pm_1_0_mass_concentration": parse_float(pm_data[0:4]),
        "pm_2_5_mass_concentration": parse_float(pm_data[4:8]),
        "pm_4_0_mass_concentration": parse_float(pm_data[8:12]),
        "pm_10_mass_concentration": parse_float(pm_data[12:16]),
        "pm_0_5_number_concentration": parse_float(pm_data[16:20]),
        "pm_1_0_number_concentration": parse_float(pm_data[20:24]),
        "pm_2_5_number_concentration": parse_float(pm_data[24:28]),
        "pm_4_0_number_concentration": parse_float(pm_data[28:32]),
        "pm_10_number_concentration": parse_float(pm_data[32:36]),
        "pm_typical_size": parse_float(pm_data[36:40]),
    }


def decode_measurement(pmcu_id, measurement):
    result = {
        "id": pmcu_id,
        "imei": pmcu_id[5:],
        "rh": float((measurement[0] << 8) | measurement[1]) / 10,
        "temperature": float((measurement[2] << 8) | measurement[3]) / 10
    }

    offset = 4

    gga_sentence = ""
    for char in measurement[offset:]:
        offset += 1
        char = chr(char)
        if char == '\0':
            break
        gga_sentence += char
    location = decode_gga_sentence(gga_sentence)

    gsm_sentence = ""
    for char in measurement[offset:]:
        offset += 1
        char = chr(char)
        if char == '\0':
            break
        gsm_sentence += char

    if not location:  # If GPS location was not found, decodes GSM one
        location = decode_gsm_location(gsm_sentence)

    if location:
        result.update(**location)

    result.update(**decode_pm_data(measurement[offset:]))

    return result


class PMCUClient:
    def __on_mqtt_message(self, message):
        self.on_measurement(decode_measurement(message.topic, message.payload))

    def __init__(self, on_measurement):
        import random
        import sys
        self.mqtt_client = mqtt.Client("client/" + str(random.randint(0, sys.maxsize)))
        self.on_measurement = on_measurement
        self.mqtt_client.on_message = lambda mqtt_client, user_data, message: self.__on_mqtt_message(message)

    def listen(self, broker_address, broker_port=1883):
        self.mqtt_client.connect(broker_address, broker_port)
        self.mqtt_client.subscribe("pmcu/+")
        self.mqtt_client.loop_forever()

    def disconnect(self):
        self.mqtt_client.disconnect()


if __name__ == "__main__":
    import sys
    import random
    import json

    if len(sys.argv) < 2:
        print("IP address not specified!")
        exit()

    print("IP address selected: \"%s:1883\"" % sys.argv[1])

    measurement_id = 0


    def __on_measurement(message):
        global measurement_id
        print("Measurement (%d):" % measurement_id)
        print(json.dumps(message, indent=4))
        measurement_id += 1


    client = PMCUClient(__on_measurement)
    client.listen(sys.argv[1])
