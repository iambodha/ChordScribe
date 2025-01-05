import json
from collections import Counter
from itertools import islice

def compute_token_frequency_json(input_file, output_file, chunk_size=100000):
    try:
        token_counts = Counter()

        with open(input_file, 'r', encoding='utf-8') as file:
            while True:
                lines = list(islice(file, chunk_size))
                if not lines:
                    break
                stripped_lines = (line.strip() for line in lines)
                token_counts.update(stripped_lines)

        sorted_token_counts = dict(sorted(token_counts.items(), key=lambda item: item[1], reverse=True))

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(sorted_token_counts, file, indent=2)

        print(f"Token frequencies have been written to {output_file}")
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

input_file = 'tokens.txt'
output_file = 'token_frequencies.json'
compute_token_frequency_json(input_file, output_file)
