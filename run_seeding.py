import os
import sys
import subprocess
import datetime
import time
import re
import argparse
import random
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from Clickyadb import ADBController

# Path to the seeding script
SEEDING_SCRIPT_PATH = "uipath_interface/scripts/seedin.py"

# Google Sheet configuration
SPREADSHEET_ID = '1j8VkPHappTqcDLrszOjFwu4lFOXqjyvsHHkEEmsEj2s'  # Replace with your actual spreadsheet ID
SHEET_NAME = 'Sheet1'  # Replace with your actual sheet name
RANDOMSEARCH_SHEET_NAME = 'randomsearch'  # Sheet containing random search terms
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Variable to store random search terms
randomsearch_terms = []

def get_google_sheets_service():
    """
    Authenticate and get a Google Sheets service object.
    
    Returns:
        service: Google Sheets service object
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)

def get_spreadsheet_data():
    """
    Fetch all data from the Google Sheet.
    
    Returns:
        tuple: (rows as list of dicts, fieldnames as list)
    """
    service = get_google_sheets_service()
    sheet = service.spreadsheets()
    
    # Get headers (first row)
    header_range = f"{SHEET_NAME}!1:1"
    header_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, 
                                      range=header_range).execute()
    fieldnames = header_result.get('values', [])[0]
    
    # Get all data
    data_range = f"{SHEET_NAME}"
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                               range=data_range).execute()
    values = result.get('values', [])
    
    # Skip header row and convert to list of dicts
    rows = []
    for row_values in values[1:]:
        # Pad row if it's shorter than headers
        padded_row = row_values + [''] * (len(fieldnames) - len(row_values))
        row_dict = {fieldnames[i]: padded_row[i] for i in range(len(fieldnames))}
        rows.append(row_dict)
    
    return rows, fieldnames

def get_randomsearch_data():
    """
    Fetch random search terms from the randomsearch sheet.
    
    Returns:
        list: List of search terms
    """
    service = get_google_sheets_service()
    sheet = service.spreadsheets()
    
    # Get data from randomsearch sheet
    data_range = f"{RANDOMSEARCH_SHEET_NAME}"
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                   range=data_range).execute()
        values = result.get('values', [])
        
        # Extract search terms (assuming they're in the first column)
        search_terms = []
        for row in values:
            if row and row[0].strip():  # Check if row exists and has non-empty first cell
                search_terms.append(row[0].strip())
        
        print(f"Successfully loaded {len(search_terms)} random search terms")
        return search_terms
    except Exception as e:
        print(f"Error loading random search terms: {str(e)}")
        return []

def get_random_search_term():
    """
    Get a random search term from the loaded terms.
    
    Returns:
        str: A random search term or empty string if none available
    """
    global randomsearch_terms
    if not randomsearch_terms:
        return ""
    
    return random.choice(randomsearch_terms)

def update_cell_in_sheet(row_index, column_name, value, fieldnames, sheet_id=SPREADSHEET_ID):
    """
    Update a specific cell in the Google Sheet.
    
    Args:
        row_index (int): Row index in the data (0-based, not counting header)
        column_name (str): Name of the column to update
        value (str): New value for the cell
        fieldnames (list): List of column names
        sheet_id (str): Spreadsheet ID
    """
    service = get_google_sheets_service()
    
    # Find the column index (0-based)
    try:
        col_index = fieldnames.index(column_name)
    except ValueError:
        print(f"Column '{column_name}' not found in sheet")
        return
    
    # Adjust row index to account for header row (1-based for Sheets API)
    adjusted_row = row_index + 2  # +1 for 0-indexing, +1 for header row
    
    # Convert to A1 notation
    col_letter = chr(65 + col_index)  # A=0, B=1, etc.
    cell_range = f"{SHEET_NAME}!{col_letter}{adjusted_row}"
    
    # Update the cell
    body = {
        'values': [[value]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=cell_range,
        valueInputOption='RAW',
        body=body
    ).execute()
    print(f"Updated cell {cell_range} with value '{value}'")

def run_seeding_for_row(row, dry_run=False):
    """
    Run the seeding script with data from the given row.
    
    Args:
        row (dict): A dictionary containing data for one row from the Google Sheet
        dry_run (bool): If True, don't actually run the script, just simulate success
        
    Returns:
        tuple: (bool, float) - Success status and elapsed time in seconds
    """
    # Start timing
    start_time = time.time()
    
    # Extract necessary data from the row
    email = row.get('Gmail', '')
    name = row.get('Name', '')
    address = row.get('AddresswSuite', '')
    category = row.get('Category', '')
    phone = row.get('Phone', '')
    
    # Get a random search term
    randomsearch = get_random_search_term()
    
    # Skip if any required field is missing
    if not email or not name or not address or not category or not phone:
        print(f"Skipping row with incomplete data: {row}")
        elapsed_time = time.time() - start_time
        return False, elapsed_time
    
    # If this is a dry run, simulate success
    if dry_run:
        print(f"DRY RUN: Would run seeding script for {name} with random search: {randomsearch}")
        # Simulate a small amount of time for dry runs
        time.sleep(0.5)
        elapsed_time = time.time() - start_time
        return True, elapsed_time
    
    # Create a modified version of the seeding script with the row's data
    temp_script_path = create_temp_script_with_data(email, name, address, category, phone, randomsearch)
    
    try:
        print(f"Running seeding script for {name} with random search: {randomsearch}...")
        # Get the current working directory for proper module importing
        current_dir = os.getcwd()
        
        # Run the modified script with the current directory in PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = current_dir
        
        result = subprocess.run([sys.executable, temp_script_path], 
                                capture_output=True, text=True, env=env)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Check if the script executed successfully
        if result.returncode == 0:
            print(f"Successfully completed seeding for {name} in {elapsed_time:.2f} seconds")
            print(result.stdout)
            return True, elapsed_time
        else:
            print(f"Error running seeding script for {name}:")
            print(result.stderr)
            return False, elapsed_time
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"Exception while running seeding script: {str(e)}")
        return False, elapsed_time
    finally:
        # Clean up the temporary script
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

def create_temp_script_with_data(email, name, address, category, phone, randomsearch=""):
    """
    Create a temporary copy of the seeding script with the data variables replaced.
    
    Args:
        email, name, address, category, phone: Data to insert into the script
        randomsearch: Random search term to insert
        
    Returns:
        str: Path to the temporary script file
    """
    # Read the original script
    with open(SEEDING_SCRIPT_PATH, 'r') as f:
        script_content = f.read()
    
    # Get the directory of the original script to keep relative paths working
    script_dir = os.path.dirname(SEEDING_SCRIPT_PATH)
    temp_script_name = f"temp_seeding_{int(time.time())}.py"
    temp_script_path = os.path.join(script_dir, temp_script_name)
    
    # Replace variable patterns
    # Replace {email} format
    script_content = script_content.replace("{email}", email)
    
    # Replace '{email}' format (with quotes)
    script_content = script_content.replace("'{email}'", f"'{email}'")
    
    # Replace f'{email}' format (with f-string syntax)
    script_content = script_content.replace("f'{email}'", f"'{email}'")
    
    # Do the same for other variables
    script_content = script_content.replace("{Name}", name)
    script_content = script_content.replace("'{Name}'", f"'{name}'")
    script_content = script_content.replace("f'{Name}'", f"'{name}'")
    
    script_content = script_content.replace("{address}", address)
    script_content = script_content.replace("'{address}'", f"'{address}'")
    script_content = script_content.replace("f'{address}'", f"'{address}'")
    
    script_content = script_content.replace("{Category}", category)
    script_content = script_content.replace("'{Category}'", f"'{category}'")
    script_content = script_content.replace("f'{Category}'", f"'{category}'")
    
    script_content = script_content.replace("{Phone}", phone)
    script_content = script_content.replace("'{Phone}'", f"'{phone}'")
    script_content = script_content.replace("f'{Phone}'", f"'{phone}'")
    
    # Add the randomsearch variable
    script_content = script_content.replace("{randomsearch}", randomsearch)
    script_content = script_content.replace("'{randomsearch}'", f"'{randomsearch}'")
    script_content = script_content.replace("f'{randomsearch}'", f"'{randomsearch}'")
    
    # Write to a temporary file in the same directory as the original script
    with open(temp_script_path, 'w') as tmp:
        tmp.write(script_content)
    
    print(f"Created temporary script at {temp_script_path}")
    return temp_script_path

def update_seeddate_and_timer_in_sheet(row_index, rows, fieldnames, elapsed_time):
    """
    Update the SeedDate and Timer columns for the specified row in Google Sheets.
    
    Args:
        row_index (int): The index of the row to update (0-based)
        rows (list): The list of all rows from the sheet
        fieldnames (list): The column headers
        elapsed_time (float): Time taken for the seeding operation in seconds
    """
    # Format the current date
    today = datetime.datetime.now().strftime("%m/%d/%Y")
    
    # Format the elapsed time in HH:MM:SS format
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    timer_value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Update the values in the local data
    rows[row_index]['SeedDate'] = today
    
    # Check if Timer column exists, if not, we'll skip updating it but not fail
    if 'Timer' in fieldnames:
        rows[row_index]['Timer'] = timer_value
        
    # Update the values in Google Sheets
    update_cell_in_sheet(row_index, 'SeedDate', today, fieldnames)
    
    # Only try to update Timer if the column exists
    if 'Timer' in fieldnames:
        update_cell_in_sheet(row_index, 'Timer', timer_value, fieldnames)
    else:
        print("Warning: 'Timer' column not found in sheet, timing data will not be saved")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run seeding script for rows in Google Sheet with Gmail but no SeedDate')
    parser.add_argument('--dry-run', action='store_true', help='Update SeedDate without running seeding script')
    parser.add_argument('--spreadsheet-id', help='Google Spreadsheet ID (from the URL)')
    parser.add_argument('--sheet-name', default='Sheet1', help='Name of the sheet to use')
    parser.add_argument('--randomsearch-sheet', default='randomsearch', help='Name of the sheet containing random search terms')
    parser.add_argument('--no-toggle-data', action='store_true', help='Skip toggling mobile data after each row')
    args = parser.parse_args()
    
    if args.dry_run:
        print("*** DRY RUN MODE - Will update SeedDate without running actual seeding scripts ***")
    
    # Update spreadsheet ID and sheet names if provided as arguments
    global SPREADSHEET_ID, SHEET_NAME, RANDOMSEARCH_SHEET_NAME, randomsearch_terms
    if args.spreadsheet_id:
        SPREADSHEET_ID = args.spreadsheet_id
    if args.sheet_name:
        SHEET_NAME = args.sheet_name
    if args.randomsearch_sheet:
        RANDOMSEARCH_SHEET_NAME = args.randomsearch_sheet
        
    # Check if the seeding script exists
    if not args.dry_run and not os.path.exists(SEEDING_SCRIPT_PATH):
        print(f"Seeding script not found: {SEEDING_SCRIPT_PATH}")
        return
    
    # Ensure credentials.json exists
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json file not found. Please download this file from the Google Cloud Console.")
        print("Follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Google Sheets API")
        print("4. Create OAuth 2.0 credentials (desktop client)")
        print("5. Download the credentials file as 'credentials.json' and place it in the same directory as this script")
        return
    
    # Get random search terms
    randomsearch_terms = get_randomsearch_data()
    
    # Read data from Google Sheet
    try:
        rows, fieldnames = get_spreadsheet_data()
        print(f"Successfully loaded data from Google Sheet with {len(rows)} rows")
        
        # Check if Timer column exists, and warn if not
        if 'Timer' not in fieldnames:
            print("Warning: 'Timer' column not found in the sheet. Please add a 'Timer' column to track timing data.")
    except Exception as e:
        print(f"Error loading data from Google Sheet: {str(e)}")
        return
    
    # Initialize ADB controller if we're toggling mobile data
    adb = None
    if not args.no_toggle_data and not args.dry_run:
        try:
            adb = ADBController()
            print("ADB controller initialized successfully for mobile data toggling")
        except Exception as e:
            print(f"Warning: Could not initialize ADB controller: {e}")
            print("Mobile data toggling will be skipped")
            adb = None
    
    # Count eligible rows (with Gmail but no SeedDate)
    eligible_rows = [row for row in rows if row.get('Gmail') and not row.get('SeedDate')]
    print(f"Found {len(eligible_rows)} rows with Gmail but no SeedDate")
    
    # Track total time for all operations
    total_time = 0.0
    
    # Process each eligible row
    processed_count = 0
    for i, row in enumerate(rows):
        # Check if this row has Gmail but no SeedDate
        if row.get('Gmail') and not row.get('SeedDate'):
            print(f"\nProcessing row {i+1}: {row.get('Name', 'Unknown')}")
            
            # Run the seeding script for this row and get timing
            success, elapsed_time = run_seeding_for_row(row, dry_run=args.dry_run)
            
            # Add to total time
            if success:
                total_time += elapsed_time
            
            if success:
                # Update the SeedDate and Timer columns in Google Sheets
                update_seeddate_and_timer_in_sheet(i, rows, fieldnames, elapsed_time)
                
                processed_count += 1
                print(f"Progress: {processed_count}/{len(eligible_rows)} eligible rows processed")
                print(f"Time for this operation: {elapsed_time:.2f} seconds")
                print(f"Average time per row so far: {(total_time/processed_count):.2f} seconds")
                
                # Toggle mobile data off for 20 seconds then turn it back on
                if adb and not args.dry_run and not args.no_toggle_data:
                    print("Turning mobile data OFF for 20 seconds...")
                    try:
                        adb.toggle_mobile_data("off")
                        time.sleep(50)  # Wait for 50 seconds
                        print("Turning mobile data back ON...")
                        adb.toggle_mobile_data("on")
                        print("Mobile data toggling complete")
                    except Exception as e:
                        print(f"Error toggling mobile data: {e}")
                
                # Add a delay between rows to prevent overwhelming the system
                if processed_count < len(eligible_rows) and not args.dry_run:
                    print("Waiting 5 seconds before processing next row...")
                    time.sleep(5)
            else:
                print(f"Failed to process row {i+1}. Moving to next row.")
    
    # Print summary statistics
    if processed_count > 0:
        print(f"\nProcessing complete. {processed_count} rows were updated.")
        print(f"Total processing time: {total_time:.2f} seconds")
        print(f"Average time per row: {(total_time/processed_count):.2f} seconds")
    else:
        print("\nNo rows were processed successfully.")

if __name__ == "__main__":
    main() 