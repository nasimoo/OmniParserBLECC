from ClickyCC import BoundingBoxUtils, HidUtils
from ClickyMaps import maps
from ClickyWash import Wash
import pandas as pd

# BLE Configuration
BLUETOOTH_COM_PORT = "COM4"
BAUD_RATE = 115200
hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)
bbox_utils = BoundingBoxUtils(
    screen_width=1920,
    screen_height=1080,
    base_x_offset=0,
    base_y_offset=10
)

def main():
    # Load CSV data into a pandas DataFrame
    file_path = 'Bot Rebuild 2 - Bot Master Sheet (Chromebook Edition).csv'
    df = pd.read_csv(file_path, dtype=str).fillna('Unknown')  # Ensure all data is string and replace NaN with 'Unknown'
    
    processed_email_prefixes = set()  # Track processed Gmail prefixes
    
    for index, row in df.iterrows():
        print(f"Row {index}: {row.to_dict()}")  # Debugging
        
        # Validate Gmail field
        gmail = row.get('gmail', '').strip()
        if not gmail:
            print(f"Skipping {row['firstname']} {row['lastname']} - Gmail not provided.")
            continue
        
        email_prefix = gmail.split('@')[0].strip()

        # Skip duplicate email prefixes if Date is already populated
        if email_prefix in processed_email_prefixes or not df[(df['gmail'].str.startswith(email_prefix + '@')) & (df['Date'] != 'Unknown')].empty:
            print(f"Skipping {row['firstname']} {row['lastname']} - Duplicate Gmail prefix with Date already processed.")
            continue

        # Skip if 'Date' is populated
        if row['Date'] != 'Unknown':
            print(f"Skipping {row['firstname']} {row['lastname']} - Date already populated.")
            continue

        # Add to processed email prefixes set
        processed_email_prefixes.add(email_prefix)

        # Extract row values safely
        firstname = row['firstname']
        lastname = row['lastname']
        birthdate = row['birthdate']
        gender = row['gender']
        name = row['Name']
        address = row['address']
        number = row['number']
        category = row['Category']

        print(f"Processing: {firstname} {lastname}, Gmail Prefix: {email_prefix}")

        # Execute required functions
        maps(hid, bbox_utils, name, address, number, category)
        Wash(hid, bbox_utils)

if __name__ == "__main__":
    main()
