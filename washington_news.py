# -*- coding: utf-8 -*-
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

# washington_news
title_list = []
date_list = []
href_list = []
text_list = []
token_list = []
type_list = []
News_table = pd.DataFrame({'Title': title_list, 'Date': date_list, 'Category': type_list, 
                           'Content': text_list, 'Token': token_list ,'Href_link': href_list,
                           'Create_Date': [], 'Source': []})

res = requests.get('https://www.washingtonpost.com/')
if res.status_code == 200:
    content = res.content
    soup = BeautifulSoup(content, "html.parser")
    # html
    items = soup.findAll("div", {"class": "chain-content equalize-heights no-skin clear"})
    for item in items:
        for row in item.findAll("div", {"class": "row"}):
            category_tags = row.findAll("div", {"class": "label label-normal label-primary"})
            for category in category_tags:
                if category != "":
                    # News type
                    if category.text in ['Politics', 'World', 'National', 'PostEverything', 
                                         'Technology', 'Business & Real Estate', 'Obituaries']:
                        title_tags = row.findAll("a", {"data-pb-field": "headlines.basic"})
                        print(title_tags)
                        for tag in title_tags:
                            title_list.append(tag.text)
                            href_list.append(tag.get('href'))
                            type_list.append(category.text)
                            
                            
News_table['Title'] = title_list
News_table['Category'] = type_list
News_table['Href_link'] = href_list
News_table['Source'] = ['Washington Post'] * len(title_list)
News_table['Create_Date'] = [time.strftime("%Y-%m-%d", time.localtime())] * len(title_list)

# paper content
for link in News_table['Href_link']:
    res2 = requests.get(link)
    if res2.status_code == 200:
        content = res2.content
        soup = BeautifulSoup(content, "html.parser")
        # html
        date_items = soup.findAll("div", {"class": "display-date"})
        date_items_2 = soup.findAll("span", {"class": "author-timestamp"})
        date_items_3 = soup.findAll("div", {"class": "date"})
        if date_items != []:
            for d_item in date_items:
                date_list.append(d_item.text)
        elif date_items_2 != []:
            for d_item in date_items_2:
                date_list.append(d_item.text)
        else:
            for d_item in date_items_3:
                date_list.append(d_item.get('content'))
            
        items = soup.findAll("div", {"class": "article-body"})
        for item in items:
            s = ""
            phases = item.findAll("p")
            for phase in phases:
                if phase is not None:
                    s += str(phase.text)
    text_list.append(s)
    
if len(date_list) != len(title_list):
    date_list = [time.strftime("%Y-%m-%d", time.localtime())] * len(title_list)
    
News_table['Date'] = date_list
News_table['Content'] = text_list
token_list = [''] * len(title_list)

lemma = WordNetLemmatizer()
for i in range(0, len(text_list)):
    # transform lower letters
    text = News_table['Title'][i].lower() + " " + News_table['Content'][i].lower()
    # Delete blank and symbol
    text = re.sub("\\(|\\)|\\{.*?}|\\[.*?]|\\+|\\—|\\*|\\?|\\""|\\\\|\\/|\\≦|\\.|\\△|\\=|\\:|\\~|\\,|\\;|\\%|\\°|\\≧|\\−|\\′|\\·|\\'", " ", text)
    new_text = filter(lambda ch: ch not in '\r\n\t1234567890', text)
    text = ''.join(list(new_text))
     # tokenize
    tokens = word_tokenize(text, language='english')
    # set stopword list
    stopWords = set(stopwords.words('english'))
    for w in tokens:
        # lemmatize
        w = lemma.lemmatize(w)
        # Delete stopword
        if w not in stopWords:
            token_list[i] += str(w) + ' '

News_table['Token'] = token_list
News_table.to_csv('News.csv', index = False)
