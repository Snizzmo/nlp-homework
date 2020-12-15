# Seed website: https://en.wikipedia.org/wiki/Fencing

import urllib
from urllib import request
from bs4 import BeautifulSoup, Comment
import re
from nltk.tokenize import sent_tokenize
import math
from nltk import sent_tokenize, word_tokenize, PorterStemmer, FreqDist
from nltk.corpus import stopwords  

import time
def main():
    """
    calls all other functions: 
    1. Web crawler starting with URL and outputting 15+ relavent URLs
    2. A function to loop through the URLs from step 1 and scrape all text, then store into a file per url
    3. A function to clean the text (remore newlines, lowercase, etc) and extracts sentences (1 per line) to new file
    4. Function to extract 25+ important terms from the pages using term frequency or tf-idf 
    5. Manual determination of top 10 terms
    6. Build a searchable knowledge base of facts the chatbot can share, related to the 10 terms
    """
    topic = "Mario"
    seed_url = "https://en.wikipedia.org/wiki/"+topic

    seed_url="https://lotr.fandom.com/wiki/Main_Page"

    # 1. Web crawler
    seed_queue = find_urls(seed_url, topic)
    # print(seed_queue[:4])

    # 2. Loop through the URLs, scrape all text, then store into a file per url
    url_text_docs = web_crawler(seed_queue)

    # 3. clean the text and extracts sentences 
    text_cleaner(url_text_docs)

    # 4. extract important terms from the pages using term frequency, prints top 40
    top40 = most_important_terms(url_text_docs)

    # 5. Manual selection of top 10 terms
    top10 = ['nintendo', 'bowser', 'mushroom', \
            'princess', 'characters', 'miyamoto', \
            'castle', 'goomba', 'kingdom', 'arcade']
    # top10 = ['furniture', 'business', 'products',]

    # 6. Build searchable knowledge base
    knowledge_base = build_knowledge_base(top10, url_text_docs)
    for term in top10: 
        print(knowledge_base[term][0], '\n')


# 1. Web crawler starting with URL and outputting 15+ relavent URLs
def find_urls(url, topic):
    # extract hyperlinks from an online article with Beautiful Soup
    html = request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, "html.parser")

    # get rid of all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # extract relevant hyperlinks from the page.
    web_queue = []
    web_queue.append(url)
    for link in soup.find_all('a'):
        # print(link)
        link_str = str(link.get('href'))
        #print(link_str)
        if topic in link_str or topic.lower() in link_str:
            if link_str.startswith('/url?q='):
                link_str = link_str[7:]
                #print('MOD:', link_str)
            if '&' in link_str:
                i = link_str.find('&')
                link_str = link_str[:i]
            if link_str.startswith('http') and 'google' not in link_str and 'web.archive' not in link_str \
                and '.pdf' not in link_str and 'rsc.org' not in link_str and link_str not in web_queue:
                web_queue.append(link_str)
    i = 0      
    for link in web_queue: 
        print(i, link)
        i+=1
    #print(len(web_queue))

    return(web_queue)    

# 2. A function to loop through the URLs from step 1 and scrape all text, then store into a file per url
def web_crawler(initial_queue):
    url_text_docs = []
    for url in initial_queue:
        with open('url' + str(initial_queue.index(url)) + '.txt', 'w', encoding="utf-8") as f:
            try: html = request.urlopen(url).read().decode('latin1')
            except urllib.error.URLError as e:
                print(str(e.reason))
                f.write(str(e.reason) + '\n')    
            soup = BeautifulSoup(html, "html.parser")
            
            # Get rid of comments
            comments = soup.findAll(text=lambda text:isinstance(text, Comment))
            for comment in comments:
                comment.extract()

            #The following gets the text from the urls and adds to url_text_docs
            data = soup.findAll(text=True)
            result = filter(visible, data)
            temp_list = list(result)      # list from filter
            temp_str = ' '.join(temp_list)
            f.write(temp_str)
            url_text_docs.append('url' + str(initial_queue.index(url)) + '.txt')

            # uncomment following to store the links from each page onto their own text doc
            # """
            # for link in soup.find_all('a'):
            #     link_str = str(link.get('href'))
            #     #print(link_str)
            #     if topic in link_str or topic.lower() in link_str:
            #         if link_str.startswith('/url?q='):
            #             link_str = link_str[7:]
            #             #print('MOD:', link_str)
            #         if '&' in link_str:
            #             i = link_str.find('&')
            #             link_str = link_str[:i]
            #         if link_str.startswith('http') and 'google' not in link_str:
            #             f.write(link_str + '\n')
            # """

    return url_text_docs

# helper function for 2 to determine if an element is visible
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']: # 'navigation' ,'personal'
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

# 3. A function to clean the text (remore newlines, lowercase, etc) and extracts sentences (1 per line) to new file
def text_cleaner(url_text_docs): 
    for url in url_text_docs: 
        with open(url, 'r', encoding="utf-8") as f:
            text = f.read()
            text = re.sub(r'[\n\t]*','', text)
            while '  ' in text:
                text = text.replace('  ', ' ')
            sents = sent_tokenize(text)
            with open('clean_'+url, 'w', encoding="utf-8") as w: 
                for sent in sents:
                    w.write(sent + '\n')

# 4. Function to extract 25+ important terms from the pages using term frequency or tf-idf 
def most_important_terms(url_text_docs):
    # Rename all the urls to their cleaned version
    i=0
    for url in url_text_docs:
        url_text_docs[i] = "clean_"+url
        i+= 1
    
    # return(fdist.most_common(40))
    stop_words = set(stopwords.words('english')) 
    reduced_tokens = []
    for url in url_text_docs:
        with open(url, 'r', encoding="utf-8") as f:
            text = f.read()
            # tokenize, remove stop words, punctuation
            text = re.sub(r'[.?!,:;()\-\n\d]',' ', text.lower())
            tokens = word_tokenize(text)
            reduced_tokens += [w for w in tokens if (w not in stop_words and len(w) > 5 and w.isalpha())]
    
    # simple term frequency
    fdist = FreqDist(reduced_tokens)
    print(fdist.most_common(40))
    
    return(fdist.most_common(40))

# 6. Build a searchable knowledge base of facts the chatbot can share, related to the 10 terms
def build_knowledge_base(terms, url_text_docs):
    '''
    For every term, for every sentence in every URL, if the term is in a sentence 
    then add that sentence to a list which is the value in a dictionary and the key is the term
    '''
    knowledge_base = {}
    for term in terms:
        for url in url_text_docs:
            with open(url, 'r', encoding="utf-8") as r: 
                text = r.read()
                sents = sent_tokenize(text)
                for sent in sents: 
                    if term in sent: 
                        if term not in knowledge_base: 
                            knowledge_base[term] = [(sent),]
                        else: 
                            knowledge_base[term].append(sent)

    #  print(knowledge_base)
    return knowledge_base

if __name__ == "__main__":
    main()