import time
from Clickyadb import ADBController
# from ClickyCC import BoundingBoxUtils, HidUtils

# # BLE Configuration
# BLUETOOTH_COM_PORT = "COM4"
# BAUD_RATE = 115200
# hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)
# bbox_utils = BoundingBoxUtils(
#     screen_width=1920,
#     screen_height=1080,
#     base_x_offset=10,
#     base_y_offset=0
# )
def Wash(hid,bbox_utils):
    hid.move_to_origin()

    CSV_FILE_PATH = "output\wash\myaccount_bbox_content.csv"
    bbox_utils.bbox_click("86", CSV_FILE_PATH, hid)  # Close Chrome
    bbox_utils.bbox_click("58", CSV_FILE_PATH, hid, x_offset=-20)  # Open Chrome
    time.sleep(5)
    hid.refresh_page()
    bbox_utils.bbox_click("59", CSV_FILE_PATH, hid)  # open User Profile
    hid.fullscreen()
    time.sleep(3)
    # bbox_utils.bbox_click("5", CSV_FILE_PATH, hid)  # open User Profie
    # time.sleep(3)
    # hid.press_up_down_loop("down", 2, delay=0.5)
    bbox_utils.bbox_click("88", CSV_FILE_PATH, hid,y_offset=-60)  # Click manage accounts
    time.sleep(10)
    hid.fullscreen()
    time.sleep(5)
    CSV_FILE_PATH_2 = "output\wash\\accountsettings_bbox_content.csv"
    bbox_utils.bbox_click("49", CSV_FILE_PATH_2, hid,y_offset=40,x_offset=40)  # click more options
    bbox_utils.bbox_click("49", CSV_FILE_PATH_2, hid,y_offset=50)  # delete

    time.sleep(10)
    hid.fullscreen()
    CSV_FILE_PATH_3 = "output\wash\\controlcenter_bbox_content.csv"
    bbox_utils.bbox_click("82", CSV_FILE_PATH_3, hid)  # click control
    bbox_utils.bbox_click("109", CSV_FILE_PATH_3, hid,x_offset=-35,y_offset=-20)  # click power options
    time.sleep(5)
    bbox_utils.bbox_click("127", CSV_FILE_PATH_3, hid,y_offset=-20)  # click restart
    try:
        adb = ADBController()
        adb.toggle_mobile_data("off")  # Turn off mobile data
        time.sleep(20)
        adb.toggle_mobile_data("on")   # Turn on mobile data
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(45)
    hid.type_input("926260")
    time.sleep(10)

# Wash(hid,bbox_utils)