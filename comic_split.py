from sys import argv
import os
from PIL import Image
from pathlib import Path

def splitComicDbPic(file_path, dest_dir):
    image = Image.open(file_path)  # Open the image
    width, height = image.size  # Get the image dimensions
    print(f"Processing image: {file_path}")
    print(f"Image dimensions: {width}x{height}")

    # Check if height is larger than width and copy the original file if so
    if height > width:
        dest_path = Path(dest_dir) / Path(file_path).name
        image.save(dest_path)
        print(f"Copied original file to {dest_path}")
        return
    
    # Calculate the new dimensions for each half
    half_width = width // 2
    half_height = height

    print(f"New dimensions for each half: {half_width}x{half_height}")

    # Split the image in half vertically
    left_half = image.crop((0, 0, half_width, height))
    right_half = image.crop((half_width, 0, width, height))

    # Save the split images
    name = os.path.splitext(os.path.basename(file_path))[0]
    for i, half in enumerate([left_half, right_half], 1):
        output_path = os.path.join(dest_dir, f"{name}_{i:02d}")
        _, extension = os.path.splitext(file_path)
        half.save(output_path + extension)
        print(f"Saved half: {output_path}")

def splitComicByDir(src_dir, dest_dir):
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        relative_dir = Path(root).relative_to(src_dir)

        # Create corresponding directory structure in dest_dir
        destination_root = dest_dir / relative_dir
        destination_root.mkdir(parents=True, exist_ok=True)

        for filename in files:
            file_path = Path(root) / filename
            splitComicDbPic(file_path, destination_root)


if __name__ == "__main__":
    if len(argv) < 3:
        print(f'Usage: python {argv[0]} <src_dir> <dest_dir>')
        exit()
    splitComicByDir(argv[1], argv[2])
    
