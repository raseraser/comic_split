import os
import shutil
from sys import argv
from pathlib import Path
from PIL import Image
from zipfile import ZipFile
from rarfile import RarFile
import py7zr

def is_image_file(filename):
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    extension = os.path.splitext(filename)[1].lower()
    return extension in image_extensions

def is_compress_file(filename):
    compress_extensions = ['.zip', '.cbz', '.rar', '.cbr', '.7z']
    extension = os.path.splitext(filename)[1].lower()
    return extension in compress_extensions

def split_comic_pics(file_path_list, dest_dir):
    """
    Split the comic pictures in the given file path list into halves and save them in the destination directory.

    Args:
        file_path_list (list): A list of file paths of the comic pictures to be split.
        dest_dir (str): The destination directory where the split images will be saved.

    Returns:
        int: The number of comic pictures processed.

    Raises:
        None

    """
    for file_path in file_path_list:
        image = Image.open(file_path)  # Open the image
        width, height = image.size  # Get the image dimensions

        # Check if height is larger than width and copy the original file if so
        if height > width:
            dest_path = Path(dest_dir) / Path(file_path).name
            image.save(dest_path)
            print("#", end="", flush=True)
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
            print("#", end="", flush=True)
    print("", flush=True)
    return len(file_path_list)

def split_comic_pics_bydir(src_dir, dest_dir):
    file_list = []
    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)
        if os.path.isfile(file_path) and is_image_file(filename):
            file_list.append(file_path)
    return split_comic_pic(file_list, dest_dir)

def split_comics(src_dir, dest_dir):
    """
    Split the comic files in the source directory into separate directories and compress them into .cbz files.

    Args:
        src_dir (str): The path to the source directory containing the comic files.
        dest_dir (str): The path to the destination directory where the compressed .cbz files will be saved.

    Returns:
        int: The total number of comic files processed.

    Raises:
        FileNotFoundError: If the source directory does not exist.
    """
    src_dir = Path(src_dir)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    comic_cnt = 0

    for root, dirs, files in os.walk(src_dir):
        relative_dir = Path(root).relative_to(src_dir)
        # Create corresponding directory structure in dest_dir
        destination_root = dest_dir / relative_dir

        image_files = []
        archive_files = []

        print(f"> scan {relative_dir} ...")
        for filename in files:
            file_path = Path(root) / filename
            extension = file_path.suffix.lower()
            if is_image_file(filename):
                image_files.append(file_path)
            elif is_compress_file(filename):
                archive_files.append(file_path)

        if len(dirs) == 0 and len(image_files) > 0:
            comic_cnt += 1
            print(f"> Process images files in {relative_dir} ...")
            destination_base = dest_dir / relative_dir.parent
            destination_base.mkdir(parents=True, exist_ok=True)

            temp_dir = Path(dest_dir) / f"temp_{relative_dir.name}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            cnt = split_comic_pics(image_files, temp_dir)

            # Compress the processed images into a .cbz file
            cbz_file = destination_root.with_suffix('.cbz')  # Fix the destination path
            with ZipFile(cbz_file, 'w') as zipf:
                for image_file in temp_dir.iterdir():
                    zipf.write(image_file, arcname=image_file.name)
            print(f"> Compressed {cnt} images into {cbz_file}")

            # Delete the temporary directory
            shutil.rmtree(temp_dir)

        elif len(archive_files) > 0:
            destination_root.mkdir(parents=True, exist_ok=True)
            temp_dir1 = Path(dest_dir) / f"temp1_{relative_dir.name}"
            #temp_dir1.mkdir(parents=True, exist_ok=True)

            for archive_file in archive_files:
                comic_cnt += 1
                print(f"> Process archive file {archive_file} ...")
                if archive_file.suffix.lower() in ['.zip', '.cbz']:
                    with ZipFile(archive_file, 'r') as zipf:
                        zipf.extractall(temp_dir1)
                elif archive_file.suffix.lower() in ['.rar', '.cbr']:
                    with RarFile(archive_file, 'r') as rar:
                        rar.extractall(temp_dir1)
                elif archive_file.suffix.lower() in ['.7z']:
                    with py7zr.SevenZipFile(archive_file, mode='r') as szf:
                        szf.extractall(temp_dir1)

                temp_dir2 = Path(dest_dir) / f"temp2_{relative_dir.name}"
                temp_dir2.mkdir(parents=True, exist_ok=True)

                cnt = split_comic_pics_bydir(temp_dir1, temp_dir2)

                # Compress the processed images into a .cbz file
                cbz_file = destination_root / f"{archive_file.stem}.cbz"
                with ZipFile(cbz_file, 'w') as zipf:
                    for image_file in temp_dir2.iterdir():
                        zipf.write(image_file, arcname=image_file.name)
                print(f"> Compressed {cnt} images into {cbz_file}")

                # Delete the temporary directories
                shutil.rmtree(temp_dir1)
                shutil.rmtree(temp_dir2)
            print(f"> Compressed {len(archive_files)} archives files.")
        else:
            print(f"> skip {relative_dir} ...")
    return comic_cnt

if __name__ == "__main__":
    if len(argv) < 3:
        print(f'Usage: python {argv[0]} <src_dir> <dest_dir>')
        exit()
    cnt = split_comics(argv[1], argv[2])
    print(f"Total {cnt} comic(s) processed.")
