import pandas as pd

#Load the data 


STATE ="California"


#In 2035, a location in San Diego County, California at X lat and Y long has a solar potential of Z kWh/m2 per year.
def point_text(row):
    """
    Convert a DataFrame row with solar potential data into a descriptive sentence. 

    Expects columns: state, county, solar_potential_kwh_m2_per_year.
    Returns a string summarizing the solar potential for the given state and county.
    """
    state = row['state']
    county = row['county']
    lcoe_site = row['lcoe_site_usd_per_mwh']
    return (
        f"In 2035, a location in {county}, {state} at {row['latitude']}, {row['longitude']} has an area available for solar development of {row['area_developable_sq_km']:.2f} sq km, "
        f"a capacity of {row['capacity_ac_mw']:.2f} MW, and a capacity factor of {row['capacity_factor_ac']:.2f}. "
        f"The LCOE for site-specific projects is {lcoe_site:.2f} USD/MWh."
        f" The LCOT is {row['lcot_usd_per_mwh']:.2f} USD/MWh and the LCOE all-in is {row['lcoe_all_in_usd_per_mwh']:.2f} USD/MWh."
        
    )

# Group the DataFrame by county

def county_summary(county_df):
    county = county_df.name

    #Find totals/sums. Could have also used the averages.  
    sum_area_developable = county_df['area_developable_sq_km'].sum()
    sum_capacity_ac_mw = county_df['capacity_ac_mw'].sum()
    sum_capacity_factor = county_df['capacity_factor_ac'].sum()

    sum_lcoe_site = county_df['lcoe_site_usd_per_mwh'].sum()
    sum_lcot = county_df['lcot_usd_per_mwh'].sum()
    sum_lcoe_all = county_df['lcoe_all_in_usd_per_mwh'].sum()

    description = (
        f"In 2035 in {county}, California, the total area available for solar development is {sum_area_developable:.2f} sq_km. "
        f"The total capacity of solar installations is {sum_capacity_ac_mw:.2f} MW, with a capacity factor of {sum_capacity_factor:.2f}. "
        f"The total LCOE for site-specific projects is {sum_lcoe_site:.2f} USD/MWh, while the total LCOT is {sum_lcot:.2f} USD/MWh."
        f"The total LCOE all-in is {sum_lcoe_all:.2f} USD/MWh."
    )
    return pd.Series({
        'total_area_developable_sq_km': sum_area_developable,
        'total_capacity_ac_mw': sum_capacity_ac_mw,
        'total_capacity_factor': sum_capacity_factor,
        'total_lcoe_site_usd_per_mwh': sum_lcoe_site,
        'total_lcot_usd_per_mwh': sum_lcot,
        'total_lcoe_all_in_usd_per_mwh': sum_lcoe_all,
        'county_text': description
    })



# Function to summarize the state data

def state_summary(df_state):
    sum_area_developable = df_state['area_developable_sq_km'].sum()
    sum_capacity_ac_mw = df_state['capacity_ac_mw'].sum()
    sum_capacity_factor = df_state['capacity_factor_ac'].sum()

    sum_lcoe_site = df_state['lcoe_site_usd_per_mwh'].sum()
    sum_lcot = df_state['lcot_usd_per_mwh'].sum()
    sum_lcoe_all = df_state['lcoe_all_in_usd_per_mwh'].sum()

    return (
        f"In 2035 in {STATE}, the total area available for solar development is {sum_area_developable:.2f} sq_km. "
        f"The total capacity of solar installations is {sum_capacity_ac_mw:.2f} MW, with a total capacity factor of {sum_capacity_factor:.2f}. "
        f"The total LCOE for site-specific projects is {sum_lcoe_site:.2f} USD/MWh, while the total LCOT is {sum_lcot:.2f} USD/MWh."
        f"The total LCOE all-in is {sum_lcoe_all:.2f} USD/MWh."
    )


def generate_all_resolution_text(input_csv, output_csv =None):

    df = pd.read_csv(input_csv)
    df_state = df[df['state'] == STATE]
    
    # Fine Resolution 
    df_state['point_text'] = df_state.apply(point_text, axis =1)

    #Medium Resolution 
    county_texts = df_state.groupby('county').apply(county_summary).reset_index()

    #Course Resolution 
    state_text = state_summary(df_state)



    # Show samples
    print("🔹 Sample point-level descriptions:")
    print(df_state['point_text'].head(), "\n")

    print("🔹 Sample county-level summaries:")
    print(county_texts.head(), "\n")

    print("🔹 State-level summary:")
    print(state_text)

    if output_csv:
        df_state.to_csv(output_csv, index=False)
        county_texts.to_csv("county_solar_summary.csv", index=False)
        with open("state_solar_summary.txt", "w") as f:
            f.write(state_text)
        print(f"\n✅ Saved to {output_csv}, county_solar_summary.csv, and state_solar_summary.txt")

generate_all_resolution_text("copy_solar_open_access_2035_moderate_supply_curve.csv", output_csv="solar_multi_county_out.csv")
