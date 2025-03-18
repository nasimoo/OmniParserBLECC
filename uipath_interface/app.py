from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import subprocess
import sys
from ClickyCC import BoundingBoxUtils, HidUtils

app = Flask(__name__)

# Configuration
BLUETOOTH_COM_PORT = "/dev/tty.usbserial-02242E2E"
BAUD_RATE = 115200
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BASE_X_OFFSET = -7
BASE_Y_OFFSET = -10

# Global variable to track the currently running script process
script_process = None

# Initialize utilities
bbox_utils = BoundingBoxUtils(SCREEN_WIDTH, SCREEN_HEIGHT, BASE_X_OFFSET, BASE_Y_OFFSET)
hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)

# Get the output directory path within uipath_interface
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Available actions from ClickyCC
AVAILABLE_ACTIONS = {
    "click": {
        "name": "Click",
        "description": "Click at a specific bounding box location",
        "parameters": ["bbox_id", "csv_file", "x_offset", "y_offset"]
    },
    "type_input": {
        "name": "Type Input",
        "description": "Type text at a specific location",
        "parameters": ["text", "bbox_id", "csv_file", "click_before", "x_offset", "y_offset"]
    },
    "press_tab": {
        "name": "Press Tab",
        "description": "Press the Tab key",
        "parameters": []
    },
    "press_enter": {
        "name": "Press Enter",
        "description": "Press the Enter key",
        "parameters": []
    },
    "scroll_up": {
        "name": "Scroll Up",
        "description": "Scroll up",
        "parameters": []
    },
    "scroll_down": {
        "name": "Scroll Down",
        "description": "Scroll down",
        "parameters": []
    },
    "move_to_origin": {
        "name": "Move to Origin",
        "description": "Move cursor to origin",
        "parameters": []
    },
    "delay": {
        "name": "Delay",
        "description": "Add a delay between actions",
        "parameters": ["seconds"]
    },
    "up_down_loop": {
        "name": "Up/Down Loop",
        "description": "Press up or down arrow keys multiple times",
        "parameters": ["direction", "times", "delay"]
    },
    "screen_scope": {
        "name": "Screen Scope",
        "description": "Change to a different screen scope",
        "parameters": []
    }
}

@app.route('/')
def index():
    return render_template('index.html', actions=AVAILABLE_ACTIONS)

@app.route('/api/actions', methods=['GET'])
def get_actions():
    return jsonify(AVAILABLE_ACTIONS)

@app.route('/api/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/api/parsed_images', methods=['GET'])
def get_parsed_images():
    parsed_images = []
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            if file.endswith('_bbox.csv'):
                base_name = file[:-9]
                image_path = os.path.join('api/output', f"{base_name}_parsed.png")
                csv_path = os.path.join('output', file)
                parsed_images.append({
                    'name': base_name,
                    'image_path': image_path,
                    'csv_path': csv_path
                })
    return jsonify(parsed_images)

@app.route('/api/bbox_files', methods=['GET'])
def get_bbox_files():
    bbox_files = []
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            if file.endswith('_bbox.csv'):
                bbox_files.append(os.path.join('output', file))
    return jsonify(bbox_files)

@app.route('/api/scripts', methods=['GET'])
def get_scripts():
    scripts = []
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
    if os.path.exists(scripts_dir):
        for file in os.listdir(scripts_dir):
            if file.endswith('.py'):
                scripts.append(file[:-3])  # Remove .py extension
    return jsonify(scripts)

@app.route('/api/load_script', methods=['GET'])
def load_script():
    script_name = request.args.get('name')
    if not script_name:
        return jsonify({"error": "Missing script name"}), 400
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', f"{script_name}.py")
    if not os.path.exists(script_path):
        return jsonify({"error": "Script not found"}), 404
    
    try:
        # Read the script file
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Add debug logging to identify hardware test sections
        if "Testing hardware connection" in script_content:
            print(f"Detected hardware test section in script {script_name}, will skip during parsing")
        
        # Parse the script content to extract actions
        actions = parse_script_content(script_content)
        return jsonify({"actions": actions})
    except Exception as e:
        return jsonify({"error": f"Error loading script: {str(e)}"}), 500

