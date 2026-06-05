import os
import glob
from PIL import Image

def process_images(raw_dir, processed_dir, target_size=512):
    os.makedirs(processed_dir, exist_ok=True)
    
    # Get all common image formats
    extensions = ('*.png', '*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.PNG')
    raw_files = []
    for ext in extensions:
        raw_files.extend(glob.glob(os.path.join(raw_dir, ext)))
        
    print(f"Found {len(raw_files)} images in {raw_dir}")
    
    processed_count = 0
    skipped_count = 0
    
    for idx, filepath in enumerate(raw_files):
        try:
            with Image.open(filepath) as img:
                # Skip if too small
                if img.width < 300 or img.height < 300:
                    skipped_count += 1
                    continue
                    
                # Convert to RGB (handles RGBA, grayscale, etc)
                img = img.convert("RGB")
                
                # Center crop to square
                min_dim = min(img.width, img.height)
                left = (img.width - min_dim) / 2
                top = (img.height - min_dim) / 2
                right = (img.width + min_dim) / 2
                bottom = (img.height + min_dim) / 2
                
                img_cropped = img.crop((left, top, right, bottom))
                
                # Resize using LANCZOS  
                img_resized = img_cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
                
                # Save as PNG
                out_filename = f"image_{processed_count+1:04d}.png"
                out_path = os.path.join(processed_dir, out_filename)
                
                img_resized.save(out_path, "PNG")
                processed_count += 1
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            skipped_count += 1
            
    print("-" * 30)
    print(f"Processing Complete.")
    print(f"Processed successfully: {processed_count}")
    print(f"Skipped (too small/errors): {skipped_count}")

if __name__ == "__main__":
    process_images("../data/raw_images", "../data/processed", target_size=512)
