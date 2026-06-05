import os
import requests
from tqdm import tqdm
import time

# ─────────────────────────────────────────────────────────────────────────────
# HOW TO GET YOUR FREE PEXELS API KEY (takes 2 minutes):
#   1. Go to https://www.pexels.com/api/
#   2. Click "Get Started" and create a free account
#   3. Copy your API key and paste it below
# ─────────────────────────────────────────────────────────────────────────────
PEXELS_API_KEY = "F9bVsx4d6BPBNL7nsfCQFw7kJkZqwNWi9FkDla1QY8mm7RBwKLAJKvkm"

HEADERS = {
    "Authorization": PEXELS_API_KEY,
    "User-Agent": "LoracraftBot/1.0"
}

def search_pexels(query, per_page=80, page=1):
    """Search for photos on Pexels and return a list of image URLs."""
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "size": "large",
        "page": page,
    }
    response = requests.get(url, headers=HEADERS, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    # Extract the best quality URLs
    photos = []
    for photo in data.get("photos", []):
        src = photo.get("src", {})
        # Use 'large2x' for high quality, fallback to 'large'
        img_url = src.get("large2x") or src.get("large")
        if img_url:
            photos.append(img_url)
    return photos


def download_single_image(img_url, temp_filename, headers):
    """Download a single image to a temporary file."""
    try:
        response = requests.get(img_url, stream=True, timeout=15, headers=headers)
        response.raise_for_status()

        # Verify content-type
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            return None

        # Determine extension
        if "jpeg" in content_type or "jpg" in content_type:
            ext = "jpg"
        elif "png" in content_type:
            ext = "png"
        else:
            ext = "jpg"

        with open(temp_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return ext
    except Exception:
        # Silently fail, main loop will handle skipped downloads
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass
        return None


def download_images(queries, output_dir, num_images=2100):
    """
    Download office workspace images using the Pexels API.
    """
    if PEXELS_API_KEY == "YOUR_PEXELS_API_KEY" or not PEXELS_API_KEY:
        print("ERROR: Please set your Pexels API key in this script.")
        print("Get a free key at: https://www.pexels.com/api/")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    all_urls = []
    # We fetch up to 4 pages per query to ensure we get plenty of unique images
    pages_to_fetch = 4
    for query in queries:
        print(f"Fetching results for: '{query}'...")
        for page in range(1, pages_to_fetch + 1):
            try:
                urls = search_pexels(query, per_page=80, page=page)
                if not urls:
                    break
                all_urls.extend(urls)
                print(f"  Page {page}: Found {len(urls)} images.")
            except Exception as e:
                print(f"  Error searching for '{query}' (page {page}): {e}")
                break

    # Deduplicate
    all_urls = list(dict.fromkeys(all_urls))
    print(f"\nTotal unique images found: {len(all_urls)}")
    
    if len(all_urls) < num_images:
        print(f"WARNING: Only found {len(all_urls)} unique URLs, which is less than requested {num_images}.")
        num_images = len(all_urls)
        
    print(f"Downloading up to {num_images} in parallel...\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }

    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # We will download files to a temporary name first
    temp_files = []
    downloaded_exts = {}  # maps temp path to its file extension
    
    max_workers = 16
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks
        future_to_url = {}
        for idx, img_url in enumerate(all_urls[:num_images * 2]):  # submit more than needed in case of failures
            temp_path = os.path.join(output_dir, f"temp_{idx:05d}.tmp")
            future = executor.submit(download_single_image, img_url, temp_path, headers)
            future_to_url[future] = (temp_path, img_url)
            
        success_count = 0
        pbar = tqdm(total=num_images, desc="Downloading")
        
        for future in as_completed(future_to_url):
            temp_path, img_url = future_to_url[future]
            try:
                ext = future.result()
                if ext and success_count < num_images:
                    temp_files.append(temp_path)
                    downloaded_exts[temp_path] = ext
                    success_count += 1
                    pbar.update(1)
                else:
                    # If download failed, or we already have enough, delete temp file if it was created
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        pbar.close()

    # Rename temporary files to final names sequentially: raw_0001.jpg, raw_0002.jpg...
    final_count = 0
    for idx, temp_path in enumerate(temp_files):
        if os.path.exists(temp_path):
            ext = downloaded_exts[temp_path]
            final_name = os.path.join(output_dir, f"raw_{final_count + 1:04d}.{ext}")
            os.rename(temp_path, final_name)
            final_count += 1

    print(f"\nDone! Successfully downloaded {final_count} images to '{output_dir}'")


if __name__ == "__main__":
    # Diverse set of queries for a professional office dataset
    queries = [
        "modern office workspace",
        "corporate desk setup",
        "professional office interior",
        "office meeting room",
        "computer workstation desk",
        "home office setup",
        "creative workspace",
        "minimalist desk setup",
        "corporate office building",
        "executive boardroom",
        "coworking space",
        "tech startup office",
    ]
    download_images(queries, "../data/raw_images", num_images=2100)
