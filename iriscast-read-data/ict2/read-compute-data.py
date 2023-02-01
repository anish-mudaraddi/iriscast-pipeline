import csv
import os


if __name__ == '__main__':
    """
        Reads Imperial College Tier 2 compute data and outputs csv
        
        Calculated watt hours from instantaneous power
            - inconsistent interval period - so calculated number of seconds between intervals 
            and used that to calculate watt hours
    """

    inp_file = "ict2/myresults.csv"
    out_file = "ict2/ic-compute.csv"


    assert os.path.exists(inp_file), "input file does not exist"

    all_data = []
    with open(inp_file, encoding='UTF8') as csv_file:
        reader = csv.DictReader(csv_file)

        # keep track of previously read timestamp for each host
        host_prev_timestamp = {}

        # iterate through the csv file
        for row in reader:
            x = row

            # set timestamp to 0 if first read for host
            if x["hostip"] not in host_prev_timestamp:
                host_prev_timestamp[x["hostip"]] = 0

            # if timestamp is 0, then watt hours 0
            if not x["watts"] or host_prev_timestamp[x["hostip"]] == 0:
                x["watt_hours"] = 0

            else:
                # work out interval and use that to work out watt hours
                duration_seconds = (int(x["unixtime"]) - host_prev_timestamp[x['hostip']])
                x["watt_hours"] = round(int(row["watts"]) * (duration_seconds/3600),3)

            # set current timestamp to previous timestamp
            host_prev_timestamp[x["hostip"]] = int(x["unixtime"])
            all_data.append(x)

    # write new file
    keys = all_data[0].keys()
    with open(out_file, "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)


