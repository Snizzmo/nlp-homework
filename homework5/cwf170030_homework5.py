# Seed website: https://en.wikipedia.org/wiki/Fencing

import urllib
from urllib import request
from bs4 import BeautifulSoup
import re
from nltk.tokenize import sent_tokenize
import math
from nltk import sent_tokenize, word_tokenize, PorterStemmer, FreqDist
from nltk.corpus import stopwords  

def main():
    """
    calls all other functions: 
    1. Web crawler starting with URL and outputting 15+ relavent URLs
    2. A function to loop through the URLs from step 1 and scrape all text, then store into a file
    3. A function to clean the text (remore newlines, lowercase, etc) and extracts sentences (1 per line) to new file
    4. Function to extract 25+ important terms from the pages using term frequency or tf-idf 
    5. Manual determination of top 10 terms
    6. Build a searchable knowledge base of facts the chatbot can share, related to the 10 terms
    """
    topic = "Fencing"
    seed_url = "https://en.wikipedia.org/wiki/"+topic
    seed_queue = find_urls(seed_url, topic)
    #print(seed_queue)
    url_text_docs = web_crawler(seed_queue)
    text_cleaner(url_text_docs)
    most_important_terms(url_text_docs)

# 1
def find_urls(url, topic):
    """
    Web crawler starting with URL and outputting 15+ relavent URLs
    Should be mostly within the original domain 
    """
    # extract hyperlinks from an online article with Beautiful Soup
    html = request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, "html.parser")

    # get rid of all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # extract relevant hyperlinks from the page.
    web_queue = []
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
                and '.pdf' not in link_str and link_str not in  web_queue:
                web_queue.append(link_str)
            
    for link in web_queue: 
        print(link)
    print(len(web_queue))

    return(web_queue)    

# 2
def web_crawler(initial_queue):
    url_text_docs = []
    for url in initial_queue:
        with open('url' + str(initial_queue.index(url)+1) + '.txt', 'w', encoding="utf-8") as f:
            try: html = request.urlopen(url).read().decode('latin1')
            except urllib.error.URLError as e:
                print(str(e.reason))
                f.write(str(e.reason) + '\n')    
            soup = BeautifulSoup(html, "html.parser")

            #The following gets the text from the urls
            data = soup.findAll(text=True)
            result = filter(visible, data)
            temp_list = list(result)      # list from filter
            temp_str = ' '.join(temp_list)
            #temp_str = re.sub(r'\W+', ' ', temp_str)
            f.write(temp_str)
            url_text_docs.append('url' + str(initial_queue.index(url)+1) + '.txt')
            # uncomment following to store the links from each page onto their own text doc
            # """
            # for link in soup.find_all('a'):
            #     link_str = str(link.get('href'))
            #     #print(link_str)
            #     if 'Fencing' in link_str or 'fencing' in link_str:
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


# helper function for 3 to determine if an element is visible
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

# 3
def text_cleaner(url_text_docs): 
    for url in url_text_docs: 
        with open(url, 'r', encoding="utf-8") as f:
            text = f.read()
            text = re.sub(r'[\n\t]*','', text)
            while '  ' in text:
                text = text.replace('  ', ' ')
            #print(text)
            sents = sent_tokenize(text)
            with open('clean_'+url, 'w', encoding="utf-8") as w: 
                for sent in sents:
                    w.write(sent)

