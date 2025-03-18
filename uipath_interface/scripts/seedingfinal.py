import sys
import os
import time
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ClickyCC import BoundingBoxUtils, HidUtils

def main():
    # BLE Configuration
    BLUETOOTH_COM_PORT = '/dev/tty.usbserial-02242E2E'
    BAUD_RATE = 115200
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    BASE_X_OFFSET = -10
    BASE_Y_OFFSET = -10

    # Get absolute paths for files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'output')

    # Initialize utilities
    print('Initializing utilities...')
    try:
        bbox_utils = BoundingBoxUtils(SCREEN_WIDTH, SCREEN_HEIGHT, BASE_X_OFFSET, BASE_Y_OFFSET)
        print('BoundingBoxUtils initialized successfully')
    except Exception as e:
        print(f'Failed to initialize BoundingBoxUtils: {str(e)}')
        traceback.print_exc()
        raise

    try:
        print(f'Connecting to device at {BLUETOOTH_COM_PORT}...')
        hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)
        if hasattr(hid, 'ser') and hid.ser and hid.ser.is_open:
            print('Connected successfully to hardware')
        else:
            print('Warning: Serial connection may not be fully established')
    except Exception as e:
        print(f'Failed to connect to hardware: {str(e)}')
        traceback.print_exc()
        raise

    print("Moving to origin")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.move_to_origin()
        print("Moved to origin successfully")
    except Exception as e:
        print(f"ERROR moving to origin: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    # Screen Scope: signin
    csv_file_path = os.path.join(output_dir, 'signin_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print("Moving to origin")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.move_to_origin()
        print("Moved to origin successfully")
    except Exception as e:
        print(f"ERROR moving to origin: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    print(f"Clicking on ID 3")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing bbox_click('3', {csv_file_path}, hid, x_offset=0, y_offset=-100)")
        bbox_utils.bbox_click('3', csv_file_path, hid, x_offset=0, y_offset=-100)
        print("Click completed successfully")
    except Exception as e:
        print(f"ERROR clicking on ID 3: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Adding delay of 5 second(s)")
    time.sleep(5)
    print("Delay completed")
    # Screen Scope: guest
    csv_file_path = os.path.join(output_dir, 'guest_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print("Pressing Enter key")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.press_enter()
        print("Enter key pressed successfully")
    except Exception as e:
        print(f"ERROR pressing Enter key: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    print("Adding delay of 5 second(s)")
    time.sleep(5)
    print("Delay completed")
    # Screen Scope: chromebrowser
    csv_file_path = os.path.join(output_dir, 'chromebrowser_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Typing 'maps.google.com' at ID 1")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('maps.google.com', '1', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)")
        hid.type_input('maps.google.com', '1', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID 1: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Pressing Enter key")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.press_enter()
        print("Enter key pressed successfully")
    except Exception as e:
        print(f"ERROR pressing Enter key: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    print("Adding delay of 10 second(s)")
    time.sleep(10)
    print("Delay completed")
    print(f"Clicking on ID 72")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing bbox_click('72', {csv_file_path}, hid, x_offset=0, y_offset=0)")
        bbox_utils.bbox_click('72', csv_file_path, hid, x_offset=0, y_offset=0)
        print("Click completed successfully")
    except Exception as e:
        print(f"ERROR clicking on ID 72: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    # Screen Scope: googlesignin
    csv_file_path = os.path.join(output_dir, 'googlesignin_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print("Adding delay of 10 second(s)")
    time.sleep(10)
    print("Delay completed")
    print(f"Typing 'hiroshivalencrest8226@gmail.com' at ID 17")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('hiroshivalencrest8226@gmail.com', '17', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)")
        hid.type_input('hiroshivalencrest8226@gmail.com', '17', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID 17: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Pressing Enter key")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.press_enter()
        print("Enter key pressed successfully")
    except Exception as e:
        print(f"ERROR pressing Enter key: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    print("Adding delay of 5 second(s)")
    time.sleep(5)
    print("Delay completed")
    # Screen Scope: googlepassword
    csv_file_path = os.path.join(output_dir, 'googlepassword_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Typing 'elmo1020' at ID 31")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('elmo1020', '31', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)")
        hid.type_input('elmo1020', '31', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID 31: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Pressing Enter key")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.press_enter()
        print("Enter key pressed successfully")
    except Exception as e:
        print(f"ERROR pressing Enter key: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    print("Adding delay of 1 second(s)")
    time.sleep(1)
    print("Delay completed")
    # Screen Scope: googlemaps
    csv_file_path = os.path.join(output_dir, 'googlemaps_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Typing '5000 Legacy Dr Suite 329' at ID Plano")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('5000 Legacy Dr Suite 329', 'Plano', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)")
        hid.type_input('5000 Legacy Dr Suite 329', 'Plano', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID Plano: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Pressing Enter key")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.press_enter()
        print("Enter key pressed successfully")
    except Exception as e:
        print(f"ERROR pressing Enter key: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    # Screen Scope: placedetails
    csv_file_path = os.path.join(output_dir, 'placedetails_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Typing 'Oasis Drug Detox Wellness' at ID 49")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('Oasis Drug Detox Wellness', '49', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)")
        hid.type_input('Oasis Drug Detox Wellness', '49', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID 49: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print(f"Clicking on ID 23")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing bbox_click('23', {csv_file_path}, hid, x_offset=0, y_offset=0)")
        bbox_utils.bbox_click('23', csv_file_path, hid, x_offset=0, y_offset=0)
        print("Click completed successfully")
    except Exception as e:
        print(f"ERROR clicking on ID 23: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    # Screen Scope: category
    csv_file_path = os.path.join(output_dir, 'category_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Typing 'Oasis Drug Detox Wellness' at ID 8")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('Oasis Drug Detox Wellness', '8', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)")
        hid.type_input('Oasis Drug Detox Wellness', '8', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=False, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID 8: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    # Screen Scope: categoryresult
    csv_file_path = os.path.join(output_dir, 'categoryresult_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Clicking on ID 20")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing bbox_click('20', {csv_file_path}, hid, x_offset=0, y_offset=0)")
        bbox_utils.bbox_click('20', csv_file_path, hid, x_offset=0, y_offset=0)
        print("Click completed successfully")
    except Exception as e:
        print(f"ERROR clicking on ID 20: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    # Screen Scope: addmoredetails
    csv_file_path = os.path.join(output_dir, 'addmoredetails_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print("Pressing down key 1 times with 0.5s delay")
    try:
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        hid.press_up_down_loop("down", 1, delay=0.5)
        print("down key pressed 1 times successfully")
    except Exception as e:
        print(f"ERROR pressing down key: {str(e)}")
        traceback.print_exc()
        time.sleep(1)
        raise
    print("Adding delay of 7 second(s)")
    time.sleep(7)
    print("Delay completed")
    print(f"Clicking on ID 20")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing bbox_click('20', {csv_file_path}, hid, x_offset=0, y_offset=0)")
        bbox_utils.bbox_click('20', csv_file_path, hid, x_offset=0, y_offset=0)
        print("Click completed successfully")
    except Exception as e:
        print(f"ERROR clicking on ID 20: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    # Screen Scope: phonecontact
    csv_file_path = os.path.join(output_dir, 'phonecontact_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print("Adding delay of 7 second(s)")
    time.sleep(7)
    print("Delay completed")
    print(f"Typing '(214) 473-4778' at ID 50")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing type_input('(214) 473-4778', '50', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=True, x_offset=0, y_offset=0)")
        hid.type_input('(214) 473-4778', '50', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before=True, x_offset=0, y_offset=0)
        print("Typing completed successfully")
    except Exception as e:
        print(f"ERROR typing at ID 50: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Adding delay of 10 second(s)")
    time.sleep(10)
    print("Delay completed")
    # Screen Scope: okedits
    csv_file_path = os.path.join(output_dir, 'okedits_bbox.csv')
    print(f"Processing {csv_file_path}")
    if not os.path.exists(csv_file_path):
        print(f"WARNING: CSV file not found: {csv_file_path}")
        print("Available files in output directory:")
        try:
            for file in os.listdir(output_dir):
                if file.endswith('.csv'):
                    print(f"  - {file}")
        except Exception as e:
            print(f"Error listing directory: {str(e)}")
    print(f"Clicking on ID 34")
    try:
        # Check if CSV file exists and HID is connected
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:
            print("Error: HID serial connection is not open")
            raise ConnectionError("HID serial connection is not open")
        print(f"Executing bbox_click('34', {csv_file_path}, hid, x_offset=0, y_offset=0)")
        bbox_utils.bbox_click('34', csv_file_path, hid, x_offset=0, y_offset=0)
        print("Click completed successfully")
    except Exception as e:
        print(f"ERROR clicking on ID 34: {str(e)}")
        traceback.print_exc()
        # Pausing to let user see the error
        time.sleep(1)
        raise  # Re-raise to stop execution
    print("Script execution completed!")

if __name__ == '__main__':
    hid = None  # Initialize for finally block
    try:
        print('Starting script execution...')
        main()
        print('Script completed successfully')
    except FileNotFoundError as e:
        print(f"File not found error: {str(e)}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
        print("Please check that the hardware is properly connected and try again.")
        sys.exit(2)
    except Exception as e:
        print(f"Error during script execution: {str(e)}")
        traceback.print_exc()
        sys.exit(3)
    finally:
        print("Script execution finished.")
        # Close any open connections
        if 'hid' in locals() and hid is not None:
            try:
                if hasattr(hid, 'ser') and hid.ser and hid.ser.is_open:
                    print('Closing serial connection...')
                    hid.ser.close()
                    print('Serial connection closed')
            except Exception as e:
                print(f"Error closing serial connection: {str(e)}")