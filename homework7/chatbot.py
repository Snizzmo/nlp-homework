# for main bot
import nltk
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords # also used in text summary
import requests as rq
import re
import pickle
import random
# for live webscraping
import urllib
from urllib import request
from bs4 import BeautifulSoup, Comment
# for text summary
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

def main():
    #SETUP
    users = load_users()
    #print(users)
    current_user=""

    #Intro dialogue 
    while True: 
        user_input = input('I am JertBot, a Lord of the rings info bot. What is your name? ')
        #Word tokenize, parse out the name (look for NNP) and store in users dict 
        text = re.sub(r'[.?!,:;()\-\n\d]',' ', user_input.lower()) 
        tokens = word_tokenize(text)
        tokens = [token.capitalize() for token in tokens]
        #POS tag
        tags = nltk.pos_tag(tokens)
        reduced_tags = [t for t in tags if t[1] == 'NNP']
        try: 
            for t in reduced_tags: 
                current_user += t[0]
            break
        except: 
            print("That doesn't look like a name.")

    #add user to the user base (dictionary)
    if current_user not in users:
        users[current_user] = []
        print("Good to meet you " + current_user + ". I know a lot about Lord of the Rings (but not J.R.R.Tolkien himself, yet).")
        print("You can tell me goodbye at any time and I will quit.")
    else: #or remember that they have been here before
        print("Good to see you again " + current_user + ". I know a lot about Lord of the Rings (but not J.R.R.Tolkien himself, yet).")
        print("Remember, you can tell me goodbye at any time and I will quit.")
    
    # Continue the conversation
    print("(Note: Right now I am only good at who and what questions. You can also try to just say the name of what you want to know about.)")
    user_input = input("What do you want to know about? ")

    #print(users)
    chat(users, current_user, user_input)

    print("Goodbye.")    

    #userStringParser(user_input)

def chat(users, user, user_input): 
    """
    Brains of the chatbot
    This parses out meaningful nouns using POS tagging 
    It then live-webscrapes to get the first paragraph from an LOTR wiki and prints results
    """
    while user_input.lower() not in ['bye', 'goodbye', 'see ya'] and user_input: 
        stop_words = stopwords.words('english')
        first_person_pronouns = ['I', 'we', 'me', 'us', 'my', 'mine', 'our', 'ours']
        #for w in first_person_pronouns: 
        stop_words.extend(first_person_pronouns) 
        sw = set(stop_words)
        tokens = [token.capitalize() for token in word_tokenize(user_input)]
        tags = [w for w in nltk.pos_tag(tokens) if (w[0].lower() not in sw)]
        url = ""
        words= ([(w[0]) for w in tags if w[1] == "NNP" or w[1] == "NN"])
        url = '_'.join(words)

        #Tries the webpage
        html_success = True
        try: html = request.urlopen('https://lotr.fandom.com/wiki/'+url).read().decode('latin1')
        except urllib.error.URLError as e:
            print(str(e.reason), 'Try typing it again.') #Prints if the webpage has error
            html_success = False
        
        # If the webpage exists without error, get the info
        if html_success:
            if url in users[user]: 
                print(random.choice(["You asked about "+url+' earlier. Here it is again.', url+' again, eh?', "Here's the info about "+url+" again."]))
            else: 
                users[user].append(url)
            
            print(getInfo('https://lotr.fandom.com/wiki/'+url))
            
            # summarize(nltk.sent_tokenize(getInfo('https://lotr.fandom.com/wiki/'+url, False)))
            
            save_users(users) #Remember the topics already asked about!

        user_input = input("What do you want to know about? ")


def load_users():
    """Simple function to unpickle the user database"""
    try: 
        users = pickle.load(open('users.pickle', 'rb'))
    except: 
        users = {}
        users['default'] = 'default'
    return(users)

def save_users(users):
    """simple function to pickle the userbase"""
    pickle.dump(users, open('users.pickle', 'wb'))


