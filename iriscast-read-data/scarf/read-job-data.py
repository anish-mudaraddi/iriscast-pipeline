import csv
import datetime
import math

if __name__ == '__main__':
    inp_file = "scarf/scarf-slurm.csv"
    out_dir = "scarf/scarf-job"
    interval_seconds = 900

    with open(inp_file, encoding='UTF8') as job_info_file:
        reader = csv.DictReader(job_info_file, delimiter=";")
        for row in reader:
            if row['allocated_cpu'] and row['allocated_mem']:
                # get job start
                node_list = row["nodes"].split(",")
                nnodes = len(node_list)
                total_mem = int(row["allocated_mem"]) if row["allocated_mem"] else 0
                ncpus = int(row['allocated_cpu']) / int(row['allocated_node'])
                mem = int(row['allocated_mem']) / nnodes

                start_unixtime = int(row["start"])
                # get job duration in seconds (rounded up to nearest 10 seconds)
                duration_seconds = math.ceil(int(row["elapsed_time"]) / interval_seconds) * interval_seconds
                total_cpu_time_per_interval = 900
                total_cpu_time_last_interval = int(row['elapsed_time']) % interval_seconds

                job_info = []
                for node in node_list:
                    for i in range(start_unixtime, (start_unixtime+duration_seconds), interval_seconds):

                        job_info.append({
                            "unixtime": i,
                            "job_id": row['job_id'],
                            "job_name": row['job_name'],
                            "group": row['group'],
                            "mem": mem,
                            "node": node,
                            "ncpus": ncpus,
                            "cpu_time": total_cpu_time_per_interval * ncpus,
                        })

                    job_info.append({
                        "unixtime": start_unixtime+int(row["elapsed_time"]),
                        "job_id": row['job_id'],
                        "job_name": row['job_name'],
                        "group": row['group'],
                        "mem": mem,
                        "node": node,
                        "ncpus": ncpus,
                        "cpu_time": total_cpu_time_last_interval * ncpus,
                    })

                keys = job_info[0].keys()
                with open("%s\%s.csv" % (out_dir, row['job_id']), 'w') as f:
                    dict_writer = csv.DictWriter(f, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(job_info)
