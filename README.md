# TinyVectorDB
A simple search engine for ITHome news.


## Environment setup

To setup a conda environment and install related dependencies.
```
conda create --name bce python=3.10 -y
conda activate bce
git clone https://github.com/vyj97/TinyVectorDB/
cd TinyVectorDB
python -m pip install -r requirements.txt
```

## Some user guide to use bce-embedding-base model in Huggingface

1. Login to your [Huggingface](https://huggingface.co/) account.
2. Proceed to https://huggingface.co/settings/tokens and generate a new token (token type=Read)
3. Execute command below in your machine and paste the token generated:
   ```
   huggingface-cli login
   ```
4. Proceed to https://huggingface.co/maidalun1020/bce-embedding-base_v1/, then select "agree and access respository".

## Running program
#### Case 1: Provide query sentence directly from command line
 ```
 python3 search.py --query-sentence [MY QUERY SENTENCE] --limit [LIMIT NUM OF DOCS RETURNED] --num_articles [NUM OF DOCS PARSED FROM ITHOME]
 # Example: python3 search.py --query-sentence 資安問題 --limit 3 --num_articles 30
 ```

#### Case 2: Provide query sentence using keyboard input after executing the program (allowing multiple query inputs)
 ```
 python3 search.py --limit [LIMIT NUM OF DOCS RETURNED] --num_articles [NUM OF DOCS PARSED FROM ITHOME]
 # Example: python3 search.py --limit 3 --num_articles 30
 ```

## Extra 
#### 1. 當我們的使用情境不止需要 parse 30 篇文章時，要如何快速的 scale up 整個 parsing process？
目前的做法是在當前的page把所有新聞抓下來後，再前往next page抓新聞，直到滿足所需的文章數。其實，可以事先準備一個網址列表，把不同page的網址存起來。接著，使用asyncio等函式庫實現平行處理，進而同時從多個page抓取新聞，並一次性進行回傳。如此一來，便無需等到當前page處理完，才能處理next page的新聞抓取。

#### 2. 當我們的 DB 當中有上千萬上億筆 documents 時，要如何更近一步提升 vector database 的搜索效率？
目前的document embeddings為768維，可以考慮使用PCA等演算法將其轉換為較低維度的representation，再來建立KD-Tree，從而減少搜索時的計算量，進而提升搜索效率。
