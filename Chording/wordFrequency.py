import os
from collections import Counter
import re
import json
import ijson

def process_file_in_chunks(filepath, chunk_size=8192):
    """Process a file in chunks to conserve memory"""
    word_counter = Counter()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Process the file in chunks
            chunk = ""
            while True:
                # Read chunk_size characters
                new_chunk = file.read(chunk_size)
                if not new_chunk:
                    # Process the last chunk
                    words = re.findall(r'\b\w+\b', chunk.lower())
                    word_counter.update(words)
                    break
                
                # Combine with any leftover partial word from previous chunk
                chunk += new_chunk
                
                # Find the last space in the chunk to avoid splitting words
                last_space = chunk.rfind(' ')
                if last_space == -1:
                    continue
                
                # Process complete words
                processable_chunk = chunk[:last_space]
                words = re.findall(r'\b\w+\b', processable_chunk.lower())
                word_counter.update(words)
                
                # Keep the remainder for the next iteration
                chunk = chunk[last_space:]
                
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
    
    return word_counter

def process_files():
    total_counter = Counter()
    
    # Check if text directory exists
    if not os.path.exists('text'):
        print("Error: 'text' directory not found")
        return
    
    # Process each .txt file
    files_processed = 0
    for filename in os.listdir('text'):
        if filename.endswith('.txt'):
            file_path = os.path.join('text', filename)
            file_counter = process_file_in_chunks(file_path)
            total_counter.update(file_counter)
            files_processed += 1
            
            # Periodically save progress for very large datasets
            if files_processed % 100 == 0:
                print(f"Processed {files_processed} files...")
    
    # Convert to a more memory-efficient structure
    # Only keep words that appear more than once to reduce size
    word_freq_dict = {
        "metadata": {
            "total_unique_words": len(total_counter),
            "files_processed": files_processed
        },
        "frequencies": {
            word: count for word, count in total_counter.most_common()
        }
    }
    
    # Write results to JSON file
    try:
        with open('word_frequencies.json', 'w', encoding='utf-8') as output_file:
            json.dump(word_freq_dict, output_file, indent=2)
        
        print(f"Analysis complete. Results written to 'word_frequencies.json'")
        print(f"Total unique words found: {len(total_counter)}")
        print(f"Total files processed: {files_processed}")
        
    except Exception as e:
        print(f"Error writing output file: {str(e)}")

def read_results(n=None):
    """
    Read and display top N results from the JSON file
    If n is None, display all results
    """
    try:
        with open('word_frequencies.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"\nMetadata:")
            print(f"Total unique words: {data['metadata']['total_unique_words']}")
            print(f"Files processed: {data['metadata']['files_processed']}")
            print("\nTop words:")
            
            items = list(data['frequencies'].items())
            if n:
                items = items[:n]
                
            for word, count in items:
                print(f"{word}: {count}")
                
    except FileNotFoundError:
        print("Results file not found. Run the analysis first.")
    except Exception as e:
        print(f"Error reading results: {str(e)}")

if __name__ == "__main__":
    process_files()
    # Display top 10 words after processing
    read_results(10)