import os
import glob
from PIL import Image

def review_captions(processed_dir, captions_dir):
    image_files = sorted(glob.glob(os.path.join(processed_dir, "*.png")))
    
    if not image_files:
        print("No images found to review.")
        return
        
    total = len(image_files)
    print(f"Starting review of {total} image/caption pairs.")
    print("Close the image window after viewing to proceed to the prompt.")
    print("-" * 50)
    
    for i, img_path in enumerate(image_files):
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        txt_path = os.path.join(captions_dir, f"{base_name}.txt")
        
        if not os.path.exists(txt_path):
            print(f"[{i+1}/{total}] Missing caption for {base_name}, skipping.")
            continue
            
        with open(txt_path, "r", encoding="utf-8") as f:
            current_caption = f.read().strip()
            
        print(f"\n[{i+1}/{total}] Image: {base_name}.png")
        print(f"Current Caption: {current_caption}")
        
        # Show image
        try:
            img = Image.open(img_path)
            img.show()
        except Exception as e:
            print(f"Could not display image: {e}")
            
        # Prompt user
        user_input = input("Edit caption? (press Enter to keep, or type new caption): ").strip()
        
        if user_input:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(user_input)
            print("Caption updated!")
        else:
            print("Caption kept.")
            
    print("\nReview complete!")

if __name__ == "__main__":
    review_captions("../data/processed", "../data/captions")
