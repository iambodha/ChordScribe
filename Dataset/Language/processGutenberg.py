import os
from concurrent.futures import ThreadPoolExecutor

BATCH_SIZE = 1000
BUFFER_SIZE = 8192000

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', buffering=BUFFER_SIZE) as f:
            file_content = f.read().strip()
            if len(file_content) > 0:
                max_size = 5 * 1024 * 1024
                if len(file_content.encode('utf-8')) > max_size:
                    file_content = file_content[:max_size]

            result = f"--- Start of {os.path.basename(file_path)} ---\n"
            result += file_content
            result += f"\n--- End of {os.path.basename(file_path)} ---\n\n"
            return result
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""

source_folder = r'gutenberg_books'
destination_folder = r'processedFolder'

if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

files = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith('.txt')]

combined_content = []

with ThreadPoolExecutor() as executor:
    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i:i + BATCH_SIZE]
        results = executor.map(process_file, batch)
        for result in results:
            combined_content.append(result)

combined_file_path = os.path.join(os.getcwd(), 'combined_processed.txt')
if not os.path.exists(os.path.dirname(combined_file_path)):
    os.makedirs(os.path.dirname(combined_file_path))

with open(combined_file_path, 'w', encoding='utf-8', buffering=BUFFER_SIZE) as f:
    f.write("\n".join(combined_content))

print(f"All processed files have been combined into {combined_file_path}")
