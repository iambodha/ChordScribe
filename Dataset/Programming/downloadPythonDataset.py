import os
import pandas as pd

# You need to manually download the dataset from Zenodo (URL: https://zenodo.org/record/6607065) 
# and place the extracted files in the same directory as this script.

def process_csv_and_save_code(csv_file):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        with open('python_Data.txt', 'a', encoding='utf-8') as code_file:
            for index, row in df.iterrows():
                code = row['code_block']
                if isinstance(code, str):
                    code_file.write(code + "\n\n")
                else:
                    print(f"Row {index + 1} in {csv_file}: No Python code found.")
        
        print(f"Python code from {csv_file} has been saved to python_Data.txt")
    else:
        print(f"Error: {csv_file} not found in the current directory. Please download and place the file manually.")

def main():
    csv_files = ['сode_blocks_upto_20.csv', 'сode_blocks_21.csv']
    
    for csv_file in csv_files:
        process_csv_and_save_code(csv_file)

if __name__ == "__main__":
    main()
