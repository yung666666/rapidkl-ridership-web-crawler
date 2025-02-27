import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
import os

# Function to get the RapidKL railway ridership between any two stations
def get_passenger_volume(A_station, B_station, retries=2, delay=5):
    url = f"https://data.gov.my/dashboard/rapid-explorer/rail/{A_station}/{B_station}"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=20)  # Set timeout to prevent hanging
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
                if script_tag:
                    data = json.loads(script_tag.string)

                    # Extract daily and monthly data
                    try:
                        date = data["props"]["pageProps"]['A_to_B']['data']['daily']['x']
                        daily_passenger = data["props"]["pageProps"]['A_to_B']['data']['daily']['passengers']
                        #AB_daily_passenger = data["props"]["pageProps"]['A_to_B']['data']['daily']['passengers']
                        #BA_daily_passenger = data["props"]["pageProps"]['B_to_A']['daily']['passengers']
                        month = data["props"]["pageProps"]['A_to_B']['data']['monthly']['x']
                        monthly_passenger = data["props"]["pageProps"]['A_to_B']['data']['monthly']['passengers']
                        #AB_monthly_passenger = data["props"]["pageProps"]['A_to_B']['data']['monthly']['passengers']
                        #BA_monthly_passenger = data["props"]["pageProps"]['B_to_A']['monthly']['passengers']

                        # Create DataFrames
                        #df_day = pd.DataFrame({'date': date, 'AtoB_volume': AB_daily_passenger, 'BtoA_volume': BA_daily_passenger})
                        #df_month = pd.DataFrame({'month': month, 'AtoB_volume': AB_monthly_passenger, 'BtoA_volume': BA_monthly_passenger})
                        df_day = pd.DataFrame({'date': date, 'ridership': daily_passenger})
                        df_month = pd.DataFrame({'month': month, 'ridership': monthly_passenger})
                        
                        return df_day, df_month  # Successfully fetched data
                    
                    except KeyError:
                        print(f"Could not find ridership data for {A_station} to {B_station}")
                        return None, None

            print(f"Attempt {attempt + 1} failed for {A_station} to {B_station}. Retrying...")
            time.sleep(delay + random.uniform(1, 3))  # Wait before retrying

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {A_station} to {B_station}: {e}")

    print(f"Skipping {A_station} to {B_station} after {retries} failed attempts.")
    return None, None  # If all retries fail

# Function to generate station pair
def process_station_pair(A, B):
    """
    Process a single station pair and return the processed DataFrames.
    """
    #print(f"Processing pair: {A} to {B}")
    
    # Get passenger volume for this station pair
    df_day, df_month = get_passenger_volume(A, B)
    
    if df_day is not None and df_month is not None:
        # Process the dates as requested
        df_day['date'] = pd.to_datetime(df_day['date'] / 1000, unit='s')
        df_month['month'] = pd.to_datetime(df_month['month'] / 1000, unit='s').dt.strftime('%Y-%m')
        
        # Add a column to identify the station pair
        df_day['A_station'] = A
        df_day['B_station'] = B
        df_month['A_station'] = A
        df_month['B_station'] = B
        
        return df_day, df_month
    else:
        print(f"Skipping pair {A} to {B} due to data retrieval failure")
        return None, None

# load the existing CSV file
def load_existing_data(file_path):
    """
    Load existing data from a CSV file if it exists, otherwise return an empty DataFrame.
    Convert 'date' and 'month' columns to datetime if they exist.
    """
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Convert 'date' to datetime if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # Convert 'month' to datetime if it exists and then to 'YYYY-MM' format if needed
        if 'month' in df.columns:
            df['month'] = pd.to_datetime(df['month'], errors='coerce').dt.strftime('%Y-%m')
        return df
    return pd.DataFrame()

