import nltk, re
from nltk import word_tokenize
from nltk.corpus import stopwords
import requests as rq

def main():
    """
    This is a chatbot that will give you info on the Lord of the Rings books, movies, etc! 

    Diagram tree of logic: 
    1. Intro from computer
    2. user says something
    3. computer tries to uinderstand
        ASR, IE, POS tagging, Syntax parsing
    4. dialog engine decides what to do 
    5. Computer response
    6. go to 2
    
    User model 
        Name
        Symptoms

    KB (live web scraping)

    include NLP that we've covered (tf-idf, ~)

    """
    users = {}
    current_user = ""

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
                current_user += t[0]+" "
            break
        except: 
            print("That doesn't look like a name.")
    
    #add user to the user base (dictionary)
    users[current_user] = current_user

    user_input = input('Good to meet you ' + current_user + ". I know a lot about Lord of the Rings. What do you want to know?")

    userStringParser(user_input)

def userStringParser(string):
    """
    here we parse user string
    get info about user
        store
    see what request they are wanting/talking about
    print that 
    """
    
    

def getInfo():
    """
    This is the knowledge base. We use get requests using API to get information, quotes, etc.  
    """
    URL = "https://the-one-api.dev/v2/movie"
    Bearer = 'Bearer PlJSuXTxCb3078hZYyk0'
    headers = {"Authorization": Bearer}

    r = rq.get(URL, headers=headers)

    print(r.text)
    
if __name__ == "__main__":
    main()