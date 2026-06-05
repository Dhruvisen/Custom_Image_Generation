# Custom Image Generation with LoRA (Loracraft)

A complete end-to-end pipeline to download images, preprocess them, auto-caption using BLIP, review captions interactively, upload datasets to Hugging Face Hub, and train a LoRA model on Google Colab.

---

## 📁 Project Structure

```
custom_img_gen/
├── README.md                  # Detailed project overview and flow
├── requirements.txt           # Python library dependencies
├── Custom_img_gen.ipynb       # Google Colab notebook for LoRA training/inference
├── .gitignore                 # Files excluded from GitHub (venv, datasets, weights)
└── loracraft/
    ├── data/                  # Local data storage (Ignored by Git)
    │   ├── raw_images/        # Raw downloads from Pexels API
    │   ├── processed/         # Center-cropped & resized 512x512 PNGs
    │   └── captions/          # Generated BLIP descriptions (.txt)
    └── src/                   # Python source code scripts
        ├── download_images.py # Downloads raw images in parallel from Pexels
        ├── prepare_dataset.py # Crops, resizes, and processes raw images
        ├── caption_images.py  # Generates BLIP descriptions automatically
        ├── review_captions.py # CLI to review and edit captions
        ├── upload_dataset.py  # Bundles and uploads dataset to Hugging Face
        ├── train_lora.py      # Local placeholders
        ├── inference.py       # Local placeholders
        └── app.py             # Local placeholders
```

---

## 🔄 Project Flow & Workflow

The pipeline is split into two parts: a **Local Data Curation Phase** (runs on CPU/local machine) and a **Cloud Training Phase** (runs on Google Colab GPU).

### Phase 1: Local Data Curation
1. **Download Raw Dataset (`download_images.py`)**:
   - Searches and downloads high-resolution images from Pexels using target queries (e.g., "modern office workspace", "creative desk setup").
   - Utilizes thread-pools to download up to 2100 images in parallel.
   
2. **Process and Resize (`prepare_dataset.py`)**:
   - Inspects downloaded images, discarding any below 300x300 pixels.
   - Performs a center-square crop and resizes them to `512x512` PNG format (using PIL Lanczos filter) to prepare them for training.

3. **Generate AI Captions (`caption_images.py`)**:
   - Runs Salesforce's `blip-image-captioning-base` locally on CPU.
   - Automatically generates descriptions for each processed image and saves them in individual `.txt` files.
   - Optional: Prepends a custom token/trigger word to the captions.

4. **Review Captions Interactively (`review_captions.py`)**:
   - Displays each processed image side-by-side with its BLIP description.
   - Allows manually editing and refining captions via interactive prompt.

5. **Upload to Hugging Face Hub (`upload_dataset.py`)**:
   - Combines image files and text captions into a Hugging Face `Dataset` structure.
   - Pushes the dataset privately to Hugging Face Hub (e.g., `Dhruvi512/office-workspace-dataset`).

---

### Phase 2: LoRA Training & Inference on Google Colab
6. **Colab Training (`Custom_img_gen.ipynb`)**:
   - Open and run the notebook in a GPU-accelerated Google Colab environment.
   - Installs Diffusers, PEFT, Transformers, Accelerate, and BitsAndBytes.
   - Logs into Hugging Face to fetch the private dataset created in Phase 1.
   - Fine-tunes a model (such as Stable Diffusion or FLUX) using LoRA (Low-Rank Adaptation) to learn the features of your custom image dataset.
   - Saves model weights as a `.safetensors` file.

7. **Inference (`Custom_img_gen.ipynb`)**:
   - Loads the base model + trained LoRA weights.
   - Generates high-quality custom images based on text prompts.

---

## 🛠️ Getting Started (Local Machine)

### 1. Installation
Set up a virtual environment and install the required Python libraries:
```bash
# Initialize virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Pexels API Key
Open `loracraft/src/download_images.py` and set your `PEXELS_API_KEY`:
```python
PEXELS_API_KEY = "YOUR_API_KEY_HERE"
```

### 3. Run the Pipeline
Run the scripts sequentially to prepare and upload your dataset:
```bash
# Step 1: Download raw images
python loracraft/src/download_images.py

# Step 2: Crop & resize images
python loracraft/src/prepare_dataset.py

# Step 3: Auto-generate captions
python loracraft/src/caption_images.py

# Step 4: Interactively review captions
python loracraft/src/review_captions.py

# Step 5: Login to Hugging Face (Required once)
huggingface-cli login

# Step 6: Push dataset to Hugging Face Hub
python loracraft/src/upload_dataset.py
```
