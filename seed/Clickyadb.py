import subprocess

class ADBController:
    def __init__(self):
        """Initialize and check if a device is connected."""
        self.device_id = self.get_device_id()
        if not self.device_id:
            raise Exception("No device found. Make sure USB debugging is enabled and authorized.")

    def run_adb_command(self, command):
        """Runs an ADB command and returns the output."""
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def get_device_id(self):
        """Get the connected ADB device ID."""
        devices = self.run_adb_command("adb devices")
        lines = devices.split("\n")[1:]  # Skip header
        for line in lines:
            if "device" in line and "unauthorized" not in line:
                return line.split()[0]
        return None

    def toggle_mobile_data(self, state):
        """Turn Mobile Data ON or OFF."""
        if state.lower() == "on":
            self.run_adb_command("adb shell svc data enable")
            print("Mobile Data turned ON.")
        elif state.lower() == "off":
            self.run_adb_command("adb shell svc data disable")
            print("Mobile Data turned OFF.")
        else:
            print("Invalid state. Use 'on' or 'off'.")

