"""
Title: Homework 4, parts 1 and 2. Cracking a Cipher
Author: Timur Kasimov (Grinnell, 2025)
Data Created: March 31, 2024
Date Updated: April 5th, 2024

Purpose: Implement and test a cipher-cracker using Metropolis-Hastings

This is a homework assignment for my Computational Methods Class
"""


# importing necessary packages
import numpy as np
import pandas as pd
import math
import random
import string



######################################
## GLOBAL VARIABLES USED THROUGHOUT ##
######################################
# alphabet consists of all upper and lower case characters in english, plus space, comma, period chars
ALPHABET = list(string.ascii_letters) + [' ', ',', '.'] 

LENGTH = len(ALPHABET)
MAXITER = 10000 # limit each run to 10,000 iterations
MIN = math.exp(-20) # value to replace zeros in the transition matrix

# Set to TRUE if the csv file with transition matrix is already saved
# Set to FALSE if running on a new machine and need to create the transition matrix
# Note: csv file with the transition matrix must be saved in the same directory as the
# current file hw4.py
TRANSITION_MATRIX_SAVED = True

# Set to true if want to confuse the deciphering Metropolis-Hastings algorithm
# by reversing the message before enciphering it. 
CONFUSE = False



########################
### permute_alphabet ###
########################
'''
Pre-conditions:
     none
Post-conditions: 
     returns void?
Purpose: Permutes the initial alphabet/mapping in random order, 
     creating random (reverse) cipher
'''
def permute_alphabet():
     random.shuffle(mapping) # credit to stackexchange and 'random' library that includes the shuffle function


################
### swap_two ###
################
'''
Pre-conditions:
     alphabet: a list of characters with length of LENGTH (55)
Post-conditions: 
     new_mappping: a list of characters with two random characters swapped
Purpose: takes the current mapping for the reverse cipher and randomly 
     swaps two characters in it
'''
def swap_two(alphabet):
     new_mapping = alphabet.copy() # shallow copy, i believe?
     i1, i2 =  random.sample(range(LENGTH), 2) # credit to stackexchange and 'random' library with its sample 
     new_mapping[i1], new_mapping[i2] = new_mapping[i2], new_mapping[i1] # swaps two elements
     return new_mapping


############################
# create_transition_matrix #
############################
'''
Pre-conditions:
     none, but should only be run if transition matrix was not previously saved
Post-conditions: 
     none
Purpose: creates transition matrix of characters based on 
     the War and Peace text by Leo Tolstoy and saves it as 
     a csv file
     '''
def create_transition_matrix():
     # initialize a 2d array of the correct size
     trans_matrix = np.zeros((LENGTH, LENGTH))
     # print(trans_matrix)

     # read the War and Peace text
     with open('/Users/timur/CompMethods/cipher_cracker/WarAndPeace.txt', "r") as f:
          text = f.read()
          #  record the text's length
          length = len(text)

          # iterate through text's characters
          for i in range(length-1):
               
               # take two neighbouring characters
               ch1, ch2 = text[i], text[i+1]
               # if both characters are in alphabet, ...
               if (ch1 in ALPHABET and ch2 in ALPHABET):
                    # increment the number of such transitions
                    i1, i2 = ALPHABET.index(ch1), ALPHABET.index(ch2)
                    trans_matrix[i1, i2] += 1
     
     # print(trans_matrix)
     # calculate the total number of valid transitions
     sum = trans_matrix.sum()
     # print("SUM: ", sum)
     # transform absolute counts into proportions of total transitions
     trans_matrix = trans_matrix * (1/sum)

     #  replacing zeros in the matrix with very small number MIN
     for row in range(LENGTH):
          for col in range(LENGTH):
               if (trans_matrix[row, col] == 0.0):
                    trans_matrix[row, col] = MIN  
     # print(trans_matrix)

     # save transition matrix as file
     df = pd.DataFrame(data = trans_matrix)
     df.to_csv('./transition_matrix.csv', sep=',', header=False, index=False)
#  end create_transition_matrix


############################
#  read_transition_matrix  #
############################
'''
Pre-conditions:
     none
Post-conditions: 
     none
Purpose: reads previously saved as a csv file transition matrix 
     of characters based on the War and Peace text by Leo Tolstoy.
     Returns the matrix as a numpy array 
     '''              
def read_transition_matrix():
    data = pd.read_csv('./transition_matrix.csv', header=None)
    # print(data)
    matrix = np.matrix(data.iloc[0:55, 0:55])
    # print(matrix)
    return matrix


##############
#  encipher  #
##############
'''
Pre-conditions:
     string: a string of characters limited to the predefined alphabet
     cipher: a list of characters whose order defines the substitution cipher/decipher
Post-conditions: 
     message: the string of characters enciphered with the given cipher/mapping
Purpose: Enciphers the string using the given cipher
'''                 
def encipher(string, cipher):
     # convert the string to a list of chars
     my_list = list(string)
     # for each character in the message
     for i in range(len(my_list)):
          char = my_list[i]
          # find the character's index in the original alphabet
          index = ALPHABET.index(char)
          # find what this character maps to according to given cipher
          new_char = cipher[index]
          # substitute the old character with the new character
          my_list[i] = new_char
     
     # join the list of characters back into a string to return
     message = ''.join(str(x) for x in my_list)
     return message


