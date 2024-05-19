import json

def count_sectors(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    sector_counts = {}
    for item in data:
        if 'data' in item:
            sector = item['sector']
            print(sector)
            if sector in sector_counts:
                sector_counts[sector] += 1
            else:
                sector_counts[sector] = 1
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(sector_counts, file, ensure_ascii=False, indent=4)

    print(f"Data has been saved to {output_file}")

count_sectors('results.json', 'output.json')
