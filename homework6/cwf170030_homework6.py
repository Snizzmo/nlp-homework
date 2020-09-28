import pathlib
import nltk
import re
from nltk import word_tokenize
from nltk.util import ngrams
import pickle

def main():
    """
    simple main function to run the unigram/bigram program 3 times and pickle the 3 dictionaries
    """
    print('no')
    """
    english_unigram_dict, english_bigram_dict = unigram_bigram_dicts("LangId.train.English")
    french_unigram_dict, french_bigram_dict = unigram_bigram_dicts("LangId.train.French")
    italian_unigram_dict, italian_bigram_dict = unigram_bigram_dicts("LangId.train.Italian")

    # pickle the 6 dictionaries (I'm not going to be clever, this is ugly code)
    pickle.dump(english_unigram_dict, open('english_unigram_dict.pickle', 'wb'))
    pickle.dump(english_bigram_dict, open('english_bigram_dict.pickle', 'wb'))
    pickle.dump(french_unigram_dict, open('french_unigram_dict.pickle', 'wb'))
    pickle.dump(french_bigram_dict, open('french_bigram_dict.pickle', 'wb'))
    pickle.dump(italian_unigram_dict, open('italian_unigram_dict.pickle', 'wb'))
    pickle.dump(italian_bigram_dict, open('italian_bigram_dict.pickle', 'wb'))
"""
    

def unigram_bigram_dicts(file_name):
    """
    This function takes the argument filename, removes newlines, tokenizes, and 
    makes 2 dictionaries: one for unigrams and one for bigrams, storing the count of 
    the given unigram/bigram. 
    """
    # read in the text
    with open(pathlib.Path.cwd().joinpath(file_name), 'r', encoding='utf-8') as f:
        text_in = f.read()
        print('Input file: ', file_name)

    # remove newlines
    processed_text = re.sub(r'[\n]','', text_in)

    # tokenize the text 
    tokens = word_tokenize(processed_text) # This is actually superfluous but program 1 part c requires it

    # use nltk to create a list of unigrams and a list of bigrams
    unigrams = word_tokenize(processed_text)
    bigrams = list(ngrams(unigrams, 2))

    # use the bigram list to create a bigram dictionary of bigrams and counts
    # [‘token1 token2’] -> count
    bigram_dict = {b:bigrams.count(b) for b in set(bigrams)}

    # use the unigram list to create a unigram dictionary of unigrams and counts, [‘token’] -> count
    unigram_dict = {t:unigrams.count(t) for t in set(unigrams)}

    return(unigram_dict, bigram_dict)

if __name__ == "__main__":
    main()
