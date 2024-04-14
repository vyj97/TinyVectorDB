# TinyVectorDB
A simple search engine for ITHome news.


## TL;DR quickstart

To setup a conda environment and install related dependencies.
```
conda create --name bce python=3.10 -y
conda activate bce
python -m pip install -r requirements.txt
```

## Some Huggingface user guide to use bce-embedding-base model

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
 ```

#### Case 2: Provide query sentence using keyboard input after executing the program (allowing multiple query inputs)
 ```
 python3 search.py --limit [LIMIT NUM OF DOCS RETURNED] --num_articles [NUM OF DOCS PARSED FROM ITHOME]
 ```

## Extra notes
#### 當我們的使用情境不止需要 parse 30 篇文章時，要如何快速的 scale up 整個 parsing process？

#### 當我們的 DB 當中有上千萬上億筆 documents 時，要如何更近一步提升 vector database 的搜索效率？
