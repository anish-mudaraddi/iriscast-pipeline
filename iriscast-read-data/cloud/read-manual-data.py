import csv
import os
import re
import datetime

def read_file(filepath):
    with open(filepath, "r") as f:
        content = f.readlines()

    def get_val(stat, val):
        return {
            "current_power": lambda a: {
                "current_power": re.search("[0-9]+", a).group(0)
            },
            "minimum_power_over_sampling_duration": lambda a: {
                "min": re.search("[0-9]+", a).group(0)
            },
            "maximum_power_over_sampling_duration": lambda a: {
                "max": re.search("[0-9]+", a).group(0)
            },
            "average_power_over_sampling_period": lambda a: {
                "average": re.search("[0-9]+", a).group(0)
            },
            "statistics_reporting_time_period": lambda a: {
                "sampling_period": re.search("[0-9]+", a).group(0)
            },
        }.get(stat, lambda a: None)(val)

    power_stats = {}
    for line in content:
        line_str = line.split(":")
        stat = line_str[0].strip().lower().replace(" ", "_")
        val = ":".join([l for l in line_str[1:]]).strip()
        res = get_val(stat, val)
        if res:
            power_stats.update(res)

    power_stats["hostname"] = "%s.nubes.rl.ac.uk" % os.path.basename(
        os.path.dirname(filepath))
    power_stats["timestamp"] = {
        "power211122-00%3A00run": datetime.datetime(2022, 11, 21, 0, 0),
        "power211122-16%3A00run": datetime.datetime(2022, 11, 21, 16, 0),
        "power221122-08%3A00run": datetime.datetime(2022, 11, 22, 0, 0),
        "power221122-16%3A00run": datetime.datetime(2022, 11, 22, 16, 0),
    }.get(os.path.basename(filepath), datetime.datetime.now()).timestamp()

    return power_stats


if __name__ == '__main__':
    """
        Reads Cloud Control Plane and Storage manual checks and outputs formatted csv.
        Since Manual checks made intermittently, calculate average Watts 
            and create 15 minute intervals with average watt_hours at each interval

        Calculates watt hours from watts. watts * 1/4 (since readings taken at 15 minute intervals)
        Integrates info from cloud info
        
    """

    inp_dir = "cloud/manaul-checks"
    out_dir = "cloud/"

    # csv file showing cloud device name, type, and rack
    cloud_info = "cloud/cloud-devices.csv"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    all_cloud_info = {}
    with open(cloud_info, encoding='UTF8') as cloud_info_file:
        reader = csv.DictReader(cloud_info_file)
        for row in reader:
            all_cloud_info[row["name"]] = {
                "model": row["type"],
                "rack": row["rack"]
            }

    list_of_files = []
    for root, dirs, files in os.walk(inp_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))

    cloud_list = []
    storage_list = []
    for f in list_of_files:
        power_stats = read_file(f)

        power_stats.update({
            "rack": all_cloud_info[power_stats["hostname"]]["rack"],
            "model": all_cloud_info[power_stats["hostname"]]["model"]

        })

        if power_stats["hostname"].split(".")[0] in [
            "galera1", "galera2", "galera3"
        ]:
            cloud_list.append(read_file(f))
        else:
            storage_list.append(read_file(f))

    # write files
    keys = cloud_list[0].keys()
    with open("%s/cloud-openstack-manual-checks.csv" % (out_dir), 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(cloud_list)

    keys = storage_list[0].keys()
    with open("%s/cloud-storage-manual-checks.csv" % (out_dir), 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(storage_list)
