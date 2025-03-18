import time
import os
import csv
from PIL import Image
import torch
from util.utils import check_ocr_box, get_som_labeled_img, get_caption_model_processor, get_yolo_model

# Configuration
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
model_path = "weights/icon_detect/model.pt"
BOX_TRESHOLD = 0.05

# Initialize models
som_model = get_yolo_model(model_path)
som_model.to(device)
caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path="weights/icon_caption_florence", device=device)

def process_image(image_path):
    # Load and prepare image
    image = Image.open(image_path)
    image_rgb = image.convert('RGB')
    box_overlay_ratio = max(image.size) / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }

    # Measure OCR time
    start = time.time()
    ocr_bbox_rslt, _ = check_ocr_box(
        image_path, 
        display_img=False, 
        output_bb_format='xyxy', 
        goal_filtering=None, 
        easyocr_args={'paragraph': False, 'text_threshold':0.9}, 
        use_paddleocr=True
    )
    text, ocr_bbox = ocr_bbox_rslt
    cur_time_ocr = time.time()
    ocr_time = cur_time_ocr - start

    # Measure caption time
    dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
        image_path, 
        som_model, 
        BOX_TRESHOLD=BOX_TRESHOLD, 
        output_coord_in_ratio=True, 
        ocr_bbox=ocr_bbox,
        draw_bbox_config=draw_bbox_config, 
        caption_model_processor=caption_model_processor, 
        ocr_text=text,
        use_local_semantics=True, 
        iou_threshold=0.7, 
        scale_img=False, 
        batch_size=128
    )
    cur_time_caption = time.time()
    caption_time = cur_time_caption - cur_time_ocr
    total_time = cur_time_caption - start

    return ocr_time, caption_time, total_time

def main():
    # List of images to process
    images = [
        'imgs/mac_home_vs.png',
        'imgs/google_page.png',
        'imgs/windows_home.png',
        'imgs/mac_home.png',
        'imgs/windows_multitab.png',
        'imgs/omni3.jpg',
        'imgs/ios.png',
        'imgs/word.png',
        'imgs/excel.png'
    ]

    # Process each image and record times
    for image_path in images:
        if not os.path.exists(image_path):
            print(f"Skipping {image_path} - file not found")
            continue

        print(f"\nProcessing {image_path}...")
        try:
            ocr_time, caption_time, total_time = process_image(image_path)
            
            # Update CSV
            rows = []
            with open('processing_times.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

            image_name = os.path.basename(image_path)
            for row in rows:
                if row['Image Name'] == image_name:
                    row['OCR Time (s)'] = f"{ocr_time:.2f}"
                    row['Caption Time (s)'] = f"{caption_time:.2f}"
                    row['Total Time (s)'] = f"{total_time:.2f}"
                    break

            with open('processing_times.csv', 'w', newline='') as csvfile:
                fieldnames = ['Image Name', 'OCR Time (s)', 'Caption Time (s)', 'Total Time (s)']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"Results for {image_name}:")
            print(f"OCR Time: {ocr_time:.2f}s")
            print(f"Caption Time: {caption_time:.2f}s")
            print(f"Total Time: {total_time:.2f}s")

        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")

if __name__ == "__main__":
    main() 