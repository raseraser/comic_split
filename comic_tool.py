import os, sys
import json
import shutil
from sys import argv
from pathlib import Path
from PIL import Image
from zipfile import ZipFile
import patoolib
import tkinter as tk
import argparse
import logging

IMAGE_QUALITY = 90
LOG_FILE = 'tool.log'

# Set up the logger
logging.basicConfig(filename=LOG_FILE, filemode='w', level=logging.INFO)

def loginfo(message, end='\n', flush=False):
    print(message, end=end, flush=flush)
    logging.info(message)

def errorinfo(message, end='\n', flush=False):
    message = f"Error: {message}"
    print(message, end=end, flush=flush)
    logging.info(message)

def log(message):
    logging.info(message)

def info(message, end='\n', flush=False):
    print(message, end=end, flush=flush)


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
        try:
            image = Image.open(file_path)  # Open the image
        except Exception as e:
            loginfo(f"{file_path} open Error: {e}")
            continue
        width, height = image.size  # Get the image dimensions

        # Check if height is larger than width and copy the original file if so
        if height > width:
            dest_path = Path(dest_dir) / Path(file_path).name
            shutil.copy(file_path, dest_path)
            loginfo("O", end="", flush=True)
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
            #output_path = os.path.join(dest_dir, f"{name}_{i:02d}")
            # Right haft page is first page, Left haft page is second page
            output_path = os.path.join(dest_dir, f"{name}_{'1L' if i == 1 else '0R'}")
            _, extension = os.path.splitext(file_path)
            half.save(output_path + extension, quality=IMAGE_QUALITY)
            log(f">   {file_path} -> {output_path}{extension}")
            info("#", end="", flush=True)
    info("", flush=True)
    return len(file_path_list)

def split_comic_pics_bydir(src_dir, dest_dir):
    file_list = []
    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)
        if os.path.isfile(file_path) and is_image_file(filename):
            file_list.append(file_path)
    return split_comic_pics(file_list, dest_dir)

def copy_comic_pics(file_path_list, dest_dir):
    for file_path in file_path_list:
        shutil.copy(file_path, dest_dir)
    return len(file_path_list)

def copy_comic_pics_bydir(src_dir, dest_dir):
    file_list = []
    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)
        if os.path.isfile(file_path) and is_image_file(filename):
            file_list.append(file_path)
    return copy_comic_pics(file_list, dest_dir)

