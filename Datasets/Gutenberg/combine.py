import os
from concurrent.futures import ThreadPoolExecutor

BATCH_SIZE = 1000
BUFFER_SIZE = 8192000  # 8MB buffer

# Function to process a single file and return the trimmed content as a string
def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', buffering=BUFFER_SIZE) as f:
            file_content = f.read().strip()  # Remove leading/trailing whitespace
            
            # You can customize what "trim" means here; for example, removing empty lines:
            # file_content = '\n'.join(line.strip() for line in file_content.splitlines() if line.strip())
            
            # Simulate the JavaScript trim (trimming whitespace from the start and end of content)
            if len(file_content) > 0:
                # If content is too large (you can define the size limit here if needed)
                # For example, limiting it to 5MB in size (about 5 * 1024 * 1024 bytes)
                max_size = 5 * 1024 * 1024  # Example: 5MB size limit for the trimmed content
                if len(file_content.encode('utf-8')) > max_size:
                    file_content = file_content[:max_size]  # Truncate content to fit within max_size

            result = f"--- Start of {os.path.basename(file_path)} ---\n"
            result += file_content
            result += f"\n--- End of {os.path.basename(file_path)} ---\n\n"
            return result
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""  # Return empty string if an error occurs

source_folder = r'gutenberg_books'
destination_folder = r'processedFolder'

# Create the destination folder if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

files = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith('.txt')]

# List to accumulate all processed results
combined_content = []

# Process each file in batches
with ThreadPoolExecutor() as executor:
    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i:i + BATCH_SIZE]
        
        # Map the files to the process_file function using executor
        results = executor.map(process_file, batch)
        
        # Add the processed results to the combined content list
        for result in results:
            combined_content.append(result)

# Write the combined content to one large file
combined_file_path = os.path.join(os.getcwd(), 'combined_processed.txt')
with open(combined_file_path, 'w', encoding='utf-8', buffering=BUFFER_SIZE) as f:
    f.write("\n".join(combined_content))  # Combine all processed content into one file

print(f"All processed files have been combined into {combined_file_path}")