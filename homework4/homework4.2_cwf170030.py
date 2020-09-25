import pathlib
import pickle
from nltk import word_tokenize
from nltk.util import ngrams
import math

def main():
    """
    unpickles the dictionaries, calculates the probability for each language, 
    outputs accuracy using LandId.sol, and the line numbers of the incorrectly classified items 
    """
    # unpickle with some ugly code
    english_unigram_dict = pickle.load(open('english_unigram_dict.pickle', 'rb'))
    english_bigram_dict = pickle.load(open('english_bigram_dict.pickle', 'rb'))
    french_unigram_dict = pickle.load(open('french_unigram_dict.pickle', 'rb'))
    french_bigram_dict = pickle.load(open('french_bigram_dict.pickle', 'rb'))
    italian_unigram_dict = pickle.load(open('italian_unigram_dict.pickle', 'rb'))
    italian_bigram_dict = pickle.load(open('italian_bigram_dict.pickle', 'rb'))

    # Get the answers for later
    with open("langId.sol") as answer_file:
        answers = answer_file.readlines()
    answers = [x.strip() for x in answers]

    # N is number of tokens in the training data
    N_eng = len(english_unigram_dict)
    N_fre = len(french_unigram_dict)
    N_ita = len(italian_unigram_dict)

    # V is the vocabulary size in the training data (unique tokens)
    v = N_eng + N_fre + N_ita

    # for each test file, calculate a probability for each language
    # and write the language with the highest probability to a file.
    with open("langId.test") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    
    # coutner and list for incorrect answers
    count = 0
    wrong_lines = []

    with open("output.txt", "w") as o:
        for line in content: 
            count += 1
            #get the probability for each language
            prob_english = compute_prob(line, english_unigram_dict, english_bigram_dict, v, N_eng)
            prob_french = compute_prob(line, french_unigram_dict, french_bigram_dict, v, N_fre)
            prob_italian = compute_prob(line, italian_unigram_dict, italian_bigram_dict, v, N_ita)
            
            #ugly way to show which language 
            if prob_english == max(prob_english, prob_french, prob_italian): 
                newline = (str(count) + " English") 
            elif prob_french == max(prob_english, prob_french, prob_italian): 
                newline = (str(count) + " French")
            else: # prob_italian == max(prob_english, prob_french, prob_italian) 
                newline = (str(count) + " Italian")
            
            
            #write to output file
            o.write(newline)
            o.write("\n")

            #keep track of wrong answers
            if newline != answers[count-1]: 
                wrong_lines.append(count)
    
    #output the erronious lines and percent correct
    print("percent correct:", "{:.2%}".format(1-(len(wrong_lines))/count))
    print("Errors on lines", str(wrong_lines).strip('[]'))




def compute_prob(line, unigram_dict, bigram_dict, V, N):
    """
    We will simply multiply the probabilities together.
    Each bigram’s probability with Laplace smoothing is
    (b + 1) / (u + v) where 
    b is the bigram count, 
    u is the unigram count of the first word in the bigram, and
    v is the total vocabulary size (add the lengths of the 3 unigram dictionaries)
    Other probability included for fun, but the important one is p_laplace
    """
    #print(line)
    unigrams_test = word_tokenize(line)
    bigrams_test = list(ngrams(unigrams_test, 2))

    p_gt = 1       # calculate p using a variation of Good-Turing smoothing
    p_laplace = 1  # calculate p using Laplace smoothing
    p_log = 0      # add log(p) to prevent underflow

    for bigram in bigrams_test:
        n = bigram_dict[bigram] if bigram in bigram_dict else 0
        n_gt = bigram_dict[bigram] if bigram in bigram_dict else 1/N
        d = unigram_dict[bigram[0]] if bigram[0] in unigram_dict else 0
        if d == 0:
            p_gt = p_gt * (1 / N)
        else:
            p_gt = p_gt * (n_gt / d)
        p_laplace = p_laplace * ((n + 1) / (d + V))
        p_log = p_log + math.log((n + 1) / (d + V))

    # print("\nprobability with simplified Good-Turing is %.5f" % (p_gt))
    # print("probability with laplace smoothing is %.5f" % p_laplace)
    # print("log prob is %.5f == %.5f" % (p_log, math.exp(p_log)))
    return(p_laplace)
    
if __name__ == "__main__":
    main()
