# comic_split
##### Description (English)

- This script splits comic images into halves and saves them in a specified directory. It supports various image and compressed file formats.

##### Installation (English)

- ```
  pip install -r requirements.txt
  ```

##### Usage (English)

1. Prepare a list of file paths of the comic pictures to be split.

2. Call the `split_comics` function with the list of file paths and the destination directory.

   ```python
   from comic_split import split_comics
   import sys
   
   src_dir = sys.argv[1]  # path to the file containing list of comic image paths
   dest_dir = sys.argv[2]  # path to the destination directory
   
   cnt = split_comics(src_dir, dest_dir)
   ```

This will split the comic pictures in the given file path list into halves and save them in the destination directory. The function returns the number of comic pictures processed.

##### Execution Example (English)

To run the script, use the following command:

```bash
python comic_split.py d:\comic d:\comic_split_output
```

In this example, `d:\comic` is the path to a text file that contains the file paths of the comic images you want to split. Each file path should be on a new line in the text file.

`d:\comic_split_output` is the path to the directory where you want to save the split images.

##### Note (English)

- The script checks if the height of the image is larger than its width. If so, it copies the original file without splitting it.

- The script supports the following image formats: '.png', '.jpg', '.jpeg', '.gif'.

- The script can also process compressed files with the following extensions: '.zip', '.cbz', '.rar', '.cbr', '.7z'. It will extract the images, split them, and save them in the destination directory.