@app.route('/api/save_script', methods=['POST'])
def save_script():
    data = request.json
    script_name = data.get('name')
    actions = data.get('actions')
    
    if not script_name or not actions:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Create the script file
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
    os.makedirs(scripts_dir, exist_ok=True)
    script_path = os.path.join(scripts_dir, f"{script_name}.py")
    
    # Generate Python script content
    script_content = generate_script_content(actions, include_test_movement=False)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return jsonify({"message": "Script saved successfully", "path": script_path})

@app.route('/api/play_script', methods=['POST'])
def play_script():
    global script_process
    try:
        data = request.json
        script_name = data.get('name')
        
        if not script_name:
            return jsonify({"error": "Missing script name"}), 400
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', f"{script_name}.py")
        
        if not os.path.exists(script_path):
            return jsonify({"error": f"Script not found: {script_path}"}), 404
        
        try:
            # Kill any existing process
            if script_process is not None:
                try:
                    script_process.kill()
                except Exception as kill_e:
                    print(f"Warning: Failed to kill existing process: {str(kill_e)}")
                script_process = None
                
            # Get the project root directory (parent of uipath_interface)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Log information about the script being executed
            print(f"Executing script: {script_path}")
            print(f"Working directory: {project_root}")
            print(f"Python executable: {sys.executable}")
            
            # Check if BLUETOOTH_COM_PORT exists before running script
            com_ports = []
            try:
                import serial.tools.list_ports
                com_ports = [port.device for port in serial.tools.list_ports.comports()]
                print(f"Available COM ports: {com_ports}")
            except Exception as e:
                print(f"Warning: Unable to list COM ports: {str(e)}")
            
            # Set up environment variables
            env = os.environ.copy()
            env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
            
            # Enhanced debug mode for Python script
            env['PYTHONUNBUFFERED'] = '1'  # Ensure output is not buffered
            
            # Run the script with increased timeout
            print("Starting subprocess with unbuffered output and line buffering...")
            process = subprocess.Popen(
                [sys.executable, '-u', script_path],  # -u for unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffering
                cwd=project_root,  # Set working directory to project root
                env=env  # Pass the modified environment
            )
            
            print(f"Started process with PID: {process.pid}")
            
            # Store the process globally
            script_process = process
            
            # Read the first 10 lines of the script for debugging
            try:
                with open(script_path, 'r') as f:
                    script_header = ''.join(f.readlines()[:10])
                    print(f"Script header:\n{script_header}...")
            except Exception as read_e:
                print(f"Warning: Unable to read script header: {str(read_e)}")
            
            # Increased timeout to 60 seconds
            try:
                print("Waiting for process to complete...")
                stdout, stderr = process.communicate(timeout=60)
                print("Process completed.")
                # Clear the global process variable if it completed successfully
                if script_process == process:
                    script_process = None
            except subprocess.TimeoutExpired:
                print("Process timed out after 60 seconds.")
                # Only kill if it's still our current process
                if script_process == process:
                    print(f"Killing process {process.pid} due to timeout.")
                    process.kill()
                    stdout, stderr = process.communicate()
                    script_process = None
                else:
                    # Process was already killed by stop_script
                    return jsonify({
                        "message": "Script execution was stopped",
                        "output": "Script execution was stopped by user."
                    })
                return jsonify({
                    "error": "Script execution timed out after 60 seconds",
                    "output": stdout,
                    "error_output": stderr,
                    "error_details": "The script took too long to complete. This could be due to hardware connection issues or a problem in the script itself."
                }), 500
            
            # Print debug information
            print(f"Script execution completed with return code: {process.returncode}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            
            # Check for common error patterns in the output
            error_analysis = analyze_script_output(stdout, stderr)
            
            if process.returncode == 0:
                return jsonify({
                    "message": "Script executed successfully",
                    "output": stdout,
                    "error": stderr
                })
            else:
                return jsonify({
                    "error": f"Script execution failed with return code: {process.returncode}",
                    "output": stdout,
                    "error": stderr,
                    "error_analysis": error_analysis
                }), 500
                
        except Exception as e:
            print(f"Error executing script: {str(e)}")
            import traceback
            traceback_info = traceback.format_exc()
            print(f"Traceback: {traceback_info}")
            return jsonify({
                "error": f"Error executing script: {str(e)}",
                "traceback": traceback_info,
                "details": "There was an error while executing the script. See the traceback for details."
            }), 500
    except Exception as e:
        print(f"Unhandled error in play_script route: {str(e)}")
        import traceback
        traceback_info = traceback.format_exc()
        print(f"Traceback: {traceback_info}")
        return jsonify({
            "error": f"Unhandled error in server: {str(e)}",
            "traceback": traceback_info,
            "details": "There was an unhandled error in the server. Please check the logs for details."
        }), 500

@app.route('/api/stop_script', methods=['POST'])
def stop_script():
    global script_process
    try:
        if script_process is None:
            return jsonify({"message": "No script currently running"}), 200
            
        # Try to terminate the process
        try:
            script_process.terminate()
            # Give it a moment to terminate gracefully
            try:
                script_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate in time
                script_process.kill()
                
            stdout, stderr = script_process.communicate()
            script_process = None
            
            return jsonify({
                "message": "Script stopped successfully",
                "output": stdout if stdout else "",
                "error": stderr if stderr else ""
            })
        except Exception as e:
            return jsonify({"error": f"Error stopping script: {str(e)}"}), 500
    except Exception as e:
        print(f"Unhandled error in stop_script route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Unhandled error in server: {str(e)}"}), 500

