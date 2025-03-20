from Clickyadb import ADBController
import time

# Test the ADBController
print("Initializing ADB Controller...")
try:
    adb = ADBController()
    
    # Get the current state of mobile data
    print("Device ID:", adb.device_id)
    
    # Toggle mobile data OFF
    print("Turning mobile data OFF...")
    adb.toggle_mobile_data("off")
    time.sleep(2)  # Wait for the change to take effect
    
    # Toggle mobile data back ON
    print("Turning mobile data ON...")
    adb.toggle_mobile_data("on")
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {e}") 