##############
#  calc_sum  #
##############
'''
Pre-conditions:
     message: a string of characters limited to the predefined alphabet
     matrix: a matrix of character transition probabilities taken from War and Peace
Post-conditions: 
     sum: float value, the sum of logs of respective matrix entries
Purpose: calculates the sum of logged probabilities of transitions
'''
def calc_sum(message, matrix):
     length = len(message)
     # iterate through text's characters
     sum = 0.0
     for i in range(length-1):
         ch1, ch2 = message[i], message[i+1]
         #  if both characters are in alphabet, ...
         if (ch1 in ALPHABET and ch2 in ALPHABET):
             i1, i2 = ALPHABET.index(ch1), ALPHABET.index(ch2)
             sum += math.log(matrix[i1, i2])    
     return sum


#####################
#  calc_acceptance  #
#####################
'''
Pre-conditions:
     old_sum: a float value from previously accepted decipher
     new_sum: a float value from proposed decipher attempt
Post-conditions: 
     probability of acceptance: float value between 0 and 1
Purpose: calculates and returns the probability with which we should
     accept the newly proposed deciphering mapping
'''
def calc_acceptance(old_sum, new_sum):
     try:
          difference = math.exp(new_sum-old_sum)
     except:
          difference = 1
     
     return min(difference, 1)


##############
#  scramlbe  #
##############
'''
Pre-conditions:
     message: original message
Post-conditions: 
     scrambled message: ciphered message
Purpose: calculates and returns the probability with which we should
     accept the newly proposed deciphering mapping
'''
def scramble(message):
     # create a random cipher from the alphabet
     permute_alphabet()
     # encipher the message using cipher/mapping
     return encipher(message, mapping)


##################
#  insert-chars  #
##################
'''
Pre-conditions:
     message: original message
Post-conditions: 
     modified message: modified string with unlikely character transition
     insterted every 10 characters
Purpose: modifies the message before using substitution cipher on it.
     This is one of the ways to confuse the decipherers and make the
     Metropolis-Hastings deciphering algorithm fail.
'''
def insert_chars(message):
     # convert the string to a list of chars
     my_list = list(message)
     # for each character in the message
     index = 0
     length = len(my_list)
     while (index < length):
          my_list.insert(index, 'T')
          my_list.insert(index, 'q')
          index += 7
          length += 2
     
     # join the list of characters back into a string to return
     message = ''.join(str(x) for x in my_list)
     return message


##################
#  delete_chars  #
##################
'''
Pre-conditions:
     message: previously modified message using insert_chars
Post-conditions: 
     message: de-modified string equal to the original message
Purpose: de-modifies the message that was previously modified to protect
     from Metropolis attacker
'''
def delete_chars(message):
     # convert the string to a list of chars
     my_list = list(message)
     # for each character in the message
     index = 0
     length = len(my_list)
     while (index < length):
          del my_list[index:index+2]
          index += 5
          length -= 2

     # join the list of characters back into a string to return
     message = ''.join(str(x) for x in my_list)
     return message


##############
#  decipher  #
##############
'''
Pre-conditions:
     scrambled_message: ciphered message to be deciphered
     mapping: an alphabet in the form of the list of characters, 
     not necessarily in order
Post-conditions: 
     deciphered: returns deciphered message as a string
Purpose: runs a chain of MAXITER (10,000) iterations using Metropolis-
     Hastings to try and decipher the scambled message.
'''
def decipher(scrambled_message, mapping):
     # create an initial deciphering mapping
     permute_alphabet()

     # first attempt at deciphering
     deciphered_message = encipher(scrambled_message, mapping)
     # calculate sum of logs of probabilities of transitions
     old_sum = calc_sum(deciphered_message, matrix)

     # to keep track of best mapping
     best_mapping = mapping.copy()
     best_sum = old_sum

     counter = 0
     acceptances = 0

     for iter in range(MAXITER):
          # print("Best mapping and probability")   
          # print(best_mapping)
          # print(best_sum)
          # print("Current Mapping")
          # print(mapping)
          # print()

          if (iter % 2000 == 0):
               print("Iteration:", iter)
          # propose a new mapping
          new_mapping = swap_two(mapping)
 
          # decipher scrambled message using the new proposed mapping
          deciphered_message = encipher(scrambled_message, new_mapping)
          # print(deciphered_message)

          # calculate acceptance probability and accept or reject new mapping
          new_sum = calc_sum(deciphered_message, matrix)
          probability = calc_acceptance(old_sum, new_sum)

          # if random number is less than probability of acceptance
          if (random.random() < probability):
              acceptances += 1
              # accept the new mapping as the current mapping
              mapping = new_mapping
              # new sum of logs becomes old sum
              old_sum = new_sum
              # keep track of the best deciphered message so far
              if (old_sum > best_sum):
                   counter += 1
                   best_sum = old_sum
                   for i in range(len(mapping)):
                        best_mapping[i] = mapping[i]


     print()
     print("The best deciphered message is:")
     if (CONFUSE):
          deciphered = delete_chars(encipher(scrambled_message, best_mapping))
     else:
          deciphered = encipher(scrambled_message, best_mapping)
     print(deciphered)
     print()
    

     # DEBUGGING
     # print("Scrambled Message:")
     # print(scrambled_message)
     # print()
     # print("Last deciphered")
     # print(encipher(scrambled_message, mapping))
     # print("Counter: ", counter)
     # print("Acceptances: ", acceptances)

     return deciphered