# 4
def most_important_terms(url_text_docs):
    i=0
    for url in url_text_docs:
        url_text_docs[i] = "clean_"+url
        i+= 1

    #make it all one doc because it's easier imo
    text=""
    for url in url_text_docs:
        with open(url, 'r', encoding="utf-8") as f:
            text += (f.read()+'\n')

    # tokenize, remove stop words, punctuation
    text = re.sub(r'[.?!,:;()\-\n\d]',' ', text.lower())
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english')) 
    reduced_tokens = [w for w in tokens if (w not in stop_words and len(w) > 5 and w.isalpha())]
    # simple term frequency
    fdist = FreqDist(reduced_tokens)
    print(fdist.most_common(50))
    
    """
    # a) Sentence Tokenize
    sentences = sent_tokenize(text)
    total_documents = len(sentences) #here, our document is all webpage text together

    # b) Create the Frequency matrix of the words in each sentence.
    freq_matrix = create_frequency_matrix(sentences) #Term frequency (TF) is how often a word appears in a document, divided by how many words are there in a document.
    #print(freq_matrix)

    # c) Calculate Term Frequency and generate a matrix
    tf_matrix = create_tf_matrix(freq_matrix)
    #print(tf_matrix)

    #  d) Creating table for documents per words
    count_doc_per_words = create_documents_per_words(freq_matrix)
    #print(count_doc_per_words)

    # e) Calculate IDF and generate a matrix
    idf_matrix = create_idf_matrix(freq_matrix, count_doc_per_words, total_documents)
    #print(idf_matrix)

    # 6 Calculate TF-IDF and generate a matrix
    tf_idf_matrix = create_tf_idf_matrix(tf_matrix, idf_matrix)
    #print(tf_idf_matrix)

    # 7 Important Algorithm: score the sentences
    sentence_scores = score_sentences(tf_idf_matrix)
    #print(sentence_scores)

    # 8 Find the threshold
    threshold = find_average_score(sentence_scores)
    #print(threshold)

    # 9 Important Algorithm: Generate the summary
    summary = generate_summary(sentences, sentence_scores, 1.5 * threshold)
    print(summary)

# helper funtion for 4 to find the frequency of words in each sentence.
def create_frequency_matrix(sentences):
    frequency_matrix = {}
    stopWords = set(stopwords.words("english"))
    ps = PorterStemmer()

    for sent in sentences:
        freq_table = {}
        words = word_tokenize(sent)
        for word in words:
            word = word.lower()
            word = ps.stem(word)
            if word in stopWords:
                continue

            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1

        # frequency_matrix[sent[:15]] = freq_table
        frequency_matrix[sent[:15]] = freq_table

    return frequency_matrix

# helper funtion for 4 to find the term frequency and generate matrix
def create_tf_matrix(freq_matrix):
    tf_matrix = {}

    for sent, f_table in freq_matrix.items():
        tf_table = {}

        count_words_in_sentence = len(f_table)
        for word, count in f_table.items():
            tf_table[word] = count / count_words_in_sentence

        tf_matrix[sent] = tf_table

    return tf_matrix

# helper function for 4 to find how many sentences contain a word (documents per words) 
def create_documents_per_words(freq_matrix):
    word_per_doc_table = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in word_per_doc_table:
                word_per_doc_table[word] += 1
            else:
                word_per_doc_table[word] = 1

    return word_per_doc_table

# helper function for 4 to find the Inverse document frequency (IDF) for each word in a paragraph
def create_idf_matrix(freq_matrix, count_doc_per_words, total_documents):
    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}

        for word in f_table.keys():
            idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

        idf_matrix[sent] = idf_table

    return idf_matrix

# helper function for 4 to find the tf*idf (TF*IDF algorithm is made of 2 algorithms multiplied together)
def create_tf_idf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}

    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):

        tf_idf_table = {}

        for (word1, value1), (word2, value2) in zip(f_table1.items(),
                                                    f_table2.items()):  # here, keys are the same in both the table
            tf_idf_table[word1] = float(value1 * value2)

        tf_idf_matrix[sent1] = tf_idf_table

    return tf_idf_matrix

def score_sentences(tf_idf_matrix) -> dict:
    # 
    # score a sentence by its word's TF
    # Basic algorithm: adding the TF frequency of every non-stop word in a sentence divided by total no of words in a sentence.
    # :rtype: dict
    # 

    sentenceValue = {}

    for sent, f_table in tf_idf_matrix.items():
        total_score_per_sentence = 0

        count_words_in_sentence = len(f_table)
        for word, score in f_table.items():
            total_score_per_sentence += score

        sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence

    return sentenceValue

def find_average_score(sentenceValue) -> int:
    # 
    # Find the average score from the sentence value dictionary
    # :rtype: int
    # 
    sumValues = 0
    for entry in sentenceValue:
        sumValues += sentenceValue[entry]

    # Average value of a sentence from original summary_text
    average = (sumValues / len(sentenceValue))

    return average

def generate_summary(sentences, sentenceValue, threshold):
    sentence_count = 0
    summary = ''

    for sentence in sentences:
        if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= (threshold):
            summary += " " + sentence
            sentence_count += 1

    return summary

    """

if __name__ == "__main__":
    main()