from ClickyCC import BoundingBoxUtils, HidUtils
import time
import csv
import datetime
import random
from ClickyWash import Wash
# BLE Configuration
BLUETOOTH_COM_PORT = "COM4"
BAUD_RATE = 115200
hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)

bbox_utils = BoundingBoxUtils(
    screen_width=1920,
    screen_height=1080,
    base_x_offset=-7,
    base_y_offset=-5
)
def process_csv(file_path):
    processed_data = []
    seen_gmails = set()

    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(f"Row being checked: {row}")  # Debugging row content
            if row['gmail'] and not row['date'].strip():  # Handle whitespace in Date
                email_prefix = row['gmail'].split('@')[0] if '@gmail.com' in row['gmail'] else row['gmail']
                if email_prefix not in seen_gmails:
                    print(f"Adding {email_prefix} to processed data")
                    seen_gmails.add(email_prefix)
                    processed_data.append({
                        'firstname': row['firstname'],
                        'lastname': row.get('lastname', 'Debroin'),
                        'email_prefix': email_prefix,
                        'birthdate': row['birthdate'],
                        'gender': row['gender'],
                        'luckynumber': row.get('luckynumber', '')
                    })
    print(f"Final processed data: {processed_data}")  # Debugging output
    return processed_data

def update_csv(file_path, email_prefix):
    today = datetime.date.today().strftime("%Y-%m-%d")
    updated_rows = []

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            for row in reader:
                # Update the Date column if the email matches
                if row['gmail'].startswith(email_prefix) and not row['date'].strip():
                    row['date'] = today
                updated_rows.append(row)

        # Write back the updated rows to the CSV
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        print(f"Date updated successfully for: {email_prefix}")
    except Exception as e:
        print(f"Error updating CSV: {e}")

def main():
    DATA= "Bot Rebuild 2 - Gmail Bot.csv"
    data = process_csv(DATA)
    for entry in data:
        firstname = entry['firstname']
        lastname = entry['lastname']
        gmail = entry['email_prefix']
        birthdate = entry['birthdate'].split('/')  # Split birthdate into components (MM, DD, YYYY)
        CSV_FILE_PATH = "output\\wash\\myaccount_bbox_content.csv"
        hid.move_to_origin()
        bbox_utils.bbox_click("86", CSV_FILE_PATH, hid)  # Close Chrome
        bbox_utils.bbox_click("58", CSV_FILE_PATH, hid, x_offset=-20)  # Open Chrome
        time.sleep(10)
        for _ in range(2):
            hid.refresh_page()

        bbox_utils.bbox_click("59", CSV_FILE_PATH, hid)  # Open user profile
        time.sleep(10)

        bbox_utils.bbox_click("8", CSV_FILE_PATH, hid, y_offset= 80)  # Open Add new Account
        time.sleep(10)
        CSV_FILE_PATH_2 = "output\\gmailcreate\\signin_bbox_content.csv"
        bbox_utils.bbox_click("83", CSV_FILE_PATH_2, hid)  # Open Create Account
        time.sleep(5)

        CSV_FILE_PATH_3 = "output\\gmailcreate\\createaccount_bbox_content.csv"
        hid.type_input(firstname, "33", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_3, click_before=True)
        hid.type_input(lastname, "40", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_3, click_before=True)
        time.sleep(5)
        bbox_utils.bbox_click("37", CSV_FILE_PATH_3, hid,x_offset=30)  # Click Next
        time.sleep(5)

        CSV_FILE_PATH_4 = "output\\gmailcreate\\bdate_bbox_content.csv"

        # Select Month
        bbox_utils.bbox_click("38", CSV_FILE_PATH_4, hid)  # Click Month
        time.sleep(5)
        hid.press_up_down_loop("down", int(birthdate[0]))  # Adjust for 0-based index
        hid.press_enter()
        # Enter Day and Year
        hid.type_input(birthdate[1], "36", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=True)  # Day
        time.sleep(5)
        hid.type_input(birthdate[2], "37", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=True)  # Year

        # Select Gender (using `gender` column)
        bbox_utils.bbox_click("7", CSV_FILE_PATH_4, hid)  # Click Gender
        hid.press_up_down_loop("down", int(entry['gender']))  # Adjust for 0-based index
        hid.press_enter()
        time.sleep(10)
        bbox_utils.bbox_click("41", CSV_FILE_PATH_4, hid,x_offset=30)  # Click Next    
        time.sleep(5)


        CSV_FILE_PATH_5 = "output\\gmailcreate\\gmailoptions_bbox_content.csv"
        CSV_FILE_PATH_5A = "output\\gmailcreate\\ngoptions_bbox_content.csv"

        hid.type_input(gmail, "20", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5A, click_before=True)
        time.sleep(20)
        bbox_utils.bbox_click("86", CSV_FILE_PATH_5, hid)  # Click Create own Gmail
        hid.type_input(gmail, "89", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5, click_before=False)
        time.sleep(5)
        bbox_utils.bbox_click("50", CSV_FILE_PATH_5, hid,x_offset=30)  # Click Next
        time.sleep(5)

        CSV_FILE_PATH_6 = "output\\gmailcreate\\password_bbox_content.csv"
        hid.type_input("elmo1020", "13", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_6, click_before=True, x_offset=0, y_offset=-10)
        time.sleep(7)
        bbox_utils.bbox_click("16", CSV_FILE_PATH_6, hid, y_offset=-20,x_offset=30)  # Press Next
        time.sleep(30)
        bbox_utils.bbox_click("16", CSV_FILE_PATH_6, hid, y_offset=-20,x_offset=30)  # Press Next Again
        time.sleep(50)

        CSV_FILE_PATH_7 = "output\\gmailcreate\\policy_bbox_content.csv"
        bbox_utils.bbox_click("0", CSV_FILE_PATH_7, hid, x_offset=30,y_offset=0)  
        time.sleep(7)
        hid.press_up_down_loop("down", 40, delay=0.1) 
        bbox_utils.bbox_click("32", CSV_FILE_PATH_7, hid, x_offset=30,y_offset=-20)  # Click more options
        time.sleep(7)
        hid.press_up_down_loop("down", 60,delay=0.1) 
        bbox_utils.bbox_click("25", CSV_FILE_PATH_7, hid, x_offset=30,y_offset=-20)  # Click I agree
        time.sleep(20)
        update_csv(DATA, gmail)
        
        Wash(hid, bbox_utils)

if __name__ == "__main__":
    main()