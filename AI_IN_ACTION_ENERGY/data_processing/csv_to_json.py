import csv 
import json 

def csv_to_json(csv_file_path, json_file_path = None):
    data = []

    with open(csv_file_path, newline = '', encoding = 'utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Reads CSV into dicts keyed by header row 
        for row in reader:

            entry ={
                # By County Resoltuion 
                'state': 'California',
                'county': row['county'],
                'description': row['county_text'], #county_text
                'level':'county', 

                # For Point/ Coordinate Resolution comment out the above and uncomment below:
                #'state': row['state'],
                #'county': row['county'],
                #'description': row['point_text'],
                #'level': 'point',
                #'latitude': float(row['latitude']),
                #'longitude': float(row['longitude']),


                #Optional fields, uncomment if needed:
                #'area_developable_sq_km': float(row['area_developable_sq_km']),
                #'capacity_ac_mw': float(row['capacity_ac_mw']),
                #'capacity_factor_ac': float(row['capacity_factor_ac']),
                #'lcoe_site_usd_per_mwh': float(row['lcoe_site_usd_per_mwh']),
                #'lcot_usd_per_mwh': float(row['lcot_usd_per_mwh']),
                #'lcoe_all_in_usd_per_mwh': float(row['lcoe_all_in_usd_per_mwh'])

                #Field for sums (6) - single or per county totals  
                'total_area_developable_sq_km': float(row['total_area_developable_sq_km']),
                'total_capacity_ac_mw': float(row['total_capacity_ac_mw']),
                'total_capacity_factor': float(row['total_capacity_factor']),
                'total_lcoe_site_usd_per_mwh': float(row['total_lcoe_site_usd_per_mwh']),
                'total_lcot_usd_per_mwh': float(row['total_lcot_usd_per_mwh']),
                'total_lcoe_all_in_usd_per_mwh': float(row['total_lcoe_all_in_usd_per_mwh'])
            }

            data.append(entry)
        
        if json_file_path:
            with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=4)

        return data
    
if __name__ == "__main__":

    

    #To convert the multi county CSV to JSON, uncomment the lines below: 
    #csv_file = 'solar_multi_county_out.csv' #'county_solar_summary.csv
    #json_file = 'solar_multi_county_out.json'#'county_solar_summary.json' 
    #json_data = csv_to_json(csv_file, json_file)


    #To convert the single county CSV to JSON, comment out the above lines and uncomment below:
    csv_file = 'county_solar_summary.csv'
    json_file = 'county_solar_summary.json' 
    json_data = csv_to_json(csv_file, json_file)

    print(f"Converted {len(json_data)} rows from CSV to JSON.")


