import csv
import math

"""
    Calculated Durham Job Data - creates entry every 15 minutes for each job that should be running with 
        average energy usage, 
        total memory allocated, 
        total cpu time 
    used per node 
"""


def read_mem(mem_string):
    """ Converts memory into Megabytes per node """
    if mem_string[-2:] in ['Mn', 'Mc']:
        return int(mem_string[:-2])
    if mem_string[-2:] == 'Gn':
        return (int(mem_string[:-2]) * 1024)

if __name__ == '__main__':

    slurm_alloc_file = "durham/slurm_info.log"
    slurm_energy_file = "durham/durham-slurm.csv"

    out_dir = "C:\\Users\\vgc59244\\Downloads\\durham-job"
    interval_seconds = 900

    job_info = {}
    with open(slurm_energy_file, encoding='UTF8') as energy_file:
        reader = csv.DictReader(energy_file)
        for row in reader:
            job_info[row['id']] = {
                "wh": row['wh'],
                "nnodes": int(row['nnodes']),
                "project": row['project'],
                "partition": row['partition'],
                'start': int(row['start']),
                'end': int(row['end'])
            }
    with open(slurm_alloc_file, encoding='UTF8') as alloc_file:
        reader = csv.DictReader(alloc_file, delimiter='|')
        for row in reader:
            if row['JobID'] in job_info.keys():
                job_info[row['JobID']].update({
                    "ncpus": int(row['NCPUS']),
                    "partition": row['Partition'],
                    "cpu_time": int(row['CPUTimeRAW']),
                    "node_list": row['NodeList'],
                    "mem_alloc": row['ReqMem'],
                    "job_name": row['JobName'],
                    "group": row['Group'],
                    "elapsed_time_raw": int(row['ElapsedRaw'])
                })

    for k, v in job_info.items():

        # get job start
        total_mem = read_mem(v["mem_alloc"])
        node_list = v['node_list'].split(',')
        nnodes = len(node_list)
        ncpus = v['ncpus'] / v['nnodes']
        mem = total_mem / nnodes


        start_unixtime = int(v["start"])
        duration_seconds = math.ceil(int(v['elapsed_time_raw']) / interval_seconds) * interval_seconds

        total_cpu_time_per_interval = interval_seconds
        total_cpu_time_last_interval = int(v["elapsed_time_raw"]) % interval_seconds

        if v['wh']:
            wh_ps = (float(v['wh']) / nnodes) / duration_seconds
        else:
            wh_ps = 0

        all_info = []
        for node in node_list:
            for i in range(start_unixtime, (start_unixtime+duration_seconds), interval_seconds):

                all_info.append({
                    "unixtime": i,
                    "job_id": k,
                    "job_name": v['job_name'],
                    "group": v['group'],
                    "mem": mem,
                    "node": node,
                    "ncpus": ncpus,
                    "cpu_time": total_cpu_time_per_interval * ncpus,
                    "wh": wh_ps * total_cpu_time_per_interval
                })

            all_info.append({
                "unixtime": start_unixtime+int(v["elapsed_time_raw"]),
                "job_id": k,
                "job_name": v['job_name'],
                "group": v['group'],
                "mem": mem,
                "node": node,
                "ncpus": ncpus,
                "cpu_time": total_cpu_time_last_interval * ncpus,
                "wh": wh_ps * total_cpu_time_last_interval
            })

        keys = all_info[0].keys()
        with open("%s\%s.csv" % (out_dir, k), 'w') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_info)

