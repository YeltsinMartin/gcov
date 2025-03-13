import re
import os 

# Example usage:
header_file = b'C:\WindRiver\workspace\gnc_sw\gnc_vxworks\src\autocode\Codegen\GNC_OBC_ert_rtw\GNC_OBC_types.h'

#now go decrypt the required input in to format
input_order_list = ['bus_servicer','bus_client_reduced','bus_nav2_3','bus_time','bus_actuators_model','bus_sensors_10Hz','bus_lidar_sensor','bus_lrf_sensor','bus_rw_sensor','bus_servicer_sys_tmt']

#input_order_list = ['bus_servicer_sys_tmt']

input_data_size = { 'int8_T'    :1,
                    'uint8_T'    :1,
                    'int16_T'   : 2,
                    'uint16_T'  : 2,
                    'int32_T'   : 4,
                    'uint32_T'  : 4,
                    'real32_T'  : 4,
                    'real64_T'  : 8,
                    'real_T'    : 8,
                    'time_T'    : 8,
                    'boolean_T' : 1,
                    'int_T'     : 4,
                    'uint_T'    : 4,
                    'ulong_T'   : 4,
                    'char_T'    : 1,
                    'uchar_T'   : 1,
                    'byte_T'    : 1,
                    'END'       : 0}

packed_schema_list= []

def parse_struct_from_header(header_file):
    struct_dict = {}
    
    with open(header_file, 'r') as file:
        content = file.read()
        
        # Define a regular expression pattern to match typedef struct declarations
        pattern = re.compile(r'typedef\s+struct\s*\{([^}]*)\}\s*(\w+)\s*;', re.MULTILINE)
        
        # Find all typedef struct declarations in the file
        structs = pattern.findall(content)
        
        # Iterate over each typedef struct found in the file
        for struct_content, struct_name in structs:
            # Remove any comments from the struct content
            struct_content = re.sub(r'//.*?\n|/\*.*?\*/', '', struct_content, flags=re.DOTALL)
            struct_content = struct_content.replace('\n    ', '') #.replace('\t', '').replace(' ', '')
            struct_content = struct_content.split(';')
            # Add the struct to the dictionary
            struct_dict[struct_name] = struct_content
            
    return struct_dict

def findDataType(key):
    ls = []
    if key not in input_data_size.keys(): 
        if not 'Enum' in key:  
            struct_content_list = struct_dict[key]
            ls.append('END')
            for dataType in struct_content_list:
                ls.extend(findDataType(dataType))
        else:
            ls.append('uint32_T')
    else:
        return [key]
    
    return ls

def calculate_reminder(value, divisor):
    remainder = value % divisor
    if remainder == 0:
        return 0
    else:
        return divisor - remainder

def update_file(file_path):
    
    with open(file_path, 'rb') as input_file:
        original_data = input_file.read()

    modified_data = bytearray(original_data)

    #read the binary file and add appropriate zeros to the binary data
    file_pos = 0
    #count memeory 
    for ptr1 in range(len(packed_schema_list)):
        
        dataType = packed_schema_list[ptr1]
        size = input_data_size[dataType]

        if size % 4 != 0:
            
            file_pos += size
                
        elif size == 8:
            
            padding_size = calculate_reminder(file_pos, 8)
            
            for i in range(padding_size):
                modified_data.insert(file_pos, 0)
                
            file_pos += padding_size
            
            file_pos += size
            
        elif size == 4:
            
            padding_size = calculate_reminder(file_pos, 4)
            
            for i in range(padding_size):
                modified_data.insert(file_pos, 0)

            file_pos += padding_size
            
            file_pos += size

    if file_pos % 8 != 0:
        
        padding_size = calculate_reminder(file_pos, 8)
            
        for i in range(padding_size):
            modified_data.insert(file_pos, 0)
            
        file_pos += padding_size
    
    #new_file_path = file_path.replace("algo_data\\inputs", "algo_data\\inputs\\out")
    
    #print(f"Padded size {new_file_path} : {file_pos} \n")

    with open (file_path, 'wb') as output_file:
        output_file.write(modified_data)

def get_bin_files(folder):
    bin_files = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith('.bin')]
    return bin_files
    
if __name__ == "__main__":
    
    #get input files list
    file_list  = get_bin_files(b"C:\WindRiver\workspace\gnc_sw\algo_data\inputs")
    
    #parse strcut schema from header
    struct_dict = parse_struct_from_header(header_file)
    
    #process the struct contents to elaborate the datatypes, resolve complex struct to basic types
    for struct_name, struct_content in struct_dict.items():
        
        pattern = r'(\w+) \w+\[(\d+)\]'
        
        struct_content_list = []
        
        # Loop through each string in the list
        for value in struct_content:
            # Use the findall method to extract all matches of the pattern in the given string
            matches = re.findall(pattern, value)

            if matches: 
                # Iterate over the matches and print the first word the number of times found in the []
                for datatype, number in matches:
                    struct_content_list.extend([datatype] * int(number))
            else:
                value = value.split(' ')[0]
                if(value != '\n'):
                    struct_content_list.append(value)
        
        struct_dict[struct_name] = struct_content_list

    #create the flattened schema of inputs
    for input in input_order_list:
        for datatype in struct_dict[input]:
            result = findDataType(datatype)
            packed_schema_list.extend(result)

    #compute the size of the packed data with respect to the h file
    #to corss check with file size so that we are not reading wrong data.
    size = 0
    for dataType in packed_schema_list:
        size += input_data_size[dataType]
    print (F"size of decomposed packed structure {size}")


    for file in file_list:
        update_file(file)
    
    with open("strcut_schema.log", 'w') as log_file:
        log_file.write(str(packed_schema_list))
        
    print(set(packed_schema_list))

'''
# Print the parsed struct dictionary
with open ("out.log", 'w') as f:
    
    for struct_name, struct_content in struct_dict.items():
        f.write(f'Struct Name: {struct_name} \t\t')
        #f.write(f'Struct Content: {struct_content}\n')
        
        # Define a regular expression pattern
        pattern = r'(\w+) \w+\[(\d+)\]'

        # Loop through each string in the list
        for value in struct_content:
            # Use the findall method to extract all matches of the pattern in the given string
            matches = re.findall(pattern, value)

            if matches: 
                # Iterate over the matches and print the first word the number of times found in the []
                for datatype, number in matches:
                    datatype = datatype + '\n'
                    f.write( f"{ datatype * int(number)} \n")
            else:
                value = value.split(' ')[0]
                f.write(f'{value}\n') 
'''

