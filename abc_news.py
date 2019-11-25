# -*- coding: utf-8 -*-
import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

title_list = []
date_list = []
href_list = []
text_list = []
token_list = []
type_list = []
News_table = pd.DataFrame({'Title': title_list, 'Date': date_list, 'Category': type_list, 
                           'Content': text_list, 'Token': token_list ,'Href_link': href_list,
                           'Create_Date': [], 'Source': []})

res = requests.get('https://www.abc.net.au/news/')
if res.status_code == 200:
    content = res.content
    soup = BeautifulSoup(content, "html.parser")
    # 爬蟲 html分解
    items = soup.findAll("body")
    for item in items:
        rows = item.findAll('div', {'class', 'inline-content uberlist article'})
        for row in rows:
            #print(row)
            # 新聞類型
            if row.find('a').text in ['World', 'Asia Pacific', 'Business']:
                for link in row.findAll('a'):
                    l = link.get('href')
                    if len(l) > 20: # 被免抓到分頁標題網址
                        href_list.append('https://www.abc.net.au/' + link.get('href'))
                    
                for title in row.findAll('h3'):
                    #print(title.text.replace('\n', ''))
                    title_list.append(title.text.replace('\n', ''))
                    type_list.append(row.find('a').text)
                    
News_table['Title'] = title_list
News_table['Category'] = type_list
News_table['Href_link'] = href_list
News_table['Source'] = ['ABC News'] * len(title_list)
News_table['Create_Date'] = [time.strftime("%Y-%m-%d", time.localtime())] * len(title_list)

# 抓文章內容
for link in News_table['Href_link']:
    res2 = requests.get(link)
    if res2.status_code == 200:
        content = res2.content
        soup = BeautifulSoup(content, "html.parser")
        
        # 爬蟲 html分解
        items = soup.findAll("div", {"class": "article section"})
        for item in items:
            s = ""
            phases = item.findAll("p")
            for phase in phases:
                if phase is not None:
                    if phase.get("class") is None:
                        s += str(phase.text)
        p_items = soup.findAll("p", {"class": "published"})
        for p_item in p_items:
            if 'posted' in p_item.text.strip().lower():
                d_item = p_item.find("span", {"class": "timestamp"})
                date_list.append(d_item.text.strip())                                                    
    text_list.append(s)
    
# 有時候網頁提供之時間會有問題，若有問題時直接抓取當天時間
if len(date_list) != len(title_list):
    date_list = [time.strftime("%Y-%m-%d", time.localtime())] * len(title_list)

News_table['Content'] = text_list
News_table['Date'] = date_list
token_list = [''] * len(title_list)

lemma = WordNetLemmatizer()
for i in range(0, len(text_list)):
    #轉全小寫
    text = News_table['Title'][i].lower() + " " + News_table['Content'][i].lower()
    #刪除數字空白和標點符號
    text = re.sub("\\(|\\)|\\{.*?}|\\[.*?]|\\®|\\+|\\—|\\*|\\?|\\""|\\\\|\\/|\\≦|\\.|\\△|\\=|\\:|\\~|\\,|\\;|\\%|\\°|\\≧|\\−|\\′|\\·|\\'", " ", text)
    new_text = filter(lambda ch: ch not in '\r\n\t1234567890', text)
    text = ''.join(list(new_text))
     # 斷詞
    tokens = word_tokenize(text, language='english')
    # 停用詞列表設置
    stopWords = set(stopwords.words('english'))
    for w in tokens:
        # 字根還原
        w = lemma.lemmatize(w)
        # 刪停用詞
        if w not in stopWords:
            token_list[i] += str(w) + ' '

News_table['Token'] = token_list
News_table.to_csv('News.csv', index = False, header = False, mode='a')
