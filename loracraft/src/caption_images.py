import os
import glob
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm
import torch

def generate_captions(processed_dir, captions_dir, trigger_word=None, batch_size=16):
    os.makedirs(captions_dir, exist_ok=True)
    
    image_files = sorted(glob.glob(os.path.join(processed_dir, "*.png")))
    if not image_files:
        print(f"No processed PNG images found in {processed_dir}")
        return
        
    print("Loading BLIP model onto CPU...")
    # Using CPU explicitly as requested
    device = "cpu"
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    
    print(f"Generating captions for {len(image_files)} images (batch_size={batch_size})...")
    
    sample_captions = []
    
    for i in tqdm(range(0, len(image_files), batch_size), desc="Captioning"):
        batch_paths = image_files[i:i + batch_size]
        batch_imgs = []
        valid_paths = []
        
        for filepath in batch_paths:
            try:
                img = Image.open(filepath)
                # The processor expects RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")
                batch_imgs.append(img)
                valid_paths.append(filepath)
            except Exception as e:
                print(f"\nError loading {filepath}: {e}")
                
        if not batch_imgs:
            continue
            
        try:
            # Generate caption
            inputs = processor(images=batch_imgs, return_tensors="pt").to(device)
            out = model.generate(**inputs, max_new_tokens=50)
            
            for filepath, single_out in zip(valid_paths, out):
                caption = processor.decode(single_out, skip_special_tokens=True).strip()
                
                # Prepend trigger word if specified
                if trigger_word:
                    full_caption = f"{trigger_word}, {caption}"
                else:
                    full_caption = caption
                
                # Save to txt
                base_name = os.path.splitext(os.path.basename(filepath))[0]
                txt_path = os.path.join(captions_dir, f"{base_name}.txt")
                
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(full_caption)
                    
                if len(sample_captions) < 3:
                    sample_captions.append(f"{base_name}: {full_caption}")
                    
        except Exception as e:
            print(f"\nError captioning batch starting at {batch_paths[0]}: {e}")
            
    print("\nCaptioning Complete! Here are some samples:")
    for sample in sample_captions:
        print(f"  - {sample}")

if __name__ == "__main__":
    generate_captions("../data/processed", "../data/captions", trigger_word=None, batch_size=16)
