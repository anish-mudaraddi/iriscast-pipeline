import csv
import os
import datetime

if __name__ == '__main__':
    """
        Reads Cambridge Data and outputs individual csvs for each node into directory
        Cambridge Data consisted of a csv file where the schema was the following:
            
            Timestamp Host1_attr1, Host1_attr2 ... Host2_attr1, Host2_attr2 ... etc
        
    """

    out_dir = "cambridge/nodes"
    inp_file = "cambridge/cambridge.csv"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    assert os.path.exists(inp_file), "input file does not exist"

    with open(inp_file, 'r') as f:
        content = f.readlines()

    all_headers = content[0].strip().split(',')

    # get number of nodes, 13 unique fields
    num_nodes = int((len(all_headers) - 1) / 12)

    headers = content[0].strip().split(',')[1:13]

    all_data = {i:[] for i in range(1, num_nodes+1)}

    # read in line by line and populate dictionary
    # need to read in full file - each line contains entry for each node at specific timestamp
    for line in content[1:]:
        line_parts = line.strip().split(',')
        timestamp = int(datetime.datetime.strptime(line_parts[0], '%d/%m/%Y %H:%M').timestamp())
        curr_part = 1
        node = 1

        while curr_part < len(line_parts) - 2:
            node_content = dict()
            node_content['unixtime'] = timestamp
            node_content['node'] = "node_%s" % node
            for header in headers:
                node_content[header.lower()] = line_parts[curr_part]
                curr_part += 1

            node_content['ram cache + buffer'] = round(((float(node_content['ram cache + buffer']) / 1024) / 1024) / 1024, 3)
            node_content['ram total'] = round(((float(node_content['ram total']) / 1024) / 1024) / 1024, 3)
            node_content['ram used'] = round(((float(node_content['ram used']) / 1024) / 1024) / 1024, 3)
            node_content['ram free'] = round(((float(node_content['ram free']) / 1024) / 1024) / 1024, 3)
            node_content['watt_hours'] = int(node_content['power']) * (1/60) if node_content['power'] else ''

            all_data[node].append(node_content)
            node += 1

    keys = all_data[1][0].keys()
    for k,v in all_data.items():
        with open('%s/node_%s.csv' % (out_dir, k), 'w') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(v)



