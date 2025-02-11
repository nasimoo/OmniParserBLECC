from ClickyCC import BoundingBoxUtils, HidUtils
import time

# BLE Configuration
# BLUETOOTH_COM_PORT = "COM4"
# BAUD_RATE = 115200
# hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)

# bbox_utils = BoundingBoxUtils(
#     screen_width=1920,
#     screen_height=1080,
#     base_x_offset=-10,
#     base_y_offset=-10
# )


def gmailcreate(bbox_utils,hid,firstname,lastname,birthdate,gender,gmail):


    print(f"Processing: {firstname} {lastname} with email prefix {gmail}")

    CSV_FILE_PATH = "output\\wash\\myaccount_bbox_content.csv"
    hid.move_to_origin()
    bbox_utils.bbox_click("86", CSV_FILE_PATH, hid)  # Close Chrome
    bbox_utils.bbox_click("58", CSV_FILE_PATH, hid)  # Open Chrome
    time.sleep(15)
    for _ in range(2):
        hid.refresh_page()

    bbox_utils.bbox_click("59", CSV_FILE_PATH, hid)  # Open user profile
    bbox_utils.bbox_click("8", CSV_FILE_PATH, hid)  # Open Add new Account
    time.sleep(20)
    CSV_FILE_PATH_2 = "output\\gmailcreate\\signin_bbox_content.csv"
    bbox_utils.bbox_click("83", CSV_FILE_PATH_2, hid)  # Open Create Account
    time.sleep(10)

    CSV_FILE_PATH_3 = "output\\gmailcreate\\createaccount_bbox_content.csv"
    hid.type_input(firstname, "33", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_3, click_before=True)
    hid.type_input(lastname, "40", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_3, click_before=True)
    time.sleep(10)
    bbox_utils.bbox_click("37", CSV_FILE_PATH_3, hid)  # Click Next
    time.sleep(20)

    CSV_FILE_PATH_4 = "output\\gmailcreate\\bdate_bbox_content.csv"

    # Select Month
    bbox_utils.bbox_click("38", CSV_FILE_PATH_4, hid)  # Click Month
    time.sleep(10)
    birthdate = birthdate.split('/')  # Split birthdate into components (MM, DD, YYYY)
    hid.press_up_down_loop("down", int(birthdate[0]))  # Adjust for 0-based index
    hid.press_enter()
    # Enter Day and Year
    hid.type_input(birthdate[1], "36", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=True)  # Day
    time.sleep(20)
    hid.type_input(birthdate[2], "37", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=True)  # Year

    # Select Gender (using `gender` column)
    bbox_utils.bbox_click("7", CSV_FILE_PATH_4, hid)  # Click Gender
    hid.press_up_down_loop("down", int(gender))  # Adjust for 0-based index
    hid.press_enter()
    time.sleep(10)
    bbox_utils.bbox_click("41", CSV_FILE_PATH_4, hid)  # Click Next    
    time.sleep(20)


    CSV_FILE_PATH_5 = "output\\gmailcreate\\gmailoptions_bbox_content.csv"
    CSV_FILE_PATH_5A = "output\\gmailcreate\\ngoptions_bbox_content.csv"

    hid.type_input(gmail, "20", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5A, click_before=True)
    time.sleep(20)
    bbox_utils.bbox_click("86", CSV_FILE_PATH_5, hid)  # Click Create own Gmail
    hid.type_input(gmail, "89", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5, click_before=True)
    time.sleep(10)
    bbox_utils.bbox_click("50", CSV_FILE_PATH_5, hid)  # Click Next
    time.sleep(10)

    CSV_FILE_PATH_6 = "output\\gmailcreate\\password_bbox_content.csv"
    hid.type_input("elmo1020", "13", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_6, click_before=True, x_offset=0, y_offset=-10)
    time.sleep(7)
    bbox_utils.bbox_click("16", CSV_FILE_PATH_6, hid, y_offset=-40)  # Press Next
    time.sleep(30)
    bbox_utils.bbox_click("16", CSV_FILE_PATH_6, hid, y_offset=-40)  # Press Next Again
    time.sleep(50)

    CSV_FILE_PATH_7 = "output\\gmailcreate\\policy_bbox_content.csv"
    bbox_utils.bbox_click("0", CSV_FILE_PATH_7, hid, x_offset=30,y_offset=0)  
    time.sleep(7)
    hid.press_up_down_loop("down", 40, delay=0.1) 
    bbox_utils.bbox_click("32", CSV_FILE_PATH_7, hid, x_offset=30,y_offset=0)  # Click more options
    time.sleep(7)
    hid.press_up_down_loop("down", 60,delay=0.1) 
    bbox_utils.bbox_click("25", CSV_FILE_PATH_7, hid, x_offset=30,y_offset=0)  # Click I agree
    time.sleep(20)
    

# gmailcreate(bbox_utils,hid,firstname='an',lastname='aw',birthdate='10/26/1998',gender='1',gmail='wdwidwd@gmail.com')