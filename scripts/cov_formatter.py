import os 

processed_data = ''''''
with open("coverage.info", 'r') as f:
    data = f.readlines()
    for line in data:
        pos = line.find('C:') 
        if pos != -1:
            line = line[:pos] + line[line.rfind('/')+1:]
        processed_data +=line

with open("coverage.info", 'w') as f:
    f.writelines(processed_data)