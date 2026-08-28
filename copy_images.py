import os
import glob
import shutil

brain_dir = r"C:\Users\laxman\.gemini\antigravity\brain\9628aab6-7cd4-401c-9f37-0752732ca001"
target_dir = r"c:\Users\laxman\Desktop\SYNTRO TECH\frontend\images"

os.makedirs(target_dir, exist_ok=True)

for filepath in glob.glob(os.path.join(brain_dir, "*_cover_*.jpg")):
    filename = os.path.basename(filepath)
    category_name = filename.split('_cover_')[0]
    dest_path = os.path.join(target_dir, f"{category_name}.jpg")
    shutil.copy(filepath, dest_path)
    print(f"Copied {filename} -> {dest_path}")
