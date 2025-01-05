# main.py
from base_layout import layouts

# Set the user’s selected language
selected_language = "DE"  # Change as needed to test different layouts

# Get the layout for the selected language
current_layout = layouts[selected_language]

# Function to simulate typing a character using the selected layout
def type_character(char):
    """Type a character based on the current layout."""
    return current_layout.get(char, char)  # Use the default char if not found

# Test the layout with sample characters
typed_text = "".join(type_character(char) for char in "keyboard")
print("Typed text in chosen layout:", typed_text)