# -*- coding: utf-8 -*-
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
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

res = requests.get('https://www.cnbc.com/?region=usa')
if res.status_code == 200:
    content = res.content
    soup = BeautifulSoup(content, "html.parser")
    # 爬蟲 html分解
    items = soup.findAll("div", {"class": "PageBuilder-pageRow PageBuilder-containerFluidWidths"})
    for item in items:
        category_blocks = item.findAll("div", {"class": "PageBuilder-col-9 PageBuilder-col"})
        for category_tags in category_blocks:
            if category_tags != "":
                category = category_tags.findAll("a", {"class": "LazyLoaderPlaceholder-moduleTitle"})
                for c_tag in category:
                    title_tags = item.findAll("a", {"class": "LazyLoaderPlaceholder-headline"})
                    for i, t_tag in enumerate(title_tags):
                        if i <=5: # 會超出首頁新聞範圍，需限制
                            type_list.append(c_tag.text)
                            title_list.append(t_tag.text)
                            href_list.append(t_tag.get('href'))
                            # 網頁未提供時間，故直接抓取當天時間
                            date_list.append(time.strftime("%Y-%m-%d", time.localtime()))
                        else:
                            break
                    
News_table['Title'] = title_list
News_table['Date'] = date_list
News_table['Category'] = type_list
News_table['Href_link'] = href_list
News_table['Source'] = ['CNBC'] * len(title_list)
News_table['Create_Date'] = [time.strftime("%Y-%m-%d", time.localtime())] * len(title_list)

# 抓文章內容
for i, link in enumerate(News_table['Href_link']):
    # 新聞類型
    if News_table['Category'][i] in ['Tech', 'Business News', 'Personal Finance', 
                                     'Investing', 'Politics']:
        res2 = requests.get(link)
        if res2.status_code == 200:
            content = res2.content
            soup = BeautifulSoup(content, "html.parser")

            # 爬蟲 html分解
            items = soup.findAll("div", {"class": "ArticleBody-articleBody"})
            for item in items:
                s = ""
                phases = item.findAll("p")
                for phase in phases:
                    if phase is not None:
                        if phase.get("class") is None:
                            s += str(phase.text)
            text_list.append(s)
    else:
        News_table = News_table.drop([i])
                                      
News_table['Content'] = text_list
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
