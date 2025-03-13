import os
import re


def split_gcda_blob(input_file, output_dir):
    """
    Split a single binary gcov gcda output blob into multiple gcda files.

    :param input_file: Path to the input file containing the gcda blob
    :param output_dir: Directory to save the split gcda files
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f:
        blob = f.read()
    
    # Pattern to match the file path and the data between file paths
    pattern = re.compile(rb'(C:\\.*?\.gcda)(.*?)(?=C:\\|$)', re.DOTALL)

    # Find all matches
    matches = pattern.findall(blob)

    with open(os.path.join(output_dir, "log.log") , 'w') as log:
        # Print the matches
        for match in matches:
            file_path = match[0].decode('utf-8', errors='ignore')
            file_name = file_path[file_path.rfind('/')+1:]

            log.write("{}\n".format(file_path))
            
            data = match[1]
            print(f"Gcda files: {file_path}")
            #print(f"Data: {data}")  # Print only the first 100 bytes of data for brevity
            #print()
            final_path = os.path.join(output_dir,file_path[file_path.find('Objects'):file_path.rfind('/')])
            if not os.path.exists(final_path):
                os.makedirs(final_path)
            with open(os.path.join(final_path,file_name), 'wb') as out:
                pos = data.find(b"Gcov End")
                if pos == -1:
                    out.write(data[5:])
                else:
                    out.write(data[5:pos])
    
if __name__ == "__main__":
    
    input_file = b"C:\WindRiver\workspace\gnc_sw\coverage\data\gcov_gnc.bin"  # Replace with the path to your input file
    output_dir = "C:\\WindRiver\\workspace\\gnc_sw\\coverage\\data\\"  # Replace with your desired output directory

    split_gcda_blob(input_file, output_dir)