def generate_script_content(actions, include_test_movement=False):
    script_lines = []
    # Add the correct import statement
    script_lines.append("import sys")
    script_lines.append("import os")
    script_lines.append("import time")
    script_lines.append("import traceback")
    script_lines.append("sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))")
    script_lines.append("from ClickyCC import BoundingBoxUtils, HidUtils")
    script_lines.append("")
    script_lines.append("def main():")
    script_lines.append("    # BLE Configuration")
    script_lines.append("    BLUETOOTH_COM_PORT = '/dev/tty.usbserial-02242E2E'")
    script_lines.append("    BAUD_RATE = 115200")
    script_lines.append("    SCREEN_WIDTH = 1920")
    script_lines.append("    SCREEN_HEIGHT = 1080")
    script_lines.append("    BASE_X_OFFSET = -10")
    script_lines.append("    BASE_Y_OFFSET = -10")
    script_lines.append("")
    
    # Add code to get absolute paths and setup connection
    script_lines.append("    # Get absolute paths for files")
    script_lines.append("    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))")
    script_lines.append("    output_dir = os.path.join(base_dir, 'output')")
    script_lines.append("")
    script_lines.append("    # Initialize utilities")
    script_lines.append("    print('Initializing utilities...')")
    script_lines.append("    try:")
    script_lines.append("        bbox_utils = BoundingBoxUtils(SCREEN_WIDTH, SCREEN_HEIGHT, BASE_X_OFFSET, BASE_Y_OFFSET)")
    script_lines.append("        print('BoundingBoxUtils initialized successfully')")
    script_lines.append("    except Exception as e:")
    script_lines.append("        print(f'Failed to initialize BoundingBoxUtils: {str(e)}')")
    script_lines.append("        traceback.print_exc()")
    script_lines.append("        raise")
    script_lines.append("")
    
    script_lines.append("    try:")
    script_lines.append("        print(f'Connecting to device at {BLUETOOTH_COM_PORT}...')")
    script_lines.append("        hid = HidUtils(BLUETOOTH_COM_PORT, BAUD_RATE)")
    script_lines.append("        if hasattr(hid, 'ser') and hid.ser and hid.ser.is_open:")
    script_lines.append("            print('Connected successfully to hardware')")
    script_lines.append("        else:")
    script_lines.append("            print('Warning: Serial connection may not be fully established')")
    script_lines.append("    except Exception as e:")
    script_lines.append("        print(f'Failed to connect to hardware: {str(e)}')")
    script_lines.append("        traceback.print_exc()")
    script_lines.append("        raise")
    script_lines.append("")
    
    # Only include the test movement if specifically requested
    if include_test_movement:
        script_lines.append("    # Test hardware connection")
        script_lines.append("    try:")
        script_lines.append("        print('Testing hardware connection with a move_to_origin command...')")
        script_lines.append("        hid.move_to_origin()")
        script_lines.append("        print('Hardware connection test successful')")
        script_lines.append("    except Exception as e:")
        script_lines.append("        print(f'Hardware connection test failed: {str(e)}')")
        script_lines.append("        traceback.print_exc()")
        script_lines.append("        print('Continuing with script execution anyway...')")
        script_lines.append("")

    # Keep track of current screen scope
    current_screen_scope = {
        'name': None,
        'csv_path': None
    }

    # Process each action
    def process_action(action):
        nonlocal current_screen_scope
        action_id = action['id']
        properties = action.get('properties', {})
        
        if action_id == 'screen_scope':
            scope_name = properties.get('name', 'Unnamed Scope')
            csv_path = properties.get('csv_path', '')
            # Clean up the csv_path basename
            csv_basename = os.path.basename(csv_path) if csv_path else 'undefined'
            
            # Only create a new screen scope declaration if it's different from the current one
            if scope_name != current_screen_scope['name'] or csv_basename != current_screen_scope['csv_path']:
                script_lines.append(f"    # Screen Scope: {scope_name}")
                script_lines.append(f"    csv_file_path = os.path.join(output_dir, '{csv_basename}')")
                script_lines.append("    print(f\"Processing {csv_file_path}\")")
                script_lines.append("    if not os.path.exists(csv_file_path):")
                script_lines.append("        print(f\"WARNING: CSV file not found: {csv_file_path}\")")
                script_lines.append("        print(\"Available files in output directory:\")")
                script_lines.append("        try:")
                script_lines.append("            for file in os.listdir(output_dir):")
                script_lines.append("                if file.endswith('.csv'):")
                script_lines.append("                    print(f\"  - {file}\")")
                script_lines.append("        except Exception as e:")
                script_lines.append("            print(f\"Error listing directory: {str(e)}\")")
                
                # Update the current screen scope
                current_screen_scope['name'] = scope_name
                current_screen_scope['csv_path'] = csv_basename
            
            # Process nested actions
            nested_actions = properties.get('actions', [])
            for nested_action in nested_actions:
                process_action(nested_action)
                
        elif action_id == 'click':
            bbox_id = properties.get('bbox_id', '')
            x_offset = properties.get('x_offset', 0)
            y_offset = properties.get('y_offset', 0)
            script_lines.append(f"    print(f\"Clicking on ID {bbox_id}\")")
            script_lines.append(f"    try:")
            script_lines.append(f"        # Check if CSV file exists and HID is connected")
            script_lines.append(f"        if not os.path.exists(csv_file_path):")
            script_lines.append(f"            print(f\"Error: CSV file not found: {{csv_file_path}}\")")
            script_lines.append(f"            raise FileNotFoundError(f\"CSV file not found: {{csv_file_path}}\")")
            script_lines.append(f"        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append(f"            print(\"Error: HID serial connection is not open\")")
            script_lines.append(f"            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append(f"        print(f\"Executing bbox_click('{bbox_id}', {{csv_file_path}}, hid, x_offset={x_offset}, y_offset={y_offset})\")")
            script_lines.append(f"        bbox_utils.bbox_click('{bbox_id}', csv_file_path, hid, x_offset={x_offset}, y_offset={y_offset})")
            script_lines.append(f"        print(\"Click completed successfully\")")
            script_lines.append(f"    except Exception as e:")
            script_lines.append(f"        print(f\"ERROR clicking on ID {bbox_id}: {{str(e)}}\")")
            script_lines.append(f"        traceback.print_exc()")
            script_lines.append(f"        # Pausing to let user see the error")
            script_lines.append(f"        time.sleep(1)")
            script_lines.append(f"        raise  # Re-raise to stop execution")
            
        elif action_id == 'type_input':
            text = properties.get('text', '')
            bbox_id = properties.get('bbox_id', '')
            click_before = properties.get('click_before', 'False').lower() == 'on'
            x_offset = properties.get('x_offset', 0)
            y_offset = properties.get('y_offset', 0)
            script_lines.append(f"    print(f\"Typing '{text}' at ID {bbox_id}\")")
            script_lines.append(f"    try:")
            script_lines.append(f"        # Check if CSV file exists and HID is connected")
            script_lines.append(f"        if not os.path.exists(csv_file_path):")
            script_lines.append(f"            print(f\"Error: CSV file not found: {{csv_file_path}}\")")
            script_lines.append(f"            raise FileNotFoundError(f\"CSV file not found: {{csv_file_path}}\")")
            script_lines.append(f"        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append(f"            print(\"Error: HID serial connection is not open\")")
            script_lines.append(f"            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append(f"        print(f\"Executing type_input('{text}', '{bbox_id}', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before={click_before}, x_offset={x_offset}, y_offset={y_offset})\")")
            script_lines.append(f"        hid.type_input('{text}', '{bbox_id}', bbox_utils=bbox_utils, csv_file_path=csv_file_path, click_before={click_before}, x_offset={x_offset}, y_offset={y_offset})")
            script_lines.append(f"        print(\"Typing completed successfully\")")
            script_lines.append(f"    except Exception as e:")
            script_lines.append(f"        print(f\"ERROR typing at ID {bbox_id}: {{str(e)}}\")")
            script_lines.append(f"        traceback.print_exc()")
            script_lines.append(f"        # Pausing to let user see the error")
            script_lines.append(f"        time.sleep(1)")
            script_lines.append(f"        raise  # Re-raise to stop execution")
            
        elif action_id == 'press_tab':
            script_lines.append("    print(\"Pressing Tab key\")")
            script_lines.append("    try:")
            script_lines.append("        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append("            print(\"Error: HID serial connection is not open\")")
            script_lines.append("            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append("        hid.press_tab()")
            script_lines.append("        print(\"Tab key pressed successfully\")")
            script_lines.append("    except Exception as e:")
            script_lines.append("        print(f\"ERROR pressing Tab key: {str(e)}\")")
            script_lines.append("        traceback.print_exc()")
            script_lines.append("        time.sleep(1)")
            script_lines.append("        raise")
            
        elif action_id == 'press_enter':
            script_lines.append("    print(\"Pressing Enter key\")")
            script_lines.append("    try:")
            script_lines.append("        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append("            print(\"Error: HID serial connection is not open\")")
            script_lines.append("            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append("        hid.press_enter()")
            script_lines.append("        print(\"Enter key pressed successfully\")")
            script_lines.append("    except Exception as e:")
            script_lines.append("        print(f\"ERROR pressing Enter key: {str(e)}\")")
            script_lines.append("        traceback.print_exc()")
            script_lines.append("        time.sleep(1)")
            script_lines.append("        raise")
            
        elif action_id == 'scroll_up':
            script_lines.append("    print(\"Scrolling up\")")
            script_lines.append("    try:")
            script_lines.append("        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append("            print(\"Error: HID serial connection is not open\")")
            script_lines.append("            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append("        hid.scroll_up()")
            script_lines.append("        print(\"Scrolled up successfully\")")
            script_lines.append("    except Exception as e:")
            script_lines.append("        print(f\"ERROR scrolling up: {str(e)}\")")
            script_lines.append("        traceback.print_exc()")
            script_lines.append("        time.sleep(1)")
            script_lines.append("        raise")
            
        elif action_id == 'scroll_down':
            script_lines.append("    print(\"Scrolling down\")")
            script_lines.append("    try:")
            script_lines.append("        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append("            print(\"Error: HID serial connection is not open\")")
            script_lines.append("            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append("        hid.scroll_down()")
            script_lines.append("        print(\"Scrolled down successfully\")")
            script_lines.append("    except Exception as e:")
            script_lines.append("        print(f\"ERROR scrolling down: {str(e)}\")")
            script_lines.append("        traceback.print_exc()")
            script_lines.append("        time.sleep(1)")
            script_lines.append("        raise")
            
        elif action_id == 'move_to_origin':
            script_lines.append("    print(\"Moving to origin\")")
            script_lines.append("    try:")
            script_lines.append("        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append("            print(\"Error: HID serial connection is not open\")")
            script_lines.append("            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append("        hid.move_to_origin()")
            script_lines.append("        print(\"Moved to origin successfully\")")
            script_lines.append("    except Exception as e:")
            script_lines.append("        print(f\"ERROR moving to origin: {str(e)}\")")
            script_lines.append("        traceback.print_exc()")
            script_lines.append("        time.sleep(1)")
            script_lines.append("        raise")
            
        elif action_id == 'delay':
            seconds = properties.get('seconds', '1')  # Default to 1 second if not specified
            script_lines.append(f"    print(\"Adding delay of {seconds} second(s)\")")
            script_lines.append(f"    time.sleep({seconds})")
            script_lines.append(f"    print(\"Delay completed\")")
            
        elif action_id == 'up_down_loop':
            direction = properties.get('direction', 'down')  # Default to down if not specified
            times = properties.get('times', '1')  # Default to 1 time if not specified
            delay = properties.get('delay', '0.5')  # Default to 0.5 seconds delay if not specified
            
            script_lines.append(f"    print(\"Pressing {direction} key {times} times with {delay}s delay\")")
            script_lines.append("    try:")
            script_lines.append("        if not hasattr(hid, 'ser') or not hid.ser or not hid.ser.is_open:")
            script_lines.append("            print(\"Error: HID serial connection is not open\")")
            script_lines.append("            raise ConnectionError(\"HID serial connection is not open\")")
            script_lines.append(f"        hid.press_up_down_loop(\"{direction}\", {times}, delay={delay})")
            script_lines.append(f"        print(\"{direction} key pressed {times} times successfully\")")
            script_lines.append("    except Exception as e:")
            script_lines.append(f"        print(f\"ERROR pressing {direction} key: {{str(e)}}\")")
            script_lines.append("        traceback.print_exc()")
            script_lines.append("        time.sleep(1)")
            script_lines.append("        raise")
    
    # Process all top-level actions
    for action in actions:
        process_action(action)
    
    # Add proper cleanup in a finally block
    script_lines.append("    print(\"Script execution completed!\")")
    script_lines.append("")
    script_lines.append("if __name__ == '__main__':")
    script_lines.append("    hid = None  # Initialize for finally block")
    script_lines.append("    try:")
    script_lines.append("        print('Starting script execution...')")
    script_lines.append("        main()")
    script_lines.append("        print('Script completed successfully')")
    script_lines.append("    except FileNotFoundError as e:")
    script_lines.append("        print(f\"File not found error: {str(e)}\")")
    script_lines.append("        sys.exit(1)")
    script_lines.append("    except ConnectionError as e:")
    script_lines.append("        print(f\"Connection error: {str(e)}\")")
    script_lines.append("        print(\"Please check that the hardware is properly connected and try again.\")")
    script_lines.append("        sys.exit(2)")
    script_lines.append("    except Exception as e:")
    script_lines.append("        print(f\"Error during script execution: {str(e)}\")")
    script_lines.append("        traceback.print_exc()")
    script_lines.append("        sys.exit(3)")
    script_lines.append("    finally:")
    script_lines.append("        print(\"Script execution finished.\")")
    script_lines.append("        # Close any open connections")
    script_lines.append("        if 'hid' in locals() and hid is not None:")
    script_lines.append("            try:")
    script_lines.append("                if hasattr(hid, 'ser') and hid.ser and hid.ser.is_open:")
    script_lines.append("                    print('Closing serial connection...')")
    script_lines.append("                    hid.ser.close()")
    script_lines.append("                    print('Serial connection closed')")
    script_lines.append("            except Exception as e:")
    script_lines.append("                print(f\"Error closing serial connection: {str(e)}\")")
    
    return "\n".join(script_lines)

def parse_script_content(script_content):
    actions = []
    lines = script_content.split('\n')
    current_scope = None
    processed_scopes = set()  # To track processed screen scopes
    
    # Flag to skip the initial move_to_origin test that may be present in scripts
    in_initialization_section = False
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Skip lines that are not important for parsing
        if line.startswith('#') and 'Screen Scope:' not in line:
            continue
        
        # Detect if we're in the initialization section
        if "Initialize utilities" in line or "Test hardware connection" in line:
            in_initialization_section = True
            continue
            
        # If we find the first actual action or screen scope, we're no longer in initialization
        if "Screen Scope:" in line or "hid." in line and "move_to_origin" not in line:
            in_initialization_section = False
        
        # Handle Screen Scope lines
        if 'Screen Scope:' in line:
            # Clean up the scope name (handle both normal and weird syntax)
            if '"' in line or "'" in line:
                # Handle the malformed screen scope lines with quotes and parentheses
                scope_name = line.split('Screen Scope:')[1].strip().rstrip('")').strip()
            else:
                scope_name = line.split('Screen Scope:')[1].strip()
            
            # Skip if we've already processed this scope name to avoid duplicates
            scope_key = scope_name
            if scope_key in processed_scopes:
                continue
                
            processed_scopes.add(scope_key)
            
            current_scope = {
                'id': 'screen_scope',
                'properties': {
                    'name': scope_name,
                    'actions': []
                }
            }
            actions.append(current_scope)
            
        # Handle CSV file path lines
        elif current_scope and 'csv_file_path =' in line:
            # Extract the CSV path from the line
            try:
                if "os.path.join" in line:
                    # Handle the new format with os.path.join
                    csv_parts = line.split("'")
                    if len(csv_parts) >= 2:
                        csv_basename = csv_parts[-2]  # Get the basename
                        # Create the full path
                        csv_path = os.path.join('output', csv_basename)
                        current_scope['properties']['csv_path'] = csv_path
                else:
                    # Handle the old format
                    csv_path = line.split("=")[1].strip().strip("'").strip('"')
                    current_scope['properties']['csv_path'] = csv_path
            except Exception as e:
                print(f"Error parsing CSV path: {e}")
            
        # Handle action lines
        elif 'bbox_utils.bbox_click' in line:
            # Extract parameters from bbox_click call
            params = {}
            
            # Parse the line to extract bbox_id as the first positional argument
            try:
                # Extract everything between the first opening parenthesis and the last closing parenthesis
                parameters_text = line.split('bbox_utils.bbox_click(')[1].rsplit(')', 1)[0]
                
                # Split by commas to get individual parameters
                parameters = parameters_text.split(',')
                
                # First parameter should be bbox_id (strip quotes and spaces)
                if len(parameters) >= 1:
                    bbox_id = parameters[0].strip().strip("'\"")
                    params['bbox_id'] = bbox_id
                
                # Second parameter should be csv_file
                if len(parameters) >= 2:
                    csv_file = parameters[1].strip().strip("'\"")
                    params['csv_file'] = csv_file
                
                # Look for named parameters
                for param in parameters:
                    if 'x_offset=' in param:
                        x_offset = param.split('=')[1].strip()
                        params['x_offset'] = x_offset
                    elif 'y_offset=' in param:
                        y_offset = param.split('=')[1].strip()
                        params['y_offset'] = y_offset
            except Exception as e:
                print(f"Error parsing bbox_click: {e}")
            
            action = {
                'id': 'click',
                'properties': params
            }
            
            # Add to current scope if we're in one, otherwise add to top-level actions
            if current_scope and 'actions' in current_scope['properties']:
                current_scope['properties']['actions'].append(action)
            else:
                actions.append(action)
            
        elif 'hid.type_input' in line:
            # Extract parameters from type_input call
            params = {}
            
            # Parse the line to extract parameters
            try:
                # Extract everything between the first opening parenthesis and the last closing parenthesis
                parameters_text = line.split('hid.type_input(')[1].rsplit(')', 1)[0]
                
                # Split by commas to get individual parameters
                parameters = parameters_text.split(',')
                
                # First parameter should be text (strip quotes and spaces)
                if len(parameters) >= 1:
                    text = parameters[0].strip().strip("'\"")
                    params['text'] = text
                
                # Second parameter should be bbox_id
                if len(parameters) >= 2:
                    bbox_id = parameters[1].strip().strip("'\"")
                    params['bbox_id'] = bbox_id
                
                # Look for named parameters
                for param in parameters:
                    if 'csv_file_path=' in param:
                        csv_file = param.split('=')[1].strip().strip("'\"")
                        params['csv_file'] = csv_file
                    elif 'click_before=' in param:
                        click_before = param.split('=')[1].strip()
                        params['click_before'] = click_before
                    elif 'x_offset=' in param:
                        x_offset = param.split('=')[1].strip()
                        params['x_offset'] = x_offset
                    elif 'y_offset=' in param:
                        y_offset = param.split('=')[1].strip()
                        params['y_offset'] = y_offset
            except Exception as e:
                print(f"Error parsing type_input: {e}")
            
            action = {
                'id': 'type_input',
                'properties': params
            }
            
            # Add to current scope if we're in one, otherwise add to top-level actions
            if current_scope and 'actions' in current_scope['properties']:
                current_scope['properties']['actions'].append(action)
            else:
                actions.append(action)
            
        elif 'hid.press_tab' in line:
            if current_scope:
                current_scope['properties']['actions'].append({
                    'id': 'press_tab',
                    'properties': {}
                })
            else:
                actions.append({
                    'id': 'press_tab',
                    'properties': {}
                })
                
        elif 'hid.press_enter' in line:
            if current_scope:
                current_scope['properties']['actions'].append({
                    'id': 'press_enter',
                    'properties': {}
                })
            else:
                actions.append({
                    'id': 'press_enter',
                    'properties': {}
                })
                
        elif 'hid.scroll_up' in line:
            if current_scope:
                current_scope['properties']['actions'].append({
                    'id': 'scroll_up',
                    'properties': {}
                })
            else:
                actions.append({
                    'id': 'scroll_up',
                    'properties': {}
                })
                
        elif 'hid.scroll_down' in line:
            if current_scope:
                current_scope['properties']['actions'].append({
                    'id': 'scroll_down',
                    'properties': {}
                })
            else:
                actions.append({
                    'id': 'scroll_down',
                    'properties': {}
                })
                
        # Handle up/down loop actions
        elif 'hid.press_up_down_loop' in line:
            # Try to extract parameters
            params = {}
            try:
                # Extract everything between parentheses
                parameters_text = line.split('hid.press_up_down_loop(')[1].rsplit(')', 1)[0]
                
                # Split parameters by comma
                parameters = parameters_text.split(',')
                
                # Parse direction parameter (should be first parameter)
                if len(parameters) >= 1:
                    direction = parameters[0].strip().strip('"\'')
                    params['direction'] = direction
                    
                # Parse times parameter (should be second parameter)
                if len(parameters) >= 2:
                    times = parameters[1].strip()
                    # Remove int() if present
                    if 'int(' in times:
                        times = times.replace('int(', '').replace(')', '')
                    params['times'] = times
                    
                # Look for delay parameter
                for param in parameters:
                    if 'delay=' in param:
                        delay = param.split('=')[1].strip()
                        params['delay'] = delay
                        
            except Exception as e:
                print(f"Error parsing press_up_down_loop parameters: {e}")
                
            # Add the action with parsed parameters
            if current_scope:
                current_scope['properties']['actions'].append({
                    'id': 'up_down_loop',
                    'properties': params
                })
            else:
                actions.append({
                    'id': 'up_down_loop',
                    'properties': params
                })
                
        elif 'hid.move_to_origin' in line:
            # Skip if this is in the initialization section or test section
            in_test_section = False
            
            # Check previous lines for test or initialization indicators
            for i in range(max(0, idx-10), idx):
                if i < len(lines) and ('Test hardware connection' in lines[i] or 
                                      'Testing hardware' in lines[i] or
                                      'Initialize utilities' in lines[i]):
                    in_test_section = True
                    break
            
            if in_test_section or in_initialization_section:
                # Skip this move_to_origin as it's likely just the test
                continue
            
            action = {
                'id': 'move_to_origin',
                'properties': {}
            }
            
            if current_scope and 'actions' in current_scope['properties']:
                current_scope['properties']['actions'].append(action)
            else:
                actions.append(action)
            
        elif 'time.sleep(' in line and not line.startswith('time.sleep(1)'):
            seconds = line.split('time.sleep(')[1].split(')')[0]
            action = {
                'id': 'delay',
                'properties': {'seconds': seconds}
            }
            
            if current_scope and 'actions' in current_scope['properties']:
                current_scope['properties']['actions'].append(action)
            else:
                actions.append(action)
    
    return actions

def analyze_script_output(stdout, stderr):
    """Analyze script output to identify common issues"""
    analysis = []
    
    # Check for common error patterns
    if "FileNotFoundError" in stderr:
        analysis.append("File not found error detected. Please check if the CSV files exist in the output directory.")
    
    if "ConnectionError" in stderr or "Serial" in stderr and "error" in stderr.lower():
        analysis.append("Hardware connection error detected. Please check if the device is properly connected.")
    
    if "Permission" in stderr and ("denied" in stderr.lower() or "error" in stderr.lower()):
        analysis.append("Permission error detected. The script may not have access to required resources.")
    
    if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
        analysis.append("Module import error detected. Please check if all required dependencies are installed.")
    
    if "Traceback" in stderr:
        analysis.append("Python exception detected. Check the error output for detailed traceback information.")
    
    # Check if hardware connection failed
    if "Failed to connect to hardware" in stdout:
        analysis.append("Hardware connection failed. Please check if the device is properly connected and the COM port is correct.")
    
    # Check if CSV file is not found
    if "CSV file not found" in stdout:
        analysis.append("CSV file not found. Please check if the bounding box files exist in the output directory.")
    
    if not analysis:
        analysis.append("Unknown error. Please check the error output for details.")
    
    return analysis

if __name__ == '__main__':
    app.run(debug=True) 