# end decipher



########################
#####  MAIN BLOCK  #####
########################
if __name__ == "__main__":
     
     # define initial mapping in the same way as the global alphabet 
     mapping = list(string.ascii_letters) + [' ', ',', '.']

     # create and save transition matrix if needed
     if (not TRANSITION_MATRIX_SAVED):
          create_transition_matrix()
     # record transition matrix from War and Peace
     matrix = read_transition_matrix()
     


    #  define the message
     message = "The little princess went round the table with quick, short, swaying steps, her workbag on her arm, and gaily spreading out her dress sat down on a sofa near the silver samovar, as if all she was doing was a pleasure to herself and to all around her. I have brought my work, said she in French, displaying her bag and addressing all present. Mind, Annette, I hope you have not played a wicked trick on me, she added, turning to her hostess. You wrote that it was to be quite a small reception, and just see how badly I am dressed. And she spread out her arms to show her short waisted, lace trimmed, dainty gray dress, girdled with a broad ribbon just below the breast. Nicholas and his wife lived together so happily that even Sonya and the old countess, who felt jealous and would have liked them to disagree, could find nothing to reproach them with but even they had their moments of antagonism. Occasionally, and it was always just after they had been happiest together, they suddenly had a feeling of estrangement and hostility, which occurred most frequently during Countess Mary pregnancies, and this was such a time."
     # print(message)

     # Tricking the algorithm by modifiying the message
     if (CONFUSE):
          message = insert_chars(message)
          # print("Tricked/Modified message")
          # print(message)


     # DEBUGGING
     # print("Tricked")
     # print(message)
     # print()
     # print("Detricked")
     # print(delete_chars(insert_chars(message)))
     # print()
          

     # scramble the message
     scrambled_message = scramble(message)
     # print("Scrambled message")
     # print(scrambled_message)


     decipher(scrambled_message, mapping)

     # print original message in terminal to compare with best attempt at deciphering
     # print(message)
     if (CONFUSE):
          message = delete_chars(message)
     print("Original message:")
     print(message)
     print()


     




#############################
#############################
#######              ########
#######    PART 2    ########
#######              ########
#############################
#############################
     
# IN ORDER TO TRICK THE ALGORITHM, SET THE GLOBAL VARIABLE 'CONFUSE'
# TO TRUE AT THE BEGINNING OF THIS DOCUMENT. THIS CONDITION WILL 
# AUTOMATICALLY TAKE CARE OF MODIFYING AND DEMODIFYING THE MESSAGE
# AND IT WILL TRICK THE METROPOLIS ALGORITHM, FORCING IT TO FAIL
     
''' 

Two ways of tricking the Metropolis-Hastings deciphering algorithm:


1. Inserting Repeated Unlikely Transition Pair (IMPLEMENTED).

Before scrambling the message with a substitution cipher, first 
insert the same unlikely transition pair (2 characters) at every 5
characters into the original message, e.g 'qT'. So the message 
"princess" becomes "qTprincqTess". This will make the message
to appear very unlikely to be randomly generated from the 
"proper English" and will mess with acceptance probabilities of 
Metropolis-Hastings attacker. This is a very simple method to modify 
the initial message using insertion (and the de-modify using deletion)
that tricks the algorithm

Maximum Security: While this method succeeds in tricking the Metropolis
algorithm, i do not think it offers a lot of security, since it is highly
plausible that even upon visual insepction of the ciphered message,
one can notice the pattern of constantly repeated pair of characters every 5 letters.
It is a rather basic and obvious way to insert the same pair of 
characters throughout the text that is easily noticeable and also reversible.

Efficient Security: On the other hand, this simple method only takes two simple functions
to implement, and yet it still provides a certain level
of security in that the algorithm cannot decipher the modified message. Furthermore, since
the message appears as scrambled nonsense to Metropolis attacker, one may argue that
visual insepction of the scrambled message is not enough to notice such a modification.





2. Inserting Various Unlikely Transition Pairs (NOT IMPLEMENTED)

This second method similarly uses insertion of unlikely transition pairs into text,
but for this one we can first create a list of all impossible character transitions 
in the English language and randomly insert any such pair at fixed intervals in the
message. 

This provides much more security since now there is a much less obious repeated pattern
of the two same characters constantly showing up at equal intervals. With this method, 
we should not have any pair repeatedly showing up consistently. 
This method is still highly efficient for its security, although it takes somewhat more 
work that is not done here. To implement this method, one can take all the impossible character
transition pairs from the transition matrix (any values in the matrix equal to zero or MIN)
and put those character pairs in a list. Then modify the insert_chars function so that it 
randomly picks a pair of characters to insert.
 
'''
