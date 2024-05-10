# comic_split
##### 描述 (中文)

- 這個腳本將漫畫圖片分割成兩半並保存在指定的目錄中。它支持各種圖像和壓縮文件格式。

##### 安裝 (中文)

- ```
  pip install -r requirements.txt
  ```

##### 使用方法 (中文)

1. 準備一個包含要分割的漫畫圖片路徑的列表。

2. 使用列表的文件路径和目标目录调用 `split_comics` 函数。

   ```python
   from comic_split import split_comics
   import sys
   
   src_dir = sys.argv[1]  # 包含漫畫圖片路徑的文件的路徑
   dest_dir = sys.argv[2]  # 目標目錄的路徑
   
   cnt = split_comics(src_dir, dest_dir)
   ```

這將會把給定文件路徑列表中的漫畫圖片分割成兩半，並保存在目標目錄中。函數返回處理的漫畫圖片數量。

---

##### 執行範例 (中文)

要運行腳本，使用以下命令：

```bash
python comic_split.py d:\comic d:\comic_split_output
```

在此範例中，`d:\comic ` 是包含您要分割的漫畫圖像的文件路徑的文本文件的路徑。每個文件路徑應在文本文件中的新行上。

`d:\comic_split_output` 是您要保存分割圖像的目錄的路徑。

##### 注意事項 (中文)

- 腳本會檢查圖像的高度是否大於其寬度。如果是，則會複製原始文件而不分割它。

- 腳本支持以下圖像格式：'.png', '.jpg', '.jpeg', '.gif'。

- 腳本也可以處理以下擴展名的壓縮文件：'.zip', '.cbz', '.rar', '.cbr', '.7z'。它將提取圖像，分割它們，並保存在目標目錄中。
