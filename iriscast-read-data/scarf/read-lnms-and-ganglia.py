import ast
import os
import csv
from datetime import datetime
import re

def read_scarf_devices(inp_dir, type):
    all_data = []
    list_of_files = []
    for root, dirs, files in os.walk(inp_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))

    for name in list_of_files:
        with open(name, 'r') as device_dict:
            data = device_dict.read()

        data = data.replace("None", "-1")

        for keyword in ["device", "model", "rack"]:
            regexp = re.compile(r"'%s':\s*(.*?)\s*," % keyword)
            match = regexp.search(data)

            if match:
                match = match.group(0).split(":")[1].strip()
                if not match[0] == '\'':
                    data = data.replace(match[:-1], "'%s'" % match[:-1])

        device_data = ast.literal_eval(data)

        # Datetime, Device, Model, Rack, Watts
        for i, record in enumerate(device_data["data"]):
            record_dict = {
                "unixtime": int(device_data["meta"]["start"])+(i * int(device_data["meta"]["step"])),
                "device": device_data["meta"]["device"],
                "model": device_data["meta"]["model"],
                "rack": device_data["meta"]["rack"],
            }
            for i, legend_kw in enumerate(device_data["meta"]["legend"]):
                record_dict.update({
                    legend_kw: record[i] if not record[i] == -1 else ''
                })

            if type == "node":
                if not record_dict["'Watts'"]:
                    record_dict.update({
                        "watt_hours": ''
                    })
                else:
                    record_dict.update({
                        "watt_hours": round(float(record_dict["'Watts'"]) * 1/30, 3)
                    })
            elif type == "pdu":
                if not record_dict["'Total amps'"] and not record_dict["'Volts'"]:
                    record_dict.update({
                        "watt_hours": ''
                    })
                else:
                    record_dict.update({
                        "watt_hours": round(float(record_dict["'Watts'"]) * 1/12, 3)
                    })

            elif type == "network_device":
                if record_dict['device'] not in ['scarf15-ib', 'scarf16-mlnx']:
                    if not record_dict["'PSU1 Watts'"] and not record_dict["PSU2 Watts"]:
                        record_dict.update({
                            "watt_hours": ''
                        })
                    else:
                        record_dict.update({
                            "watt_hours": round(float(record_dict["'PSU1 Watts'"]) + float(record_dict["'PSU2 Watts'"]) * 1/12, 3)
                        })

            elif type == "netword_device_other":
                if record_dict['device'] in ['scarf15-ib', 'scarf16-mlnx']:
                    if not record_dict["'Watts'"]:
                        record_dict.update({
                            "watt_hours": ''
                        })
                    else:
                        record_dict.update({
                            "watt_hours": round(float(record_dict["'Watts'"]) * 1 / 12, 3)
                        })

            print(record_dict["unixtime"], datetime.fromtimestamp(record_dict["unixtime"]))
            all_data.append(record_dict)
    return all_data


def write_file(all_data, out_fp):
    keys = all_data[0].keys()
    print(keys)
    with open(out_fp, "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)

if __name__ == '__main__':

    out_dir = "scarf/out"

    node_dirs = [
        "/ganglia/devicedata-2022-11-21-16",
        "/ganglia/devicedata-2022-11-22-00",
        "/ganglia/devicedata-2022-11-22-08",
        "/ganglia/devicedata-2022-11-22-16",
    ]

    all_data = []
    for dir in node_dirs:
        all_data.extend(read_scarf_devices(dir, "node"))
    write_file(all_data, os.path.join(out_dir, "nodes.csv"))

    device_dirs = [
        "/lnms/devicedata-2022-11-21-16",
        "/lnms/devicedata-2022-11-22-00",
        "/lnms/devicedata-2022-11-22-08",
        "/lnms/devicedata-2022-11-22-16",
    ]

    all_data = []
    for dir in device_dirs:
        all_data.extend(read_scarf_devices(dir, "network_device"))
    write_file(all_data, os.path.join(out_dir, "device.csv"))

    all_data = []
    for dir in device_dirs:
        all_data.extend(read_scarf_devices(dir, "network_device_other"))
    write_file(all_data, os.path.join(out_dir, "device_other.csv"))

    pdu_dirs = [
        "/lnms/pdudata-2022-11-21-16",
        "/lnms/pdudata-2022-11-22-00",
        "/lnms/pdudata-2022-11-22-08",
        "/lnms/pdudata-2022-11-22-16",
    ]

    all_data = []
    for dir in device_dirs:
        all_data.extend(read_scarf_devices(dir, "pdu"))
    write_file(all_data, os.path.join(out_dir, "pdu.csv"))


