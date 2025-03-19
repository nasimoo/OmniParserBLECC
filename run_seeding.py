import csv
import os
import sys
import subprocess
import datetime
import time
import shutil
import re
import argparse
from tempfile import NamedTemporaryFile

# Path to the CSV file and seeding script
CSV_FILE_PATH = "uipath_interface/Nursery - Sheet1.csv"
SEEDING_SCRIPT_PATH = "uipath_interface/scripts/seedin.py"

def run_seeding_for_row(row, dry_run=False):
    """
    Run the seeding script with data from the given row.
    
    Args:
        row (dict): A dictionary containing data for one row from the CSV
        dry_run (bool): If True, don't actually run the script, just simulate success
        
    Returns:
        bool: True if the script runs successfully, False otherwise
    """
    # Extract necessary data from the row
    email = row.get('Gmail', '')
    name = row.get('Name', '')
    address = row.get('Address', '')
    category = row.get('Category', '')
    phone = row.get('Phone', '')
    
    # Skip if any required field is missing
    if not email or not name or not address or not category or not phone:
        print(f"Skipping row with incomplete data: {row}")
        return False
    
    # If this is a dry run, simulate success
    if dry_run:
        print(f"DRY RUN: Would run seeding script for {name}")
        return True
    
    # Create a modified version of the seeding script with the row's data
    temp_script_path = create_temp_script_with_data(email, name, address, category, phone)
    
    try:
        print(f"Running seeding script for {name}...")
        # Get the current working directory for proper module importing
        current_dir = os.getcwd()
        
        # Run the modified script with the current directory in PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = current_dir
        
        result = subprocess.run([sys.executable, temp_script_path], 
                                capture_output=True, text=True, env=env)
        
        # Check if the script executed successfully
        if result.returncode == 0:
            print(f"Successfully completed seeding for {name}")
            print(result.stdout)
            return True
        else:
            print(f"Error running seeding script for {name}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Exception while running seeding script: {str(e)}")
        return False
    finally:
        # Clean up the temporary script
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

def create_temp_script_with_data(email, name, address, category, phone):
    """
    Create a temporary copy of the seeding script with the data variables replaced.
    
    Args:
        email, name, address, category, phone: Data to insert into the script
        
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
    
    # Write to a temporary file in the same directory as the original script
    with open(temp_script_path, 'w') as tmp:
        tmp.write(script_content)
    
    print(f"Created temporary script at {temp_script_path}")
    return temp_script_path

def update_seeddate_in_csv(row_index, csv_rows):
    """
    Update the SeedDate column for the specified row.
    
    Args:
        row_index (int): The index of the row to update
        csv_rows (list): The list of all rows from the CSV
    """
    today = datetime.datetime.now().strftime("%m/%d/%Y")
    csv_rows[row_index]['SeedDate'] = today

def save_updated_csv(csv_rows, fieldnames):
    """
    Save the updated rows back to the CSV file.
    
    Args:
        csv_rows (list): The updated rows
        fieldnames (list): The column headers
    """
    # Create a temporary file
    temp_file = NamedTemporaryFile(mode='w', delete=False, newline='')
    
    try:
        # Write the updated data to the temporary file
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
        temp_file.close()
        
        # Replace the original file with the temporary file
        shutil.move(temp_file.name, CSV_FILE_PATH)
        print(f"Successfully updated {CSV_FILE_PATH}")
    except Exception as e:
        os.unlink(temp_file.name)
        print(f"Error updating CSV file: {str(e)}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run seeding script for rows in CSV with Gmail but no SeedDate')
    parser.add_argument('--dry-run', action='store_true', help='Update SeedDate without running seeding script')
    args = parser.parse_args()
    
    if args.dry_run:
        print("*** DRY RUN MODE - Will update SeedDate without running actual seeding scripts ***")
    
    # Check if the CSV and script files exist
    if not os.path.exists(CSV_FILE_PATH):
        print(f"CSV file not found: {CSV_FILE_PATH}")
        return
        
    if not args.dry_run and not os.path.exists(SEEDING_SCRIPT_PATH):
        print(f"Seeding script not found: {SEEDING_SCRIPT_PATH}")
        return
    
    # Read the CSV file
    csv_rows = []
    fieldnames = []
    
    with open(CSV_FILE_PATH, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        csv_rows = list(reader)
    
    # Count eligible rows (with Gmail but no SeedDate)
    eligible_rows = [row for row in csv_rows if row.get('Gmail') and not row.get('SeedDate')]
    print(f"Found {len(eligible_rows)} rows with Gmail but no SeedDate")
    
    # Process each eligible row
    processed_count = 0
    for i, row in enumerate(csv_rows):
        # Check if this row has Gmail but no SeedDate
        if row.get('Gmail') and not row.get('SeedDate'):
            print(f"\nProcessing row {i+1}: {row.get('Name', 'Unknown')}")
            
            # Run the seeding script for this row
            success = run_seeding_for_row(row, dry_run=args.dry_run)
            
            if success:
                # Update the SeedDate column
                update_seeddate_in_csv(i, csv_rows)
                
                # Save the updated CSV after each successful row
                save_updated_csv(csv_rows, fieldnames)
                
                processed_count += 1
                print(f"Progress: {processed_count}/{len(eligible_rows)} eligible rows processed")
                
                # Add a delay between rows to prevent overwhelming the system
                if processed_count < len(eligible_rows) and not args.dry_run:
                    print("Waiting 5 seconds before processing next row...")
                    time.sleep(5)
            else:
                print(f"Failed to process row {i+1}. Moving to next row.")
    
    print(f"\nProcessing complete. {processed_count} rows were updated.")

if __name__ == "__main__":
    main() 