import csv
import os
import datetime
from xml.etree.ElementTree import parse

def read_xml(filepath):
    """ parse xml file for cosma7 pdus"""
    print(filepath)
    document = parse(filepath)
    all_data = []
    pdu_kws = ["voltsA", "voltsB", "voltsC",
                  "ampsA", "ampsB", "ampsC",
                  "kwA", "kwB", "kwC"]

    date, time = os.path.basename(filepath).split(".xml")[0].split("power")[1].split("_")
    timestamp = datetime.datetime(int("20%s" % date[0:2]), int(date[2:4]), int(date[4:6]),
                         int(time[0:2]), int(time[2:4]), int(time[4:6])).timestamp()

    for pdu_xml in document.iterfind('response'):

        pdu_data = {i: float(pdu_xml.findtext(i)) for i in pdu_kws}

        pdu_data.update({
            "timestamp": timestamp,
            "host": pdu_xml.attrib['id'],
            "watt_hours": round(1000 * ((pdu_data["kwA"] + pdu_data["kwB"] + pdu_data["kwC"]) * 1/12), 2),
        })
        all_data.append(pdu_data)

    return all_data

def read_csv(filepath, hostname_prefix, recs_per_pdu):
    """ parse cosma8 or cosma67 storage csv file.
    combine each bank entry for single pdu into one entry """
    all_data = []
    with open(filepath, encoding='UTF8') as csv_file:
        reader = csv.DictReader(csv_file)

        rec_inc = 1
        record = {}
        total_watts = 0
        total_watt_hour = 0
        for row in reader:
            try:
                float(row['current'])
            except ValueError:
                record["bank_%s_amps" % row['bank']] = ""
                record["bank_%s_watts" % row['bank']] = ""
                record["bank_%s_wh" % row['bank']] = ""
            else:
                record["bank_%s_amps" % row['bank']] = row['current']
                watts = round(float(row['current']) * 230, 3)
                watt_hour = round(watts * 1 / 12, 3)

                record["bank_%s_watts" % row['bank']] = watts
                record["bank_%s_wh" % row['bank']] = watt_hour

                total_watts += watts
                total_watt_hour += watt_hour
            finally:
                if rec_inc == recs_per_pdu:
                    record['unixtime'] = int(row['timestamp'])
                    record['hostname'] = "%s.%s" % (hostname_prefix, row['pdu_id'])
                    record["total_watts"] = round(total_watts, 3)
                    record["total_watt_hours"] = round(total_watt_hour, 3)

                    all_data.append(record)

                    record = {}
                    rec_inc = 0
                    total_watt_hour = 0
                    total_watts = 0
                rec_inc += 1
    return all_data


def read_pdu_data(filepaths, type):
    """ read pdu data from file"""
    all_data = []
    print("reading filepaths for type %s" % type)
    for filepath in filepaths:
        if type == "cosma7":
            # cosma7 provided in xml
            all_data.extend(read_xml(filepath))
        if type == "cosma8":
            # cosma8 provided as csv with each pdu having 6 entries (1 per bank)
            all_data.extend(read_csv(filepath, "172.16.188", 6))
        if type == "cosma67storage":
            # cosma8 provided as csv with each pdu having 2 entries (1 per bank)
            all_data.extend(read_csv(filepath, "172.16.178", 2))
    return all_data

def write_file(out_path, data):
    """ write csv file """
    keys = data[0].keys()
    with open(out_path, "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


if __name__ == '__main__':

    out_dir = "durham/"
    storage_pdus_inp_file = "c67storage/powerc67storage_2211.csv",

    storage_data = read_pdu_data(storage_pdus_inp_file, "cosma67storage")
    write_file(os.path.join(out_dir, "cosmac67storage.csv" ), storage_data)

    cosma7_inp_dirs = [
        "powerusage/221121",
        "powerusage/221121"
    ]

    cosma7_data = []
    for file_dir in cosma7_inp_dirs:
        cosma7_data.extend(read_pdu_data(file_dir, "cosma7"))
    write_file(os.path.join(out_dir, "cosma7.csv"), cosma7_data)

    cosma8_inp_dir = "powerusage/c8",
    cosma8_data = read_pdu_data(cosma8_inp_dir, "cosma8")
    write_file(os.path.join(out_dir, "cosma8.csv"), cosma8_data)