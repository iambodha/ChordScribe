import json

# Load token_frequencies JSON from file
with open('token_frequencies.json', 'r', encoding='utf-8') as file:
    token_frequencies = json.load(file)

# Function to filter tokens
def filter_tokens(token_frequencies):
    filtered_tokens = {}

    for token, frequency in token_frequencies.items():
        # Ensure "_" token is retained explicitly
        if token == "_":
            filtered_tokens[token] = frequency
            continue

        # Remove underscores from tokens like _vk_
        if token.startswith("_") and token.endswith("_"):
            token = token.strip("_")

        # Remove tokens that start or end with an underscore, like Zamudio_ or _hi
        if token.startswith("_") or token.endswith("_"):
            continue

        # Remove tokens made up of capital letters and numbers only
        if token.isupper() and token.isalnum() and any(char.isdigit() for char in token):
            continue

        # Remove tokens made up of only numbers with length 50 or greater
        if token.isdigit() and len(token) >= 50:
            continue

        # Remove tokens made up of only numbers with specific lengths
        if token.isdigit() and len(token) in [7, 10]:
            continue

        # Add the token to the filtered dictionary
        filtered_tokens[token] = frequency

    return filtered_tokens

# Apply the filter
token_frequencies = filter_tokens(token_frequencies)

# Sort tokens by frequency in descending order
token_frequencies = dict(sorted(token_frequencies.items(), key=lambda item: item[1], reverse=True))

# Save the filtered tokens to a new JSON file
with open('filtered_token_frequencies.json', 'w', encoding='utf-8') as file:
    json.dump(token_frequencies, file, ensure_ascii=False, indent=4)

print("Filtered tokens saved to 'filtered_token_frequencies.json'")