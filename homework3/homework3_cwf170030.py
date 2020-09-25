import pathlib
import nltk
import re

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *


def main():
    """
    Run the main items: 
    1. Read in Moby Dick
    2. Process the text 
    3. Tokenize the text and print the number of tokens. Save the list of tokens for step 11.
    4. Create a set of unique tokens and print the number of unique tokens.
    5. Create a list of important words by removing stop words from the unique tokens list. Display the number of important words
    6. Using the list of important words, create a list of tuples of the word and stemmed word
    7. Create a dictionary where the key is the stem, and the value is a list of words with that stem
    8. Print the number of dictionary entries
    9. For the 25 dictionary entries with the longest lists, print the stem and its list
    10. Using the dict from step 9, call a function to compute edit distance
    11.	Perform POS tagging on the original text after step 3
    12.	Create a dictionary of POS counts where the key is the POS, and the value is the number of words with that POS. Print the dictionary.
    """
    # 1. Read in Moby Dick
    # Take the file and store as raw text in text_in
    input_file_path = 'moby_dick.txt'
    with open(pathlib.Path.cwd().joinpath(input_file_path), 'r') as f:
        text_in = f.read()
        print('Input file: ', input_file_path)

    # 2. Process the text
    text = re.sub(r'--', ' ', text_in)
    text = re.sub('[0-9]', '', text)
    processed_text = re.sub(
        r'[.?!,:;()#@$&%^&*+_=-`\'\-\n\d]', ' ', text.lower())

    # 3. Tokenize the text and print the number of tokens. Save the list of tokens for step 11.
    tokens = word_tokenize(processed_text)
    print('Number of tokens:', f"{len(tokens):,d}")

    # 4. Create a set of unique tokens and print the number of unique tokens.
    unique_tokens = set(tokens)
    print('Number of tokens:', f"{len(unique_tokens):,d}")

    # 5. Create a list of important words by removing stop words from the unique tokens list. Display the number of important words
    stop_words = set(stopwords.words('english'))
    important_words = [w for w in unique_tokens if (w not in stop_words)]
    print('Number of important words:', f"{len(important_words):,d}")

    # 6. Using the list of important words, create a list of tuples of the word and stemmed word
    stemmer = PorterStemmer()
    stemmed = [(iw, stemmer.stem(iw)) for iw in important_words]

    # 7. Create a dictionary where the key is the stem, and the value is a list of words with that stem
    stem_dict = {}
    for s in stemmed:
        if s[1] not in stem_dict:
            stem_dict[s[1]] = [(s[0])]
        else:  # if it is in the dict
            stem_dict[s[1]].append((s[0]))

    # 8. Print the number of dictionary entries
    print('Number of dictionary entries', f"{len(stem_dict):,d}")

    # 9. For the 25 dictionary entries with the longest lists, print the stem and its list
    for k in sorted(stem_dict, key=lambda k: len(stem_dict[k]), reverse=True)[:25]:
        print(k, "->", re.sub(r'[\[\]\']', '', str(stem_dict[k])))

    # 10. Using the dict from step 9, call a function to compute edit distance
    edit_distance(stem_dict)

    # 11. Perform POS tagging on the original text after step 3
    tags = nltk.pos_tag(tokens)
    # print(tags)

    # 12. Create a dictionary of POS counts where the key is the POS, and the value is the number of words with that POS. Print the dictionary.
    tag_dict = {}
    for tag in tags:
        if tag[1] not in tag_dict:
            tag_dict[tag[1]] = [(tag[0])]
        else:  # if it is in the dict
            tag_dict[tag[1]].append((tag[0]))

    for k in sorted(tag_dict, key=lambda k: len(tag_dict[k]), reverse=True):
        print(k, len(tag_dict[k]))


def edit_distance(dictionary):
    """ 
    Takes dict and computes the edit distance betweewn 
    'continue’ and every word in the 'continu' list in the stem dict
    prints the Levenshtein Distance
    """
    for w in dictionary['continu']:
        print("Edit distance continue and", w, " = ",
              LevenshteinDistance('continue', w))

    #print(LevenshteinDistance('geek', 'gesek'))


def LevenshteinDistance(word1, word2):
    # make a 2d matrix full of 0, the size of len of the words:
    rows = len(word1)+1
    cols = len(word2)+1
    d = [[0 for x in range(cols)] for x in range(rows)]

    # vertical axis
    for i in range(1, rows):
        d[i][0] = i

    # horizontal axis
    for j in range(1, cols):
        d[0][j] = j

    # for every char, if they're the same then no cost.
    # if they are different, take the minimum cost to make them the same.
    # iterate for all the everything
    for col in range(1, cols):
        for row in range(1, rows):
            if word1[row-1] == word2[col-1]:
                cost = 0
            else:
                cost = 1
            d[row][col] = min(d[row-1][col] + 1, d[row][col-1] + 1,
                              d[row-1][col-1] + cost)  # substitution

    # Uncomment the following 2 lines to see the array
    # for row in d:
    #     print(row)

    # returns the Levenshtein Distance ie bottom right most part of array
    return(d[rows-1][cols-1])


if __name__ == "__main__":
    main()