def process_comics(src_dir, dest_dir, do_split=True):
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

        loginfo(f"> scan {relative_dir} ...")
        for filename in files:
            file_path = Path(root) / filename
            extension = file_path.suffix.lower()
            if is_image_file(filename):
                image_files.append(file_path)
            elif is_compress_file(filename):
                archive_files.append(file_path)

        if len(image_files) > 0:
            comic_cnt += 1
            loginfo(f"> Process images files in {relative_dir} ...")
            destination_base = dest_dir / relative_dir.parent
            destination_base.mkdir(parents=True, exist_ok=True)

            temp_dir = Path(dest_dir) / f"temp_{relative_dir.name}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            if do_split:
                cnt = split_comic_pics(image_files, temp_dir)
            else:
                cnt = copy_comic_pics(image_files, temp_dir)

            # Compress the processed images into a .cbz file
            cbz_file = destination_root.with_suffix('.cbz')  # Fix the destination path
            with ZipFile(cbz_file, 'w') as zipf:
                for image_file in temp_dir.iterdir():
                    zipf.write(image_file, arcname=image_file.name)
            loginfo(f"> Compressed {cnt} images into {cbz_file}")

            # Delete the temporary directory
            shutil.rmtree(temp_dir)

        elif len(archive_files) > 0:
            destination_root.mkdir(parents=True, exist_ok=True)

            for archive_file in archive_files:
                temp_dir1 = Path(dest_dir) / f"temp1_{relative_dir.name}"
                temp_dir1_org = temp_dir1
                comic_cnt += 1
                loginfo(f"> Process archive file {archive_file} ...")
                # if archive_file.suffix.lower() in ['.zip', '.cbz']:
                #     with ZipFile(archive_file, 'r') as zipf:
                #         zipf.extractall(temp_dir1)
                # elif archive_file.suffix.lower() in ['.rar', '.cbr']:
                #     with RarFile(archive_file, 'r') as rar:
                #         rar.extractall(temp_dir1)
                # elif archive_file.suffix.lower() in ['.7z']:
                #     with py7zr.SevenZipFile(archive_file, mode='r') as szf:
                #         szf.extractall(temp_dir1)
                patoolib.extract_archive(str(archive_file), outdir=str(temp_dir1))
                
                # 針對解出來的 temp_dir1 , 先判斷該目錄底有是否只有一個目錄？若是，則進入該目錄，temp_dir1 也加上該目錄名稱
                # Check if temp_dir1 contains only one directory
                subdirs = [d for d in os.listdir(temp_dir1) if os.path.isdir(os.path.join(temp_dir1, d))]
                if len(subdirs) == 1:
                    # If so, update temp_dir1 to be that directory
                    temp_dir1 = temp_dir1 / subdirs[0]

                temp_dir2 = Path(dest_dir) / f"temp2_{relative_dir.name}"
                temp_dir2.mkdir(parents=True, exist_ok=True)

                if do_split:
                    cnt = split_comic_pics_bydir(temp_dir1, temp_dir2)
                else:
                    cnt = copy_comic_pics_bydir(temp_dir1, temp_dir2)

                # Compress the processed images into a .cbz file
                cbz_file = destination_root / f"{archive_file.stem}.cbz"
                with ZipFile(cbz_file, 'w') as zipf:
                    for image_file in temp_dir2.iterdir():
                        zipf.write(image_file, arcname=image_file.name)
                loginfo(f"> Compressed {cnt} images into {cbz_file}")

                # Delete the temporary directories
                shutil.rmtree(temp_dir1_org)
                shutil.rmtree(temp_dir2)
            loginfo(f"> Compressed {len(archive_files)} archives files.")
        else:
            loginfo(f"> skip {relative_dir} ...")
    return comic_cnt

import re
def gather_seqs(file_list):
    numbers = {}
    for filepath in file_list:
        filename = os.path.basename(filepath)
        match = re.search(r'\d+', filename)
        if match:
            numbers[int(match.group())] = filepath
    return numbers

def renum_comics(src_dir):
    file_list = []
    rename_list = {}
    loginfo(f"> scan {src_dir} ...")
    for root, dirs, files in os.walk(src_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            if is_image_file(filename):
                file_list.append(file_path)
        seqs = gather_seqs(file_list)

        # 檢查 seqs 有沒有從 1 開始, 而且有2,3,4,...到最後 len(seqs), 數字不能重複
        # 使用 chk_idx 與 seqs 的 iterator idx 檢查是否一致, chk_idx 從 1 開始
        chk_idx = 1
        for seq in sorted(seqs.keys()):
            if seq != chk_idx:
                loginfo(f"> {src_dir} 圖片編號不連續, 有可能有遺漏: {seq} != {chk_idx}, skip!")
                return  # 假如不一致, skip renumber
            chk_idx += 1
        
        # 假如seq<100, digital用兩位數, 假如seq<1000, digital用三位數, 以此類推,
        # 至少3位數, 用最大的seq來決定
        if seqs:
            seq_digits = len(str(max(seqs.keys())))
            if seq_digits < 3:
                seq_digits = 3
            seq_format = f"{{:0{seq_digits}d}}"
            for seq, filepath in sorted(seqs.items()):
                new_filename = seq_format.format(seq) + os.path.splitext(filepath)[1]
                new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
                #檢查是否需要做 rename
                if filepath != new_filepath:
                    #os.rename(filepath, new_filepath)
                    rename_list[filepath] = new_filepath
                    log(f">   {filepath} -> {new_filepath}")
                info("#", end="", flush=True)
            info("", flush=True)
        seqs.clear()
        file_list.clear()

    # 詢問是否要 rename
    cnt = len(rename_list)
    if cnt > 0:
        loginfo(f"Total {cnt} files need to be renumbered. check out {LOG_FILE} for details.")
        answer = input("Do you want to rename these files? (y/n): ")
        if answer.lower() == 'y':
            for src, dest in rename_list.items():
                os.rename(src, dest)
                loginfo(f">   {src} -> {dest}")
        else:
            loginfo("Rename operation cancelled.")
            cnt = 0
    return cnt

import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)

    def flush(self):
        pass

