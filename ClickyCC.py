import serial
import time
import csv
import ast
import random


class BoundingBoxUtils:
    def __init__(self, screen_width, screen_height, base_x_offset, base_y_offset):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.base_x_offset = base_x_offset
        self.base_y_offset = base_y_offset

    def calculate_x_offset(self, x):
        """Calculate progressive X offset based on X coordinate."""
        try:
            offset = self.base_x_offset
            offset += -8  * (x // 31)    
            return int(offset)  # Ensure the result is an integer
        except Exception as e:
            print(f"Error in calculate_x_offset with x={x}: {e}")
            return 0  # Default to 0 if there's an issue
    def calculate_y_offset(self, y):
        """Calculate progressive Y offset based on Y coordinate."""
        try:
            offset = self.base_y_offset
            offset += -8 * (y // 31)
            return int(offset)  # Ensure the result is an integer
        except Exception as e:
            print(f"Error in calculate_y_offset with y={y}: {e}")
            return 0  # Default to 0 if there's an issue

    def find_bounding_box_by_id(self, specific_id, csv_file_path):
        """
        Finds the bounding box for a specific ID in a CSV file and returns
        the center (x, y) coordinates in screen pixels.
        """
        try:
            with open(csv_file_path, "r") as csv_file:
                reader = csv.DictReader(csv_file)

                for row in reader:
                    if row["ID"] == specific_id:
                        try:
                            bbox = ast.literal_eval(row["bbox"])
                            if not (isinstance(bbox, (list, tuple)) and len(bbox) == 4):
                                raise ValueError(f"Malformed bbox data: {row['bbox']}")
                        except Exception as e:
                            print(f"Error parsing bbox for ID {specific_id}: {e}")
                            return None

                        print(f"Found bbox {bbox} for ID: {specific_id}")

                        x_min = int(bbox[0] * self.screen_width)
                        y_min = int(bbox[1] * self.screen_height)
                        x_max = int(bbox[2] * self.screen_width)
                        y_max = int(bbox[3] * self.screen_height)

                        x_center = (x_min + x_max) // 2
                        y_center = (y_min + y_max) // 2

                        return x_center, y_center

                print(f"Bounding box with ID '{specific_id}' not found in the CSV.")
                return None

        except FileNotFoundError:
            print(f"CSV file not found: {csv_file_path}")
        except Exception as e:
            print(f"Failed to read CSV file: {e}")
        return None

    def bbox_click(self, specific_id, csv_file_path, click_ds, x_offset=0, y_offset=0):
        """
        Process a click action for a given ID using bounding box data and BLE commands.
        Args:
            specific_id (str): The ID to locate in the CSV file.
            csv_file_path (str): Path to the CSV file containing bounding box data.
            click_ds (object): The HID utility instance for sending commands.
            x_offset (int): Optional additional horizontal offset (default is 0).
            y_offset (int): Optional additional vertical offset (default is 0).
        """
        bbox = self.find_bounding_box_by_id(specific_id, csv_file_path)
        if bbox:
            # Calculate the adjusted coordinates without altering the base offsets
            x, y = bbox
            x += self.calculate_x_offset(x)  # Apply base_x_offset
            y += self.calculate_y_offset(y)  # Apply base_y_offset

            # Add the user-provided offsets
            x += x_offset
            y += y_offset

            print(f"Clicking at adjusted position ({x}, {y}) for ID {specific_id}")

            click_ds.move_to(x, y)  # Move to the computed position
            click_ds.send_command("CLICK")  # Perform a click
            time.sleep(0.5)  # Ensure the click action completes
        else:
            print(f"ID {specific_id} not found in {csv_file_path}")


class HidUtils:
    def __init__(self, com_port, baud_rate):
        self.ser = self.initialize_serial_connection(com_port, baud_rate)

    def initialize_serial_connection(self, com_port, baud_rate):
        try:
            ser = serial.Serial(com_port, baud_rate, timeout=1)
            time.sleep(2)
            print("Connected to BLE device")
            return ser
        except Exception as e:
            print(f"Failed to connect to BLE device: {e}")
            return None

    def send_command(self, cmd):
        if self.ser:
            try:
                self.ser.write((cmd + "\n").encode('utf-8'))
                print(f"Sent: {cmd}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Failed to send command: {e}")

    def move_to_origin(self):
        self.send_command("ABS:0,0")
        time.sleep(1)



    def type_input(self, text, csv_id=None, bbox_utils=None, csv_file_path=None, click_before=False, x_offset=0, y_offset=0):
        """
        Sends a string of text as keyboard input with randomized keystroke delays.
        Ensures previous actions (like clicks) are completed before typing.
        """
        if self.ser:
            try:
                if click_before and csv_id and bbox_utils and csv_file_path:
                    bbox_utils.bbox_click(csv_id, csv_file_path, self, x_offset=x_offset, y_offset=y_offset)

                print(f"Typing text: {text}")
                
                for char in text:
                    if char == ' ':
                        # Send a command explicitly for space
                        self.send_command("kbd:space")
                    else:
                        self.send_command(f"kbd:{char}")
                    delay = random.uniform(0.05, 0.2)  # Random delay
                    time.sleep(delay)
                
                print(f"Finished typing: {text}")

            except Exception as e:
                print(f"Error in type_input: {e}")


    def press_tab(self):
        """
        Sends the Tab key press command.
        """
        self.send_command("tab")
        time.sleep(1)
        print("Tab key pressed.")
    def fullscreen(self):
        """
        Sends the F11 key press command.
        """
        self.send_command("f11")
        time.sleep(1)
        print("F11 key pressed.")
    def refresh_page(self):
        """
        Sends the F5 key press command.
        """
        self.send_command("f5")
        time.sleep(1)
        print("F5 key pressed.")

    def scroll_up(self):
        """
        Sends a command to scroll up.
        """
        self.send_command("scrollUp")
        time.sleep(1)
        print("Scrolled up.")

    def scroll_down(self):
        """
        Sends a command to scroll down.
        """
        self.send_command("scrollDown")
        time.sleep(1)
        print("Scrolled down.")
    def scroll_loop(self, direction, times, delay=0.1):
        """
        Scrolls up or down a specified number of times, with an optional delay.

        Args:
            direction (str): The direction of scrolling, either "up" or "down".
            times (int): The number of times to scroll in the specified direction.
            delay (float): The delay in seconds between each scroll. Default is 1 second.
        """
        if not isinstance(times, int) or times < 1:
            print("Invalid number of times. It must be a positive integer.")
            return

        if direction not in ["up", "down"]:
            print("Invalid direction. Use 'up' or 'down'.")
            return

        try:
            for i in range(times):
                if direction == "up":
                    self.scroll_up()
                elif direction == "down":
                    self.scroll_down()
                print(f"Scrolled {direction} {i + 1}/{times} times")
                time.sleep(delay)  # Introduce the delay between scrolls
        except Exception as e:
            print(f"Error in scrolling: {e}")


    def press_enter(self):
        """
        Sends the Enter key press command.
        """
        self.send_command("enter")
        time.sleep(1)    
        print("Enter key pressed.")
    def move_to(self, x, y):
        """
        Moves the cursor to the specified x, y coordinates without clicking.
        """
        self.send_command(f"ABS:{x},{y}")
        print(f"Moved cursor to ({x}, {y}) without clicking.")
        time.sleep(1)
    def press_up_down_loop(self, direction, times, delay=0.5):
        """
        Presses the "up" or "down" key a specified number of times.

        Args:
            direction (str): The direction of key press, either "up" or "down".
            times (int): The number of times to press the specified key.
        """
        if not isinstance(times, int) or times < 1:
            print("Invalid number of times. It must be a positive integer.")
            return

        if direction not in ["up", "down"]:
            print("Invalid direction. Use 'up' or 'down'.")
            return
        try:
            for i in range(times):
                self.send_command(direction)  # Sends "up" or "down" to the BLE device
                print(f"Pressed {direction} key {i + 1}/{times} times")
                time.sleep(delay)  # Small delay between presses
        except Exception as e:
            print(f"Error in pressing keys: {e}")