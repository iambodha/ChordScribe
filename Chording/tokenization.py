import re
import string

def tokenize_text_in_chunks(input_file, output_file, chunk_size=1000):
    """
    Tokenizes text from an input file and writes the tokens to an output file in chunks.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
        chunk_size (int): Number of lines to process per chunk.
    """
    try:
        pattern = rf"\b\w+(?:'\w+)?\b|[{re.escape(string.punctuation)}]"

        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            buffer = []
            for i, line in enumerate(infile):
                # Tokenize the current line
                tokens = re.findall(pattern, line)
                buffer.extend(tokens)

                # Write to file in chunks
                if (i + 1) % chunk_size == 0:
                    outfile.write('\n'.join(buffer) + '\n')
                    buffer = []

            # Write any remaining tokens
            if buffer:
                outfile.write('\n'.join(buffer) + '\n')

        print(f"Tokens have been written to {output_file} in chunks.")
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
input_file = 'D:\\Coding Projects\\ChordScribe\\Dataset\\englishDataset.txt'
output_file = 'tokens.txt'
tokenize_text_in_chunks(input_file, output_file)
