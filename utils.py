import numpy as np
import argparse
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import asyncio

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-sentence", type=str, default='', help='Query sentence')
    parser.add_argument("--limit", type=int, default=3, help='The maximum number of similar documents to return')
    parser.add_argument("--num_articles", type=int, default=30, help='Number of passages to be extracted from ITHome')
    
    args = parser.parse_args()
    return args    

async def fetch_content(loop, url):
    response = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(response.text, 'lxml')
    content = soup.select('div.field-name-body p')
    filtered_paragraphs = [p.get_text(strip=True) for p in content]
    return ' '.join(filtered_paragraphs[:1000])  # Max length of documents allowed

async def main(loop, urls):
    tasks = [fetch_content(loop, url) for url in tqdm(urls)]
    return await asyncio.gather(*tasks)

def scrape_ithome_news(num_articles=30): # function to scrap news from ITHome
    url = "https://www.ithome.com.tw/news"
    response = requests.get(url)
    article_dict = {'Title': [], 'Url': [], 'Content': []}
    
    print('Start scraping news from ITHome...')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Process highlight article independently
        highlight_a_tag = soup.find('div', class_='title').a
        highlight_url = url + '/' + highlight_a_tag['href'].split('/')[-1]
        article_dict['Url'].append(highlight_url)
        highlight_text = highlight_a_tag.text
        article_dict['Title'].append(highlight_text)

        page_index = 1
        first = True
        
        while(len(article_dict['Title']) < num_articles):    
            current_num_articles = len(article_dict['Title'])
            
            # turn to next page if number of articles hasn't meet requirements (default: 30)
            if not first:      
                print(f'Turning to next page! Scraping progress bar: {current_num_articles}/{num_articles}')   
                new_url = "https://www.ithome.com.tw/news?page={}".format(str(page_index))
                response = requests.get(new_url)
                soup = BeautifulSoup(response.text, 'html.parser')                
                page_index += 1
            
            current_page_items = soup.find_all('p', class_='title')
                
            for item in current_page_items:
                a_tag = item.a
                
                # get link and title of specific article
                if (a_tag['href'].split('/')[1] == 'news') and (len(article_dict['Title']) < num_articles):                
                    item_url = url + '/' + a_tag['href'].split('/')[-1]
                    article_dict['Url'].append(item_url)
                    item_text = a_tag.text
                    article_dict['Title'].append(item_text)
        
                else: 
                    pass
            
            first = False

        current_num_articles = len(article_dict['Title'])
        print(f'Finish scraping news from ITHome! Scraping progress bar: {current_num_articles}/{num_articles}')
        
        print('Start extracting news content!')
        
        # Speeding up the process of extracting article content from specific webpage
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(main(loop, article_dict['Url']))
        article_dict['Content'] = result
        print('Finish extracting news content!')

    else:
        print("Failed to retrieve data from ITHome.")
        return []

    return article_dict

 
