from sys import argv
import os
from PIL import Image
from pathlib import Path
import os
import shutil
from pathlib import Path
from zipfile import ZipFile
from rarfile import RarFile

import shutil  # Import the shutil module

def is_image_file(filename):
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    extension = os.path.splitext(filename)[1].lower()
    return extension in image_extensions

def splitComicDbPic(file_path_list, dest_dir):
    for file_path in file_path_list:
        image = Image.open(file_path)  # Open the image
        width, height = image.size  # Get the image dimensions
        #print(f"Processing image: {file_path} , {width}x{height}")

        # Check if height is larger than width and copy the original file if so
        if height > width:
            dest_path = Path(dest_dir) / Path(file_path).name
            image.save(dest_path)
            print(f"{os.path.basename(file_path)}: Copied original file to {os.path.basename(dest_path)}")
            continue
        
        # Calculate the new dimensions for each half
        half_width = width // 2
        half_height = height

        # Split the image in half vertically
        left_half = image.crop((0, 0, half_width, height))
        right_half = image.crop((half_width, 0, width, height))

        # Save the split images
        name = os.path.splitext(os.path.basename(file_path))[0]
        for i, half in enumerate([left_half, right_half], 1):
            output_path = os.path.join(dest_dir, f"{name}_{i:02d}")
            _, extension = os.path.splitext(file_path)
            half.save(output_path + extension)
            #print(f"{os.path.basename(file_path)}: Saved half: {output_path} with {half_width}x{half_height}")
            print("#", end="")
    print("")

def splitComicDbPicByDir(src_dir, dest_dir):
    file_list = []
    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)
        if os.path.isfile(file_path) and is_image_file(filename):
            file_list.append(file_path)
    
    splitComicDbPic(file_list, dest_dir)

def splitComicByDir(src_dir, dest_dir):
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        relative_dir = Path(root).relative_to(src_dir)

        # Create corresponding directory structure in dest_dir
        destination_root = dest_dir / relative_dir
        destination_base = dest_dir / relative_dir.parent
        destination_base.mkdir(parents=True, exist_ok=True)
        print(f"destination_base {destination_root}")

        image_files = []
        archive_files = []

        for filename in files:
            file_path = Path(root) / filename
            extension = file_path.suffix.lower()

            if is_image_file(filename):
                image_files.append(file_path)
            elif extension in ['.zip', '.cbz', '.rar', '.cbr']:
                archive_files.append(file_path)

        if len(dirs) == 0 and len(image_files) > 0:
            temp_dir = Path(dest_dir) / f"temp_{relative_dir.name}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            splitComicDbPic(image_files, temp_dir)

            # Compress the processed images into a .cbz file
            cbz_file = destination_root.with_suffix('.cbz')  # Fix the destination path
            print("cbz_file: ", cbz_file)
            with ZipFile(cbz_file, 'w') as zipf:
                for image_file in temp_dir.iterdir():
                    zipf.write(image_file, arcname=image_file.name)
            print(f"Compressed {len(image_files)} images into {cbz_file}")

            # Delete the temporary directory
            shutil.rmtree(temp_dir)

        elif len(archive_files) > 0:
            temp_dir1 = Path(dest_dir) / f"temp1_{relative_dir.name}"
            temp_dir1.mkdir(parents=True, exist_ok=True)

            for archive_file in archive_files:
                if archive_file.suffix.lower() in ['.zip', '.cbz']:
                    with ZipFile(archive_file, 'r') as zipf:
                        zipf.extractall(temp_dir1)
                elif archive_file.suffix.lower() in ['.rar', '.cbr']:
                    with RarFile(archive_file, 'r') as rar:
                        rar.extractall(temp_dir1)

            temp_dir2 = Path(dest_dir) / f"temp2_{relative_dir.name}"
            temp_dir2.mkdir(parents=True, exist_ok=True)

            splitComicDbPicByDir(temp_dir1, temp_dir2)

            # Compress the processed images into a .cbz file
            cbz_file = destination_root / f"{relative_dir.stem}.cbz"
            with ZipFile(cbz_file, 'w') as zipf:
                for image_file in temp_dir2.iterdir():
                    zipf.write(image_file, arcname=image_file.name)

            # Delete the temporary directories
            shutil.rmtree(temp_dir1)
            shutil.rmtree(temp_dir2)


if __name__ == "__main__":
    if len(argv) < 3:
        print(f'Usage: python {argv[0]} <src_dir> <dest_dir>')
        exit()
    splitComicByDir(argv[1], argv[2])
