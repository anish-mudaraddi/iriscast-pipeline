import datetime
import csv
import os
import pathlib


if __name__ == '__main__':

    inp_dir = "C:\\Users\\vgc59244\\Downloads\\qmul-snapshot"
    out_dir = "C:\\Users\\vgc59244\\OneDrive - Science and Technology Facilities Council\\Documents\\IRISCAST\\get-data\\get-qmul-data\\node-log-csvs"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    assert os.path.exists(inp_dir), "input dir does not exist"

    qmul_info = "qmul-info.csv"

    all_qmul_info = {}
    with open(qmul_info, "w") as qmul_info_file:
        reader = csv.DictReader(qmul_info_file)
        for row in reader:
            all_qmul_info[row["hostname"]] = row["rack"]

    # write log files to corresponding csv
    headers = ["avg_mHz", "busy_%", "bzy_mHz", "tsc_mHz",
               "irq", "smi", "poll", "c1", "c1e", "c6", "poll_%",
               "c1_%", "c1e_%", "c6_%", "cpu_%_c1", "cpu_%_c6",
               "core_tmp", "pkg_tmp", "pkg_%_pc2", "pkg_%_pc6",
               "pkg_j",	"ram_j", "pkg_%", "ram_%",
               ]

    for dir_path in [f.path for f in os.scandir(inp_dir) if f.is_dir()]:
        print(dir_path)
        hostname = os.path.basename(os.path.basename(dir_path))
        log_data = []

        for log_file in os.listdir(dir_path):
            # ignore ipmi logs if exist
            if log_file in ["thisnodepower.log", "thisnodepower.csv"]:
                continue

            with open(os.path.join(dir_path, log_file), 'r') as lf:
                contents = lf.readlines()[1:]

            # get timestamp from filename
            ts = datetime.datetime.strptime(
                os.path.basename(log_file).split(".log")[0].split("thisturbostat-")[1].split("+")[0],
                "%Y-%m-%dT%H_%M_%S"
            ).timestamp()

            for i, record in enumerate(contents):
                r_list = record.rstrip().split("\t")
                if len(r_list) != len(headers):
                    print(len(r_list), len(headers))
                    print(r_list)
                    continue
                record_entry_dict = {
                    headers[j]:r_list[j] for j in range(len(headers))
                }

                total_joules = round(float(record_entry_dict["ram_j"]) + float(record_entry_dict["pkg_j"]),3)
                watt_hours = round((total_joules/10) * 1/360, 3)
                record_entry_dict.update({
                    "hostname": hostname,
                    "date_logged": ts + (i*10),
                    "total_joules": total_joules,
                    "watt_hours": watt_hours,
                    "rack": all_qmul_info[hostname]
                })

                log_data.append(record_entry_dict)

        if log_data:
            keys = log_data[0].keys()
            with open(os.path.join(out_dir, "%s.csv" % hostname), "w") as f:
                dict_writer = csv.DictWriter(f, keys)
                dict_writer.writeheader()
                dict_writer.writerows(log_data)
