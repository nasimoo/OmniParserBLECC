# from ClickyCC import BoundingBoxUtils, HidUtils
import time

# # BLE Configuration
# BLUETOOTH_COM_PORT = "COM4"
# BAUD_RATE = 115200
# hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)
# bbox_utils = BoundingBoxUtils(
#     screen_width=1920,
#     screen_height=1080,
#     base_x_offset=-2,
#     base_y_offset=-10
# )




def maps(hid,bbox_utils,name,address,number,category):


    hid.move_to_origin()

    CSV_FILE_PATH = "output\\wash\\myaccount_bbox_content.csv"
    CSV_FILE_PATH_2 = "output\\seeding\\maps_bbox_content.csv"

    bbox_utils.bbox_click("116", CSV_FILE_PATH_2, hid)  # Close Chrome
    bbox_utils.bbox_click("58", CSV_FILE_PATH, hid)  # Press chrome
    time.sleep(5)
    hid.type_input("maps.google.com", "1", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH, click_before=True, x_offset=0, y_offset=0)  # Search maps
    time.sleep(5)
    hid.press_enter()
    time.sleep(10)

    bbox_utils.bbox_click("59", CSV_FILE_PATH, hid)  # Press user profile
    bbox_utils.bbox_click("52", CSV_FILE_PATH, hid, y_offset=60)  # Press the new gmail
    time.sleep(10)
    hid.type_input(address, "120", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_2, click_before=False, x_offset=0, y_offset=20)
    hid.press_enter()
    time.sleep(5)

    CSV_FILE_PATH_3 = "output\\seeding\\building_bbox_content.csv"
    bbox_utils.bbox_click("14", CSV_FILE_PATH_3, hid, y_offset=30)  # Open Add a missing place
    time.sleep(5)

    CSV_FILE_PATH_4 = "output\\seeding\\seeding_bbox_content.csv"
    hid.type_input(name, "76", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_4, click_before=True, x_offset=0, y_offset=0)
    time.sleep(5)
    bbox_utils.bbox_click("23", CSV_FILE_PATH_4, hid, y_offset=0)  # Open category
    time.sleep(10)

    CSV_FILE_PATH_5 = "output\\seeding\\cat_bbox_content.csv"
    hid.type_input(category, "140", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_5, click_before=True, x_offset=0, y_offset=0)
    bbox_utils.bbox_click("141", CSV_FILE_PATH_5, hid, y_offset=20)  # Click category result

    time.sleep(10)
    hid.press_up_down_loop("down",11)
    time.sleep(10)
    CSV_FILE_PATH_6="output\seeding\moredetails_bbox_content.csv"
    CSV_FILE_PATH_7= "output\seeding\seedingbottom_bbox_content.csv"
    bbox_utils.bbox_click("140", CSV_FILE_PATH_6, hid, y_offset=0)  # click More Details
    hid.press_up_down_loop("down",2)

    time.sleep(10)
    hid.type_input(number, "109", bbox_utils=bbox_utils, csv_file_path=CSV_FILE_PATH_7, click_before=True, x_offset=0, y_offset=-60) #Number
    bbox_utils.bbox_click("75", CSV_FILE_PATH_7, hid, y_offset=0)  # click save
    time.sleep(10)
    CSV_FILE_PATH_10= "output\seeding\editspolicy_bbox_content.csv"
    bbox_utils.bbox_click("63", CSV_FILE_PATH_10, hid, y_offset=-90)  # click ok
    time.sleep(10)
    hid.refresh_page()


# maps(hid,bbox_utils,name="Elevate inpatient Mental health",address="8133 Connector Dr #415 Florence KY",number="(971) 358-7773",category="Health Counselor")