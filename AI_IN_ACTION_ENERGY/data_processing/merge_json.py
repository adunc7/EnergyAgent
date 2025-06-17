import json 

#File paths 

file1 = 'county_solar_summary.json'
file2 = 'solar_multi_county_out.json'
output_file = 'merged_solar_summary.json'

# Load JSON data from files
with open(file1, 'r') as f1, open(file2, 'r') as f2:
    data1 = json.load(f1)
    data2 = json.load(f2)

# Merge the two datasets
merged_data = data1 + data2

# Save the merged dataset to a new JSON file
with open(output_file, 'w') as fout:
    json.dump(merged_data, fout, indent=4)
print(f"Merged {len(data1)} entries from {file1} and {len(data2)} entries from {file2} into {output_file}.")