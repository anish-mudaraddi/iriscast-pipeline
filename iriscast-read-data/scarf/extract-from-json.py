import json
import csv

def parse_node_list(node_list):
    full_node_list = []
    if '[' in node_list:
        node_parts = node_list.split('[')[1].split(']')[0]
        node_prefix =  node_list.split('[')[0]
        for node_part in node_parts.split(","):
            n_list = node_part.split("-")
            if len(n_list) == 2:
                for i in range(int(n_list[0]), int(n_list[1]) + 1):
                    pad = 0
                    if len(str(i)) < 3:
                        pad = 3 - len(str(i))
                    full_node_list.append("%s%s" % (node_prefix, str(i).zfill(pad)))
            else:
                full_node_list.append("%s%s" % (node_prefix, n_list[0]))
    else:
        full_node_list = [node_list]
    return full_node_list


if __name__ == '__main__':
    inp_file = "scarf/sacct-output20221121-20221122.json"
    out_file_job = "scarf/scarf-slurm.csv"

    with open(inp_file, 'r') as slurm_dict:
        data = slurm_dict.read()

    slurm_data = json.loads(data)

    all_job_data = []
    for job in slurm_data["jobs"]:
        job_details = {
            "job_id": job["job_id"],
            "job_name": job["name"],
            "group": job["group"],
            "user": job["user"],
            "start": job["time"]["start"],
            "end": job["time"]["end"] if job["time"]["end"] != 0 else "",
            "job_state": job["state"]["current"],
            "nodes": ",".join(parse_node_list(job["nodes"])),
            "nnodes": job["allocation_nodes"],
            "allocated_cpu": "",
            "allocated_mem": "",
            "allocated_node": "",
            "allocated_gres": "",
            "working_directory": job["working_directory"],
            "elapsed_time": job["time"]["elapsed"],
            "cpu_time_raw": job["time"]["elapsed"] * job["required"]["CPUs"]
        }
        res_req = [i['type'] for i in job["tres"]["requested"]]
        res_req.remove('billing')

        for r in res_req:
            if job["tres"]["allocated"]:
                job_details.update({
                    "allocated_%s"% r: [
                        el["count"] for el in job["tres"]["allocated"] if el['type'] == r
                    ][0]
                })

        all_job_data.append(job_details)

    keys = all_job_data[0].keys()
    with open(out_file_job, "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_job_data)
