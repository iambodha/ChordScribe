import json
import re
import matplotlib.pyplot as plt

with open("scored_tokens.json", "r", encoding='utf-8') as file:
    data = json.load(file)

roman_numerals_pattern = r"^(?=[MDCLXVI])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"

filtered_data = {
    k: v
    for k, v in data.items()
    if v["score"] is not None
    and len(k) > 2
    and not re.fullmatch(roman_numerals_pattern, k, re.IGNORECASE)
}

sorted_data = dict(sorted(filtered_data.items(), key=lambda item: item[1]["score"], reverse=True))

with open("filtered_scored_tokens.json", "w", encoding='utf-8') as file:
    json.dump(sorted_data, file, indent=4)

scores = [v["score"] for v in sorted_data.values()]
plt.hist(scores, bins=20, edgecolor="black")
plt.title("Score Distribution")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.show()

count = sum(1 for v in sorted_data.values() if v["frequency"] > 1 and v["score"] > 1)
print(f"Words with frequency and score greater than 1: {count}")