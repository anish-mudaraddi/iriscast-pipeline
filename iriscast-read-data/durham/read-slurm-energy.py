import datetime


if __name__ == '__main__':

    """
        read job energy usage data. Combine slurmsummary.txt info with slurmjobtimes.txt to create one entry per job.
        only collect 
        
        create two files:
            - one which contains jobs which start and end times overlapped with snapshot period
            - one which contains invalid jobs (jobs which contained no timestamps or fell outside of time period
        
        script to be run before calculating durham job data        
    """

    summary_inp_file = "slurmsummary.txt"
    job_times_file = "slurmjobtimes.txt"
    valid_jobs_file = "durham-job-energy.csv"
    invalid_jobs_file = "durham-slurm-invalid-jobs.csv"

    slurm_summary = dict()
    with open(summary_inp_file, 'r+') as txt_file:
        for line in txt_file:
            line = line.rstrip()
            attrs = line.split(" ")
            slurm_summary[attrs[0]] = {
                "id": attrs[0],
                "energy_used": attrs[1],
                "nnodes": attrs[2],
                "duration": attrs[3],
                "project": attrs[5],
                "partition": attrs[6]
            }

    with open(job_times_file, 'r') as txt_file:
        for line in txt_file:
            line = line.rstrip()
            attrs = line.split(" ")
            slurm_summary[attrs[0]].update({
                "start": int(datetime.datetime.fromisoformat(attrs[-2]).timestamp()),
                "end": int(datetime.datetime.fromisoformat(attrs[-1]).timestamp())
            })

    all_data = []
    for k, v in slurm_summary.items():
        all_data.append(v)

    start = 1669046400
    end = 1669132800

    keys = all_data[0].keys()
    with open(valid_jobs_file, "w") as f:
        with open(invalid_jobs_file, "w") as f2:
            f.write(",".join(list(keys))+"\n")
            f2.write(",".join(list(keys)[:-2])+"\n")
            for values in all_data:
                i = ",".join([str(v) for v in values.values() if values.keys() == keys])
                if i:
                    if start <= int(values["end"]) and int(values["start"]) <= end:
                        f.write(i+"\n")
                else:
                    f2.write(",".join([str(v) for v in values.values()])+"\n")