def show_ui():
    def save_dirs(src_dir, dest_dir):
        with open('dirs.json', 'w') as f:
            json.dump({'src_dir': src_dir, 'dest_dir': dest_dir}, f)

    def load_dirs():
        if os.path.exists('dirs.json'):
            with open('dirs.json', 'r') as f:
                dirs = json.load(f)
                return dirs['src_dir'], dirs['dest_dir']
        else:
            return '', ''
        
    def browse_src_dir():
        src_dir = filedialog.askdirectory()
        src_dir_entry.delete(0, tk.END)
        src_dir_entry.insert(tk.END, src_dir)
        save_dirs(src_dir, dest_dir_entry.get())

    def browse_dest_dir():
        dest_dir = filedialog.askdirectory()
        dest_dir_entry.delete(0, tk.END)
        dest_dir_entry.insert(tk.END, dest_dir)
        save_dirs(src_dir_entry.get(), dest_dir)

    def start_split():
        src_dir = src_dir_entry.get()
        dest_dir = dest_dir_entry.get()
        threading.Thread(target=split_comics, args=(src_dir, dest_dir)).start()
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future = executor.submit(split_comics, src_dir, dest_dir)
        #     cnt = future.result()
        #     loginfo(f"Total {cnt} comic(s) processed.")
            
    src_dir, dest_dir = load_dirs()
    loginfo(f"src_dir: {src_dir}, dest_dir: {dest_dir}")
    root = tk.Tk()

    src_dir_label = tk.Label(root, text="Source Directory")
    src_dir_label.grid(row=0, column=0)
    src_dir_entry = tk.Entry(root, width=50)
    src_dir_entry.grid(row=0, column=1, sticky='ew')
    src_dir_entry.insert(tk.END, src_dir)
    src_dir_button = tk.Button(root, text="Browse", command=browse_src_dir)
    src_dir_button.grid(row=0, column=2)

    dest_dir_label = tk.Label(root, text="Destination Directory")
    dest_dir_label.grid(row=1, column=0)
    dest_dir_entry = tk.Entry(root, width=50)
    dest_dir_entry.grid(row=1, column=1, sticky='ew')
    dest_dir_entry.insert(tk.END, dest_dir)
    dest_dir_button = tk.Button(root, text="Browse", command=browse_dest_dir)
    dest_dir_button.grid(row=1, column=2)

    start_button = tk.Button(root, text="START", command=start_split)
    start_button.grid(row=2, column=0, columnspan=3)

    output_text = scrolledtext.ScrolledText(root)
    output_text.grid(row=3, column=0, columnspan=3, sticky='nsew')

    sys.stdout = TextRedirector(output_text)

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', help='The command to execute')

    split_parser = subparsers.add_parser('split', help='Split comics into individual pages')
    split_parser.add_argument('src_dir', help='The source directory')
    split_parser.add_argument('dest_dir', help='The destination directory')

    compress_parser = subparsers.add_parser('compress', help='Compress files only, not split')
    compress_parser.add_argument('src_dir', help='The source directory')
    compress_parser.add_argument('dest_dir', help='The destination directory')

    renum_parser = subparsers.add_parser('renum', help='Renumber files')
    renum_parser.add_argument('src_dir', help='The source directory')

    gui_parser = subparsers.add_parser('gui', help='Show graphical user interface')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    if args.command == 'split':
        cnt = process_comics(args.src_dir, args.dest_dir, do_split=True)
        loginfo(f"Total {cnt} comic(s) processed.")
    elif args.command == 'compress':
        cnt = process_comics(args.src_dir, args.dest_dir, do_split=False)
        loginfo(f"Total {cnt} comic(s) processed.")
    elif args.command == 'renum':
        cnt = renum_comics(args.src_dir)
        loginfo(f"Total {cnt} files renumbered.")
    elif args.command == 'gui':
        show_ui()

if __name__ == '__main__':
    main()
