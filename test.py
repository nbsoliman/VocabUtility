import json

# Load the JSON data from the file
with open('C:/Users/soliman-nicholas/OneDrive - AirbusDSGS/Documents/etc/k/data/all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Iterate over all items in the dictionary and add a 'known' variable with value False
for item in data:
    item['known'] = False

# Optionally, save the modified data back to the file
with open('C:/Users/soliman-nicholas/OneDrive - AirbusDSGS/Documents/etc/k/data/all.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)