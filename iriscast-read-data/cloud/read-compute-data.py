import csv
import os
import datetime

if __name__ == '__main__':
    """
        Reads Cloud Compute Data and outputs formatted csv. 
        This is not required because this should be handled by the data pipeline.

        If we receive CSV data for Cloud Compute information which we want to transfer into opensearch we use this script

        Calculates watt hours from watts. watts * 1/4 (since readings taken at 15 minute intervals)
        Integrates information about compute node model and rack etc.
    """

    out_file = "cloud/cloud-info.csv"
    inp_file = "cloud/cloud-info-updated.csv"

    # csv file showing cloud device name, type, and rack
    cloud_info = "C:\\Users\\vgc59244\\OneDrive - Science and Technology Facilities Council\\Documents\\IRISCAST\\get-data\\get-cloud-data\\cloud-devices.csv"

    assert os.path.exists(cloud_info), "cloud info file does not exist"
    assert os.path.exists(inp_file), "input file does not exist"

    all_cloud_info = {}
    with open(cloud_info,encoding='UTF8') as cloud_info_file:
        reader = csv.DictReader(cloud_info_file)
        for row in reader:
            all_cloud_info[row["name"]] = {
                "rack": row["rack"],
                "model": row["type"]
            }

    all_data = []
    with open(inp_file, encoding='UTF8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            x = row
            rack = ""
            model = ""
            if x['hostname'] in all_cloud_info.keys():
                rack = all_cloud_info[x['hostname']]['rack']
                model = all_cloud_info[x['hostname']]['model']

            x.update({
                'watt_hours': float(x['current_power']) * 1/4,
                'rack': rack,
                'model': model,
                'timestamp': int(datetime.datetime.strptime(row['timestamp'], "%b %d, %Y @ %H:%M:%S.%f").timestamp()),
            })
            all_data.append(x)

    keys = all_data[0].keys()
    with open(out_file, "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)


