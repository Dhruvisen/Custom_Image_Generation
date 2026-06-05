import os
import glob
from PIL import Image
from datasets import Dataset, Features, Image as DatasetsImage, Value

def upload_to_hub(processed_dir, captions_dir, dataset_name="office-workspace-dataset"):
    print("Preparing dataset for upload...")
    
    image_files = sorted(glob.glob(os.path.join(processed_dir, "*.png")))
    
    data = {"image": [], "text": []}
    valid_count = 0
    
    for img_path in image_files:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        txt_path = os.path.join(captions_dir, f"{base_name}.txt")
        
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                caption = f.read().strip()
            
            # Using the image filepath, the datasets library handles loading it
            data["image"].append(img_path)
            data["text"].append(caption)
            valid_count += 1
            
    if valid_count == 0:
        print("No valid image/caption pairs found.")
        return
        
    print(f"Found {valid_count} image/caption pairs.")
    
    # Define features
    features = Features({
        "image": DatasetsImage(),
        "text": Value("string")
    })
    
    # Create dataset
    hf_dataset = Dataset.from_dict(data, features=features)
    
    print(f"Pushing to Hugging Face Hub as private dataset: {dataset_name}...")
    try:
        # push_to_hub creates the repo if it doesn't exist. private=True ensures it's private.
        hf_dataset.push_to_hub(dataset_name, private=True)
        print(f"\nSuccess! Uploaded {valid_count} pairs to https://huggingface.co/datasets/Dhruvi512/{dataset_name}")
    except Exception as e:
        print(f"\nFailed to push dataset: {e}")
        print("Make sure you are logged in using `huggingface-cli login` and your token has WRITE access.")

if __name__ == "__main__":
    upload_to_hub("../data/processed", "../data/captions")
