import csv
import datetime

# read in csv
inp_dir = "qmul/rackpower.csv"
out_dir = "qmul/updated_rackpower.csv"

updated_content = []
with open(inp_dir, 'r') as rack_file:
    content = csv.DictReader(rack_file)
    # displaying the contents of the CSV file
    prev_energy_dict = {}

    for row in content:
        new_row = {
            "unixtime": int(row['unixtime']),
            "rack": row['rack'],
            "cumulative watt hours": int(row['Wh']),
        }
        if row['rack'] not in prev_energy_dict.keys():
            new_row['watt hours'] = 0
        else:
            new_row['watt hours'] = int(row['Wh']) - prev_energy_dict[new_row['rack']]

        prev_energy_dict['rack'] = int(row['Wh'])

        updated_content.append(new_row)

keys = updated_content[0].keys()
with open(out_dir, "w") as f:
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(updated_content)