import requests
import base64
import json
import argparse
import os
import sys

def encode_image_to_base64(image_path):
    """Read an image file and return its base64 encoded string.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded string of the image
        
    Raises:
        FileNotFoundError: If the image file doesn't exist
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
        
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded

def generate_response_with_image(image_path, prompt, element_to_find=None, model="gemma3:4b", api_url="http://localhost:11434/api/generate"):
    """Send a multimodal request to the specified model with the encoded image and prompt.
    
    Args:
        image_path (str): Path to the image file
        prompt (str): Text prompt to send to the model
        element_to_find (str): Specific element to look for in the image
        model (str): Name of the Ollama model to use
        api_url (str): URL of the Ollama API
        
    Returns:
        dict: Contains the model's response and status information
        
    Raises:
        Exception: For various API or processing errors
    """
    try:
        base64_image = encode_image_to_base64(image_path)
        
        # Create an enhanced prompt with clear instructions for a yes/no answer
        enhanced_prompt = prompt
        if element_to_find:
            enhanced_prompt = f"""You are an expert in UI analysis. 
Look at this screenshot and tell me if the element '{element_to_find}' is present.
Begin your answer with 'YES' or 'NO' clearly.
Then explain your reasoning briefly. 
Only focus on the element I specified.
Original prompt: {prompt}"""
        
        data = {
            "model": model,
            "prompt": enhanced_prompt,
            "images": [base64_image],
            "stream": False  # Request a complete response instead of streaming
        }
        
        print(f"Sending request to {api_url} using model {model}...")
        response = requests.post(api_url, json=data, stream=True, timeout=60)
        
        if response.status_code != 200:
            return {
                "error": f"API error: {response.status_code}",
                "status_code": response.status_code,
                "response": ""
            }
            
        print(f"Response status code: {response.status_code}")
        
        # Handle streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        full_response += json_response['response']
                        # Print progress indicator
                        sys.stdout.write(".")
                        sys.stdout.flush()
                    if json_response.get('done', False):
                        break
                except json.JSONDecodeError as e:
                    print(f"\nError decoding JSON: {e}")
                    print(f"Problematic line: {line[:100]}...")
        
        print("\nResponse complete.")
        
        # Extract yes/no answer if possible
        yes_no_answer = "UNCERTAIN"
        if full_response.strip().upper().startswith("YES"):
            yes_no_answer = "YES"
        elif full_response.strip().upper().startswith("NO"):
            yes_no_answer = "NO"
        
        return {
            "response": full_response,
            "yes_no": yes_no_answer,
            "status_code": response.status_code,
            "model": model
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request error: {str(e)}",
            "status_code": 0,
            "response": ""
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "status_code": 0,
            "response": ""
        }

def main():
    """Main function to parse arguments and run the image analysis."""
    parser = argparse.ArgumentParser(description="Analyze images using Ollama models")
    parser.add_argument("--image", type=str, 
                        default="/Users/nasimo/Workspace/OmniParserBLECC/uipath_interface/output/washpoweroptions1_parsed.png",
                        help="Path to the image file")
    parser.add_argument("--prompt", type=str, default="Is element button 'add a missing place' found in the screen?",
                        help="Prompt to send to the model")
    parser.add_argument("--element", type=str, default="add a missing place",
                        help="Specific UI element to look for")
    parser.add_argument("--model", type=str, default="gemma3:4b",
                        help="Name of the Ollama model to use")
    parser.add_argument("--api-url", type=str, default="http://localhost:11434/api/generate",
                        help="URL of the Ollama API")
    
    args = parser.parse_args()
    
    # Display run information
    print(f"Image: {args.image}")
    print(f"Prompt: {args.prompt}")
    print(f"Element to find: {args.element}")
    print(f"Model: {args.model}")
    
    # Generate response
    result = generate_response_with_image(args.image, args.prompt, args.element, args.model, args.api_url)
    
    # Check for errors
    if "error" in result:
        print(f"\nError: {result['error']}")
        return
    
    # Display response
    print("\nComplete response from model:")
    print(result['response'])
    
    # Display yes/no result clearly
    if "yes_no" in result:
        print(f"\n===== ELEMENT DETECTION RESULT =====")
        print(f"Element '{args.element}': {result['yes_no']}")
        print("====================================")

if __name__ == '__main__':
    main()
