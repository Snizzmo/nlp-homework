import sys
import pathlib
import nltk
import re

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from random import seed
from random import randint
seed(1234)

def main():
    """
    Run the main items: 
    1. Take in user input and store as raw text
    2. Tokenize text and call lexical diversity function
    3. Call funtion to preproccess text 
    4. Make a dictionary of the nouns and the count
    5. Call a guessing game function
    """
    if len(sys.argv) < 2: # Make sure to input the file path/name! 
        print("User must define a file path. Exiting program.")
        quit()

    input_file_path = sys.argv[1] # Take the file and store as raw text in text_in
    with open(pathlib.Path.cwd().joinpath(input_file_path), 'r') as f:
        text_in = f.read()
        print('Input file: ', input_file_path)
    
    # Calculate the lexical diversity of the tokenized text and output it, formatted to 2 decimal places. 
    lexical_diversity(text_in) # Call the function to calculate and output
    
    # Call funtion to preproccess text 
    tokens, nouns = preprocess(text_in)

    # Make a dictionary of the nouns and the count
    noun_count_dict = {}
    for n in nouns: 
        count = 0
        for t in tokens: 
            if n == t: 
                count += 1
        noun_count_dict[n] = count
    noun_count_dict = sorted(noun_count_dict.items(), key=lambda x: x[1], reverse=True)
    top_50_nouns = noun_count_dict[:50]
    for n in top_50_nouns:
        print(n)

    # Call guessing game function
    guessing_game(top_50_nouns)



def lexical_diversity(text):
    """tokenize, then divide unique word tokens over total word tokens to get lexical diversity"""
    tokens = word_tokenize(text)
    lex_diversity = (len(set(tokens))/len(tokens))
    print(f'Lexical diversity is {lex_diversity:.2f}')



def preprocess(raw_text):
    """ modified from github
        Preprocess raw tex.
        Arguments: a raw text string
        Outputs are lowercase:
            tokens - all tokens
            nouns - all unique nouns
    """
    # remove punctuation and numbers with a regular expression
    text = re.sub(r'[.?!,:;()\-\n\d]',' ', raw_text.lower())

    # tokenizing extracts words, not white space
    tokens = word_tokenize(text)

    # reduce the tokens to only those that are alpha, not in the NLTK stopword list, and have length > 5
    stop_words = set(stopwords.words('english')) 
    reduced_tokens = [w for w in tokens if (w not in stop_words and len(w) > 5 and w.isalpha())]

    # lemmatization finds the root words, set makes it list of unique lemmas
    wnl = WordNetLemmatizer()
    lemmas = set([wnl.lemmatize(t) for t in reduced_tokens])

    # POS tag on unique lemmas and print 
    tags = nltk.pos_tag(lemmas)
    print('First 20 tagged words: ', tags[:20])

    #create list of lemmas that are nouns
    nouns = [w[0] for w in tags if w[1][0] == 'N']

    # print the number of tokens and the number of nouns
    print('Number of tokens after preprocessing:\t', len(reduced_tokens))
    print('Number of nounsafter preprocessing:\t', len(nouns))
    print()

    return (reduced_tokens, nouns)

def guessing_game(dictionary):
    """
    a.	give the user 5 points to start with; the game ends when their total score is negative, or they guess ‘!’ as a letter 
    b.	randomly choose one of the 50 words in the top 50 list (See the random numbers notebook in the Xtras folder of the GitHub) 
    c.	output to console an underscore _ for each letter in the word
    d.	ask the user for a letter
    e.	if the letter is in the word, print ‘Right!’, fill in all matching letter _ with the letter and add 1 point to their score
    f.	if the letter is not in the word, subtract 1 from their score, print ‘Sorry, guess again’ 
    g.	guessing for a word ends if the user guesses the word or has a negative score
    h.	keep a cumulative total score and end the game if it is negative (or the user entered ‘!’) for a guess
    i.	right or wrong, give user feedback on their score for this word after each guess
    """
    # Initialize: give player 5 points, choose a word randomly from dictionary, 
    target_word = dictionary[(randint(0, 49))][0]
    target_letters = list(target_word)
    print("Let's play a word guessing game!")
    score = 5
    end_game = False
    guessed = ["_" for l in target_letters]
    guess = " "
    prev_guesses = []

    while end_game is False: 
        # output to console an underscore _ for each letter in the word, or the correct letter for correct guesses
        print('Current score is ', score)
        for g in guessed: 
            print(g, end = " ")
        print()
        
        # get user input
        guess = ""
        while len(guess) != 1 or guess in prev_guesses: 
            print('Previous guesses: ', ' '.join(prev_guesses))
            guess = input("Guess a single letter you haven't guessed before: ")
            print()
        prev_guesses += guess

        # check is user entered ! to end game
        if guess == '!':
            end_game = True
            print("Ending game.")
            print()

        # if the user guessed correctly
        if guess in target_letters and not end_game: 
            print('Right!')
            positions = [i for i, letter in enumerate(target_word) if letter == guess]
            for i in positions:
                guessed[i] = guess
            score += 1
        # else, if it was wrong (checking for ! just to be safe)
        elif guess != '!':
            print('Sorry, that was wrong.')
            score -= 1

        # win check
        if guessed == target_letters: 
            print("You solved it! The target word was", target_word)
            print("Guess another word")
            target_word = dictionary[(randint(0, 49))][0]
            target_letters = list(target_word)
            guessed = ["_" for l in target_letters]
            guess = " "
            prev_guesses = []
        if score < 0: 
            print('Score went negative. You lose.')
            end_game = True
    
    
if __name__ == "__main__":
    main()
