"""
Title: Homework 4, parts 1 and 2. Cracking a Cipher
Author: Timur Kasimov (Grinnell, 2025)
Data Created: March 31, 2024
Date Updated: April 4th, 2024

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

TRANSITION_MATRIX_SAVED = True



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
#  calc_num  #
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


#############
#  reverse  #
#############
'''
Pre-conditions:
     message: original message
Post-conditions: 
     reversed message: reversed string from the original message
Purpose: reverses the message before using substitution cipher on it.
     This is one of the ways to confuse the decipherers and make the
     Metropolis-Hastings deciphering algorithm fail.
'''
def reverse(message):
     return message[::-1]



########################
#####  MAIN BLOCK  #####
########################
if __name__ == "__main__":
     
     # define initial mapping in the same way as the global alphabet 
     mapping = list(string.ascii_letters) + [' ', ',', '.']

     # record transition matrix from War and Peace
     matrix = read_transition_matrix()


    #  define the message
     message = "Nicholas and his wife lived together so happily that even Sonya and the old countess, who felt jealous and would have liked them to disagree, could find nothing to reproach them with but even they had their moments of antagonism. Occasionally, and it was always just after they had been happiest together, they suddenly had a feeling of estrangement and hostility, which occurred most frequently during Countess Mary pregnancies, and this was such a time."
     print(message)
     # message = reverse(message)



     # scramble the message
     scrambled_message = scramble(message)

     # create an initial deciphering mapping
     permute_alphabet()

     # first attempt at deciphering
     deciphered_message = encipher(scrambled_message, mapping)
     # calculate new sum of logs of probabilities of transitions
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

     print("Original message:")
     print(message)
     print()
     print("Scrambled Message:")
     print(scrambled_message)
     print()
     print("The best deciphered message is:")
     print(encipher(scrambled_message, best_mapping))
     print()
     print("Last deciphered")
     print(encipher(scrambled_message, mapping))
     print("Counter: ", counter)
     print("Acceptances: ", acceptances)





     




    

''' two ways of tricking the algorithm:

1. reverse the message
2. add an unlikely transition like qt every 10 characters 

'''
