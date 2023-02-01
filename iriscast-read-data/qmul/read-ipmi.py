import csv
import os
import pathlib

if __name__ == '__main__':
    inp_dir = "qmul-ipmi"
    out_dir = "qmul-ipmi-csvs"

    # get information on nodes (currently only which rack it belongs to)
    qmul_info = "qmul-info.csv"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    assert os.path.exists(inp_dir), "input dir does not exist"

    all_qmul_info = {}
    with open(qmul_info, "w") as qmul_info_file:
        reader = csv.DictReader(qmul_info_file)
        for row in reader:
            all_qmul_info[row["hostname"]] = row["rack"]

    for dir_path in [f.path for f in os.scandir(inp_dir) if f.is_dir()]:
        print(dir_path)
        hostname = os.path.basename(os.path.basename(dir_path))
        log_data = []

        for log_file in os.listdir(dir_path):
            if log_file == "thisnodepower.log":
                with open(os.path.join(dir_path, log_file), 'r') as lf:
                    contents = lf.readlines()
                    headers = contents[0].rstrip().split(",")
                    contents = contents[1:]

                prev_watt_hour = 0
                record_data = []
                for record in contents:
                    r_list = record.rstrip().split(',')
                    record_entry_dict = {
                        headers[j]: r_list[j] for j in range(len(headers))
                    }

                    if prev_watt_hour == 0:
                        record_entry_dict.update({
                            "watt_hours": 0
                        })
                    else:
                        record_entry_dict.update({
                            "watt_hours": int(record_entry_dict["Wh"]) - int(prev_watt_hour)
                        })

                    record_entry_dict.update({
                        "rack": all_qmul_info[hostname]
                    })

                    prev_watt_hour = record_entry_dict["Wh"]
                    record_data.append(record_entry_dict)

                keys = record_data[0].keys()
                with open(os.path.join(out_dir, "thisnodepower%s.csv" % hostname), "w") as f:
                    dict_writer = csv.DictWriter(f, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(record_data)