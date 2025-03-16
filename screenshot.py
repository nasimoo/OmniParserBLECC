import io
import os
import torch
from PIL import Image
import pyautogui
import time
import base64
import pandas as pd
from util.utils import (
    get_som_labeled_img,
    check_ocr_box,
    get_caption_model_processor,
    get_yolo_model
)

# Ensure output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Configure device for Apple Silicon
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
torch.backends.mps.enable_fallback_on_unsupported_ops = True

# Force MPS device for Apple Silicon
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f"Using device: {device}")

@torch.inference_mode()
def convert_model_to_float32(model):
    """Efficiently convert model to float32 for MPS compatibility"""
    if hasattr(model, 'float'):
        return model.float()
    return model

def process_screenshot(screenshot_path, som_model, caption_model_processor):
    """Process a single screenshot with optimized settings for M1/M2"""
    try:
        # OCR processing with optimized settings for Mac
        ocr_bbox_rslt, _ = check_ocr_box(
            screenshot_path,
            display_img=False,
            output_bb_format='xyxy',
            goal_filtering=None,
            easyocr_args={'paragraph': False, 'text_threshold': 0.9},
            use_paddleocr=True
        )
        text, ocr_bbox = ocr_bbox_rslt

        # Configure box overlay with Mac-optimized ratios
        image = Image.open(screenshot_path)
        box_overlay_ratio = max(image.size) / 3200
        draw_bbox_config = {
            'text_scale': 0.8 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
        }

        # Run detection and captioning with M1/M2 optimized settings
        dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
            screenshot_path,
            som_model,
            BOX_TRESHOLD=0.05,
            output_coord_in_ratio=True,
            ocr_bbox=ocr_bbox,
            draw_bbox_config=draw_bbox_config,
            caption_model_processor=caption_model_processor,
            ocr_text=text,
            use_local_semantics=True,
            iou_threshold=0.7,
            scale_img=False,
            batch_size=64  # Increased batch size for M1/M2
        )

        return dino_labeled_img, label_coordinates, parsed_content_list
    except Exception as e:
        print(f"Error processing screenshot: {str(e)}")
        return None, None, None

def main():
    # Load and optimize models for MPS
    print("Loading and optimizing models for Apple Silicon...")
    
    # Load YOLO model with MPS optimizations
    model_path = 'weights/icon_detect/model.pt'
    som_model = get_yolo_model(model_path)
    if device == 'mps':
        som_model = convert_model_to_float32(som_model)
    som_model.to(device)
    
    # Load caption model with MPS optimizations
    caption_model_processor = get_caption_model_processor(
        model_name="florence2",
        model_name_or_path="weights/icon_caption_florence",
        device=device
    )
    if device == 'mps' and hasattr(caption_model_processor, 'model'):
        caption_model_processor['model'] = convert_model_to_float32(caption_model_processor['model'])
        if hasattr(caption_model_processor['model'], 'vision_tower'):
            caption_model_processor['model'].vision_tower = convert_model_to_float32(
                caption_model_processor['model'].vision_tower
            )
    
    print("Models loaded and optimized successfully")
    
    try:
        start_time = time.time()
        
        # Take screenshot with Mac-optimized settings
        print("\nTaking screenshot...")
        screenshot_path = os.path.join(output_dir, "screenshot.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path, optimize=True, quality=95)
        
        # Process screenshot
        print("Processing screenshot...")
        results = process_screenshot(screenshot_path, som_model, caption_model_processor)
        dino_labeled_img, label_coordinates, parsed_content_list = results
        
        if dino_labeled_img is not None:
            # Save results efficiently
            output_image_path = os.path.join(output_dir, "labeled_screenshot.png")
            decoded_image = Image.open(io.BytesIO(base64.b64decode(dino_labeled_img)))
            decoded_image.save(output_image_path, optimize=True, quality=95)
            print(f"Saved labeled image to: {output_image_path}")
            
            output_csv_path = os.path.join(output_dir, "parsed_content.csv")
            df = pd.DataFrame(parsed_content_list)
            df['ID'] = range(len(df))
            df.to_csv(output_csv_path, index=False)
            print(f"Saved parsed content to: {output_csv_path}")
            
            print(f"\nTotal processing time: {time.time() - start_time:.2f}s")
        else:
            print("Failed to process screenshot")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
