from ClickyCC import BoundingBoxUtils, HidUtils
import time
import csv
import datetime
import random

# BLE Configuration
BLUETOOTH_COM_PORT = "COM4"
BAUD_RATE = 115200
hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)

bbox_utils = BoundingBoxUtils(
    screen_width=1920,
    screen_height=1080,
    base_x_offset=-10,
    base_y_offset=-10
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

        print(f"Processing: {firstname} {lastname} with email prefix {gmail}")
        hid.move_to_origin()
        CSV_FILE_PATH_0= "output\gmailbot\home_bbox_content.csv"
        bbox_utils.bbox_click("15", CSV_FILE_PATH_0, hid)  # max chrome screen
        CSV_FILE_PATH = "output\gmailbot\support_bbox_content.csv"
        hid.type_input("maps.google.com", "51", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH, click_before=True)
        time.sleep(5)
        hid.press_enter()
        time.sleep(5)
        bbox_utils.bbox_click("19", CSV_FILE_PATH, hid)  # press sign in
        time.sleep(5)
        CSV_FILE_PATH_2 = "output\gmailbot\signin_bbox_content.csv"
        bbox_utils.bbox_click("38", CSV_FILE_PATH_2, hid)  # press create acc
        bbox_utils.bbox_click("5", CSV_FILE_PATH_2, hid)  # press bus account
        time.sleep(10)
        # CSV_FILE_PATH_3 = "output\\gmailbot\\bus_bbox_content.csv"
        # bbox_utils.bbox_click("20", CSV_FILE_PATH_3, hid)  # press get a gmail account
        # time.sleep(5)
        CSV_FILE_PATH_4 = "output\\gmailbot\\name_bbox_content.csv"
        hid.type_input(firstname, "16", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=False)
        time.sleep(5)
        hid.press_tab()
        time.sleep(2)
        hid.type_input(lastname, "23", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=False)
        time.sleep(3)
        bbox_utils.bbox_click("18", CSV_FILE_PATH_4, hid)  # Click Next
        time.sleep(5)

        month_to_element_id = {
            "01": "1",
            "02": "2",
            "03": "3",
            "04": "4",
            "05": "5",
            "06": "6",
            "07": "7",
            "08": "8",
            "09": "9",
            "10": "54",
            "11": "57",
            "12": "50"
        }
        birthdate = entry['birthdate'].split('/')  # Split birthdate into components (MM, DD, YYYY)
        month = birthdate[0].zfill(2)  # Ensure zero-padding (e.g., "4" → "04")
        element_id = month_to_element_id.get(month, None)

        CSV_FILE_PATH_5 = "output\\gmailbot\\bdate_bbox_content.csv"
        CSV_FILE_PATH_5A = "output\\gmailbot\\dates_bbox_content.csv"
        # Select Month
        bbox_utils.bbox_click("18", CSV_FILE_PATH_5, hid)  # Click Month
        time.sleep(5)
        if element_id:
            bbox_utils.bbox_click(element_id, CSV_FILE_PATH_5A, hid)  # Click Month
        else:
            print(f"Invalid month in birthdate: {birthdate[0]}")        # hid.press_up_down_loop("down", int(birthdate[0]))  # Adjust for 0-based index
        hid.press_enter()

        # Enter Day and Year
        hid.type_input(birthdate[1], "17", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5, click_before=True)  # Day
        time.sleep(5)
        hid.type_input(birthdate[2], "19", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5, click_before=True)  # Year

        # Select Gender (using `gender` column)
        bbox_utils.bbox_click("22", CSV_FILE_PATH_5, hid)  # Click Gender
        hid.press_up_down_loop("down", int(entry['gender']))  # Adjust for 0-based index
        hid.press_enter()
        time.sleep(5)

        # Generate a random number between 1 and 5
        random_loops = random.randint(1, 5)

        # Then loop that many times
        for _ in range(random_loops):
            bbox_utils.bbox_click("1", CSV_FILE_PATH_5, hid)


        bbox_utils.bbox_click("21", CSV_FILE_PATH_5, hid)  # Click Next    
        time.sleep(5)


        CSV_FILE_PATH_6 = "output\gmailbot\gmails_bbox_content.csv"
        CSV_FILE_PATH_6B = "output\\gmailcreate\\ngoptions_bbox_content.csv"

        hid.type_input(gmail, "20", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_6B, click_before=False)
        time.sleep(6)
        bbox_utils.bbox_click("4", CSV_FILE_PATH_6, hid, y_offset=-5)  # Click Create own Gmail
        hid.type_input(gmail, "48", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_6, click_before=False)
        time.sleep(4)
        bbox_utils.bbox_click("26", CSV_FILE_PATH_6, hid, y_offset=20)  # Click Next
        time.sleep(5)

        CSV_FILE_PATH_7 = "output\gmailbot\password_bbox_content.csv"
        hid.type_input("elmo1020", "17", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_7, click_before=False, x_offset=0, y_offset=-10)
        time.sleep(2)
        hid.press_tab()
        hid.type_input("elmo1020", "18", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_7, click_before=True, x_offset=0, y_offset=-10)
        time.sleep(5)
        bbox_utils.bbox_click("20", CSV_FILE_PATH_7, hid, y_offset=0)  # Press Next
        time.sleep(5)
        CSV_FILE_PATH_8 = "output\\gmailbot\\recovery_bbox_content.csv"
        bbox_utils.bbox_click("24", CSV_FILE_PATH_8, hid, y_offset=0)  # Press Next Again
        time.sleep(5)

        CSV_FILE_PATH_9 = "output\\gmailbot\\review_bbox_content.csv"
        bbox_utils.bbox_click("24", CSV_FILE_PATH_9, hid, y_offset=0)  # Press Next Again


        CSV_FILE_PATH_10 = "output\gmailbot\options_bbox_content.csv"
        bbox_utils.bbox_click("0", CSV_FILE_PATH_10, hid, x_offset=30,y_offset=0)  
        time.sleep(5)
        hid.press_up_down_loop("down", 48, delay=0.1)  #Move to More option
        bbox_utils.bbox_click("32", CSV_FILE_PATH_10, hid, y_offset=-30)  # Click More Options
        time.sleep(8)
        hid.press_up_down_loop("down", 29)  # Move down to Don't Save Web App Activity
        time.sleep(5)

        CSV_FILE_PATH_11 = "output\gmailbot\agree_bbox_content.csv"
  
        hid.press_up_down_loop("down", 40, delay=0.1)  # Move down to Don't Save Web App Activity
        bbox_utils.bbox_click("27", CSV_FILE_PATH_11, hid, x_offset=30,y_offset=0)  # Click no to Web activity
        update_csv(DATA, gmail)
        


        CSV_FILE_PATH_3 = "output\wash\\controlcenter_bbox_content.csv"
        bbox_utils.bbox_click("82", CSV_FILE_PATH_3, hid)  # click control
        bbox_utils.bbox_click("109", CSV_FILE_PATH_3, hid)  # click power options
        bbox_utils.bbox_click("127", CSV_FILE_PATH_3, hid)  # click restart
        time.sleep(60)
        CSV_FILE_PATH_4 = "output\gmailbot\loggedout_bbox_content.csv"
        bbox_utils.bbox_click("18", CSV_FILE_PATH_4, hid)  # turn off diagnosis
        time.sleep(10)

        CSV_FILE_PATH_5 = "output\gmailbot\guest_bbox_content.csv"
        bbox_utils.bbox_click("18", CSV_FILE_PATH_5, hid)  # turn off diagnosis
        bbox_utils.bbox_click("11", CSV_FILE_PATH_5, hid)  # Accept and Continue
        time.sleep(20)



    if hid.ser:
        hid.ser.close()


if __name__ == "__main__":
    main()