def getInfo(wikiUrl, first_paragraph=True):
    """
    This is the knowledge base. We use get requests using API to get information, quotes, etc. 
    Uses live webscraping 
    """
    
    if wikiUrl:
        try: html = request.urlopen(wikiUrl).read().decode('latin1')
        except urllib.error.URLError as e:
            print(str(e.reason)) #THIS SHOULD NEVER OUTPUT THANKS TO THE ERROR CHECKING BEFORE CALLING getInfo
        soup = BeautifulSoup(html, "html.parser")      

        #Get rid of all the fluff 
        [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'header', 'title', 'wds-global-navigation-wrapper'])] #'wds-global-navigation-wrapper', 'wds-global-navigation__content-bar-left'])
        if soup.find('div', class_='wds-global-navigation-wrapper'):
            soup.find('div', class_='wds-global-navigation-wrapper').decompose()
        if soup.find('div', class_='mw-references-wrap'):
            soup.find('div', class_='mw-references-wrap').decompose()
        if soup.find('table', class_='bg-Shade'):
            soup.find('table', class_='bg-Shade').decompose()
        if soup.find('table'): 
            soup.find('table').decompose()
        if soup.find('table', class_='itemtable'): 
            soup.find('table', class_='itemtable').decompose() 
        if soup.find('nav', class_='article-categories CategorySelect articlePage'): 
            soup.find('nav', class_='article-categories CategorySelect articlePage').decompose()
        if soup.find('nav', class_="WikiaArticleInterlang"):
            soup.find('nav', class_="WikiaArticleInterlang").decompose()
        if soup.find('footer'): 
            soup.find('footer').decompose()
        if soup.find('div', class_='printfooter'): 
            soup.find('div', class_='printfooter').decompose()
        if soup.find('div', class_='license-description'): 
            soup.find('div', class_='license-description').decompose()
        if soup.find('div', class_='boilerplate'): 
            soup.find('div', class_='boilerplate').decompose()
        if soup.find('aside'): 
            soup.find('aside').decompose()
        if soup.find('table', class_="collapsible collapsed navbox"): 
            soup.find('table', class_="collapsible collapsed navbox").decompose()
        if soup.find('dl'):
            soup.find('dl').decompose()

        # get only the first paragraph from the wiki
        data = soup.findAll(text=True) 
        result = filter(visible, data)
        temp_list = list(result)      # list from filter
        temp_str = ''.join(temp_list)
        if (first_paragraph):
            short_str = str(temp_str.split("Contents")[0])        
            clean_text = text_cleaner(short_str)
        else: 
            clean_text = text_cleaner(temp_str)
        
        return(clean_text)

# A function to clean the text (remore newlines, etc) and extracts sentences to a string split by spaces. 
def text_cleaner(text): 
    text.replace('\n', ' ').replace('\t', ' ')
    while '  ' in text:
        text = text.replace('  ', ' ')
    sents = sent_tokenize(text)

    pattern = r'\[\d+\]'
    for sent in sents: 
        re.sub(pattern, '', sent)
        #re.sub(pattern, '', sent)
        if sent[0] == ' ':
            sent = sent[1:]

    sents_str = ' '.join(sents)
    return(sents_str)

# helper function for summarize to determine if an element is visible
def visible(element):
    if 'toc' in element.parent.name: 
        False 
    if element.parent.name in ['style', 'script', '[document]', 'head', 'header', 'title']: # 'navigation' ,'personal'
        #print(element.parent.name, " has ", element)
        #print("ELEMENT")
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        #print("COMMENT")
        return False
    elif element.parent.name != 'a' and element.parent.name != 'p' and element.parent.name != 'b' and element.parent.name != 'h2': 
        #print(element.parent.name)
        return False
    return True

# text summary
def summarize(sentences, top_n=2):
    stop_words = stopwords.words('english')
    summarize_text = []

    # similarity matrix
    similarity_martix = make_similarity_matrix(sentences, stop_words)

    # rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    #print("Indexes of top ranked_sentence order are ", ranked_sentence)

    for i in range(top_n):
      summarize_text.append("".join(ranked_sentence[i][1]))
    
    # Step 5 - Offcourse, output the summarize texr
    print("\n\nSummarize Text: \n", "\n".join(summarize_text))

    #print(sentences)
    print('end')
    
def make_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
    
    return 1 - cosine_distance(vector1, vector2)


if __name__ == "__main__":
    main()