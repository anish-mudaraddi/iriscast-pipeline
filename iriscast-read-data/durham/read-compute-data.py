import os
import csv


"""
    Reads Durham Compute Data and outputs formatted csv. 
    COSMA7 and COSMA8 node info given as txt file with schema
    
    node id, timestamp, cumulative kwh
    
    
    Calculates watt hours from cumulative kwh. (energy - prev energy) * 1000
    Multiiplies COSMA8 nodes by 2/3 to account for IPMI bios bug
"""

if __name__ == '__main__':
    inp_dir = "durham/nodes/"
    out_dir = "durham/nodes-updated/"

    list_of_files = []
    for root, dirs, files in os.walk(inp_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))

    for filepath in list_of_files:
        print("running file: %s" % f)
        compute_id = os.path.basename(filepath).split(".txt")[0]
        efiles_dict = []
        with open(filepath, "r+") as f:
            prev_line_energy = None
            for line in f:
                timestamp, energy = line.split(":")
                energy = float(energy.split('kWh')[0])
                if prev_line_energy:
                    watt_hours = round((energy - prev_line_energy) * 1000, 3)
                else:
                    watt_hours = 0

                if compute_id[1] == "8":
                    watt_hours = watt_hours * 2 / 3

                efiles_dict.append({
                    "id": compute_id,
                    "unixtime": timestamp.strip(),
                    "cumulative_energy": energy,
                    "watt_hours": watt_hours,
                })
                prev_line_energy = energy

        keys = efiles_dict[0].keys()
        with open(os.path.join(out_dir, ("%s.csv" % compute_id)), "w") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(efiles_dict)