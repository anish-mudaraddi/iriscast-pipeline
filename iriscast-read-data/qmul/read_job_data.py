import csv
import datetime
import math

def read_mem(mem_string):
    if mem_string[-1] == 'M':
        return int(mem_string[:-1])
    if mem_string[-1] == 'G':
        return (int(mem_string[:-1]) * 1024)


if __name__ == '__main__':

    inp_files = [
        "qmul/sacct-late-alloc.log",
        "qmul/sacct-early-alloc.log",
        "qmul/sacct-day-alloc.log"
    ]

    out_dir = "qmul-job"
    qmul_info = "qmul-info.csv"

    interval_seconds = 900

    all_qmul_info = {}
    with open(qmul_info, "w") as qmul_info_file:
        reader = csv.DictReader(qmul_info_file)
        for row in reader:
            all_qmul_info[row["hostname"]] = row["rack"]

    for f in inp_files:
        with open(f, encoding='UTF8') as job_info_file:
            reader = csv.DictReader(job_info_file, delimiter="|")
            for row in reader:
                # get job start
                node = row["NodeList"]
                rack = all_qmul_info[node]
                total_mem = read_mem(row["ReqMem"])

                start_unixtime = int(datetime.datetime.strptime(row['Start'], "%b %d, %Y @ %H:%M:%S.%f").timestamp())

                # get job duration in seconds (rounded up to nearest 10 seconds)
                duration_seconds = math.ceil(int(row["ElapsedRaw"]) / interval_seconds) * interval_seconds
                total_cpu_time_per_interval = interval_seconds
                total_cpu_time_last_interval = int(row["ElapsedRaw"]) % interval_seconds

                job_info = []
                for i in range(start_unixtime, (start_unixtime+duration_seconds), interval_seconds):

                    job_info.append({
                        "unixtime": i,
                        "job_id": row['JobID'],
                        "job_name": row['JobName'],
                        "group": row['Group'],
                        "mem": total_mem,
                        "node": node,
                        "ncpus": int(row['NCPUS']),
                        "cpu_time": total_cpu_time_per_interval * int(row['NCPUS']),
                        "rack": rack
                    })

                job_info.append({
                    "unixtime": start_unixtime+int(row['ElapsedRaw']),
                    "job_id": row['JobID'],
                    "job_name": row['JobName'],
                    "group": row['Group'],
                    "mem": total_mem,
                    "node": node,
                    "ncpus": int(row['NCPUS']),
                    "cpu_time": total_cpu_time_last_interval * int(row['NCPUS']),
                    "rack": rack
                })

                keys = job_info[0].keys()
                with open("%s\%s.csv" % (out_dir, row['JobID']), 'w') as f:
                    dict_writer = csv.DictWriter(f, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(job_info)