# update the CSV file
def update_or_append_data(new_df, existing_df, key_columns):
    """
    Update existing rows or append new rows based on key_columns (e.g., ['date', 'A_station', 'B_station']).
    Ensure consistent data types for merging.
    """
    if existing_df.empty:
        return new_df
    
    # Ensure key columns have consistent types
    for col in key_columns:
        if col in new_df.columns and col in existing_df.columns:
            # Handle 'date' and 'month' specifically
            if col == 'date':
                new_df[col] = pd.to_datetime(new_df[col], errors='coerce')
                existing_df[col] = pd.to_datetime(existing_df[col], errors='coerce')
            elif col == 'month':
                # Convert both to datetime for comparison, then back to 'YYYY-MM' if needed
                new_df[col] = pd.to_datetime(new_df[col], errors='coerce').dt.strftime('%Y-%m')
                existing_df[col] = pd.to_datetime(existing_df[col], errors='coerce').dt.strftime('%Y-%m')
    
    # Merge new and existing data on key columns
    merged_df = pd.merge(existing_df, new_df, 
                        on=key_columns, 
                        how='outer', 
                        suffixes=('_old', '_new'))
    
    # If there’s a new value (e.g., volume), use it; otherwise, keep the old value
    for column in new_df.columns:
        if column not in key_columns:
            merged_df[column] = merged_df[f'{column}_new'].combine_first(merged_df[f'{column}_old'])
    
    # Drop the old/new suffix columns
    merged_df = merged_df[key_columns + [col for col in new_df.columns if col not in key_columns]]
    
    return merged_df

# Updated main function
def process_and_save_data():
    """
    Process station pairs directly from JSON dropdown data and save/update data in CSV files.
    """
    # Use a sample URL to fetch the initial JSON data
    sample_url = "https://data.gov.my/dashboard/rapid-explorer/rail/A0: All Stations/AG01: Sentul Timur"
    response = requests.get(sample_url)
    
    if response.status_code != 200:
        print("Failed to fetch initial page")
        return None
    
    # Parse HTML and extract JSON
    soup = BeautifulSoup(response.text, "lxml")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script_tag:
        print("Could not find data script")
        return None
    
    data = json.loads(script_tag.string)
    
    # Extract the dropdown.rail dictionary
    try:
        rail_data = data["props"]["pageProps"]["dropdown"]["rail"]
    except KeyError:
        print("Could not find rail data in JSON")
        return None
    
    # Generate station pairs from each station and its destination list
    station_pairs = []
    for a_station, destinations in rail_data.items():
        if a_station == "A0: All Stations":
            continue  # Skip the "All Stations" entry if it’s not needed
        for b_station in destinations:
            if b_station != "A0: All Stations":  # Skip "All Stations" as a destination
                # Ensure no self-pairs (A to A)
                if a_station != b_station:
                    station_pairs.append((a_station, b_station))
    
    # For testing, limit to a subset (e.g., first 20 pairs); remove for full run
    #station_pairs = station_pairs[:20]  # Adjust or remove as needed
    
    if not station_pairs:
        print("No valid station pairs found")
        return None
    
    # Initialize lists to store all results
    all_df_day = []
    all_df_month = []
    
    # Record start time for performance measurement
    start_time = time.time()
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        # Submit all tasks
        future_to_pair = {executor.submit(process_station_pair, A, B): (A, B) 
                          for A, B in station_pairs}
        
        # Collect results as they complete
        for future in as_completed(future_to_pair):
            df_day, df_month = future.result()
            if df_day is not None and df_month is not None:
                all_df_day.append(df_day)
                all_df_month.append(df_month)
    
    # Record end time
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
    
    # Combine all DataFrames into single DataFrames
    if all_df_day:
        final_df_day = pd.concat(all_df_day, ignore_index=True)
        final_df_day = final_df_day[['date', 'A_station', 'B_station', 'ridership']]
        
        # Load existing daily data
        existing_df_day = load_existing_data('rapidkl_daily_ridership.csv')
        
        # Update or append new data
        key_columns_day = ['date', 'A_station', 'B_station']
        updated_df_day = update_or_append_data(final_df_day, existing_df_day, key_columns_day)
        
        print('Daily data done!')
        #print("Combined daily data:")
        #print(updated_df_day.head())
        
        # Save updated daily data
        updated_df_day.to_csv('rapidkl_daily_ridership.csv', index=False)
    else:
        final_df_day = None
        print("No daily data collected")
    
    if all_df_month:
        final_df_month = pd.concat(all_df_month, ignore_index=True)
        final_df_month = final_df_month[['month', 'A_station', 'B_station', 'ridership']]
        
        # Load existing monthly data
        existing_df_month = load_existing_data('rapidkl_monthly_ridership.csv')
        
        # Update or append new data
        key_columns_month = ['month', 'A_station', 'B_station']
        updated_df_month = update_or_append_data(final_df_month, existing_df_month, key_columns_month)
        
        print('Monthly data done!')
        #print("Combined monthly data:")
        #print(updated_df_month.head())
        
        # Save updated monthly data
        updated_df_month.to_csv('rapidkl_monthly_ridership.csv', index=False)
    else:
        final_df_month = None
        print("No monthly data collected")
    
    #return data

# Main execution
if __name__ == "__main__":
    process_and_save_data()