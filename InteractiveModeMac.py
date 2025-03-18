import cv2
import subprocess
import numpy as np
import serial
import time

BLUETOOTH_COM_PORT = "/dev/tty.usbserial-02242E2E"
BAUD_RATE = 115200

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 540

# Basic offset
BASE_X_OFFSET = -7
Y_OFFSET = -10

def list_avfoundation_devices():
    """List available AVFoundation devices."""
    try:
        result = subprocess.run(['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''], 
                              capture_output=True, text=True)
        print("Available AVFoundation devices:")
        print(result.stderr)
    except Exception as e:
        print(f"Error listing devices: {e}")

def calculate_x_offset(x):
    """Calculate progressive X offset based on X coordinate"""
    # Start with base offset
    offset = BASE_X_OFFSET
    
    # Add -15 for every 250 pixels
    offset += -8  * (x // 31)    
    return offset

def calculate_y_offset(y):
    """Calculate progressive X offset based on X coordinate"""
    # Start with base offset
    offset = Y_OFFSET
    
    # Add -15 for every 250 pixels
    offset += -8 * (y // 31)
    
    return offset

# List available devices before starting
list_avfoundation_devices()

ffmpeg_cmd = [
    'ffmpeg',
    '-f', 'avfoundation',
    '-rtbufsize', '100M',
    '-framerate', '30',
    '-video_size', f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}',
    '-i', '0',  # Use device index 0 for USB3 Video
    '-pix_fmt', 'bgr24',
    '-f', 'rawvideo',
    '-vsync', '0',  # Disable frame dropping
    '-fflags', '+nobuffer',  # Disable buffering
    '-flags', 'low_delay',  # Minimize latency
    '-'
]

class ClickMemory:
    def __init__(self):
        self.clicks = {}

    def should_click(self, x, y, threshold=1.0):
        if (x, y) not in self.clicks:
            self.clicks[(x, y)] = time.time()
            return True

        last_time = self.clicks[(x, y)]
        if time.time() - last_time > threshold:
            self.clicks[(x, y)] = time.time()
            return True

        return False

def send_command(ser, cmd):
    """Send a command string over BLE."""
    ser.write((cmd + "\n").encode('utf-8'))
    print(f"Sent: {cmd}")  # Debug output
    time.sleep(0.1)

def main():
    ser = serial.Serial(BLUETOOTH_COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give it more time to settle

    # Move to (0,0) before any testing happens
    print("Moving to initial position (0,0)...")
    send_command(ser, "ABS:0,0")
    time.sleep(0.5)  # Wait for movement to complete

    try:
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        click_memory = ClickMemory()

        last_click_time = time.time()
        last_pos = None
        current_pos = (0, 0)
        current_scaled_pos = (0, 0)

        def mouse_callback(event, display_x, display_y, flags, param):
            nonlocal last_click_time, last_pos, current_pos, current_scaled_pos

            # Dynamically calculate scaling factors based on screen vs. display
            scaling_factor_x = SCREEN_WIDTH / DISPLAY_WIDTH
            scaling_factor_y = SCREEN_HEIGHT / DISPLAY_HEIGHT

            # Scale the display coordinates first
            scaled_x = int(display_x * scaling_factor_x)
            scaled_y = int(display_y * scaling_factor_y)

            # Apply offsets
            x_offset = calculate_x_offset(scaled_x)
            y_offset = calculate_y_offset(scaled_y)

            actual_x = scaled_x + x_offset
            actual_y = scaled_y + y_offset

            current_pos = (display_x, display_y)
            current_scaled_pos = (actual_x, actual_y)

            if event == cv2.EVENT_LBUTTONDOWN:
                if click_memory.should_click(actual_x, actual_y):
                    # Send the combined move and click command
                    click_cmd = f"CLICK:{actual_x},{actual_y}"
                    send_command(ser, click_cmd)
                    last_pos = (display_x, display_y)
                    last_click_time = time.time()
                    print(f"Clicked at scaled coords: {actual_x},{actual_y}")
                    print(f"X offset applied: {x_offset}")  # Debug info
                    print(f"Y offset applied: {y_offset}")  # Debug info

                else:
                    print("Click ignored – too soon or same spot as last time.")

        cv2.namedWindow("Capture Card Feed")
        cv2.setMouseCallback("Capture Card Feed", mouse_callback)

        while True:
            # Read frame data
            raw_frame = process.stdout.read(SCREEN_WIDTH * SCREEN_HEIGHT * 3)
            if not raw_frame:
                # Check if ffmpeg has any error output
                error = process.stderr.read1().decode()
                if error:
                    print(f"FFmpeg error: {error}")
                break

            # Make it writable so we can draw on it
            frame = np.frombuffer(raw_frame, np.uint8).reshape((SCREEN_HEIGHT, SCREEN_WIDTH, 3)).copy()

            # Check if frame is valid
            if frame.size == 0:
                print("Received empty frame")
                continue

            # Resize for display
            resized_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

            # # Overlay current mouse positions (both display and actual)
            # cv2.putText(
            #     resized_frame,
            #     f"Display: {current_pos[0]}, {current_pos[1]}",
            #     (10, 30),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     0.7,
            #     (0, 255, 0),
            #     2
            # )
            # cv2.putText(
            #     resized_frame,
            #     f"Actual: {current_scaled_pos[0]}, {current_scaled_pos[1]}",
            #     (10, 60),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     0.7,
            #     (0, 255, 0),
            #     2
            # )

            # Draw current mouse position
            cv2.circle(resized_frame, current_pos, 5, (0, 0, 255), -1)
            cv2.line(resized_frame, (current_pos[0]-10, current_pos[1]), (current_pos[0]+10, current_pos[1]), (0, 0, 255), 1)
            cv2.line(resized_frame, (current_pos[0], current_pos[1]-10), (current_pos[0], current_pos[1]+10), (0, 0, 255), 1)

            # Draw a dot where we last clicked
            if last_pos:
                cv2.circle(resized_frame, last_pos, 5, (0, 255, 0), -1)

            cv2.imshow("Capture Card Feed", resized_frame)

            # Process any pending events
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC to quit
                break
            elif key == ord('r'):  # 'r' to restart ffmpeg
                print("Restarting ffmpeg...")
                process.terminate()
                process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)  # Give it time to start
    except Exception as e:
        print(f"Error in main: {e}")
        if 'process' in locals():
            process.terminate()
        raise
    finally:
        ser.close()
        if 'process' in locals():
            process.terminate()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()