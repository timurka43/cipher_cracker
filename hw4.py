"""
Title: Homework 4, part 1. Cracking a Cipher
Author: Timur Kasimov (Grinnell, 2025)
Data Created: March 31, 2024
Date Updated: March 31, 2024

Purpose: Implement and test a cipher-cracker using Metropolis-Hastings

This is a homework assignment for my Computational Methods Class
"""


import numpy as np
import pandas as pd

import math
import random

import string

ALPHABET = list(string.ascii_letters) + [' ', ',', '.']
LENGTH = len(ALPHABET)
MAXITER = 10000
MIN = math.exp(-20)


mapping = list(string.ascii_letters) + [' ', ',', '.']


# permutes the initial alphabet in random order, 
# creating random initial reverse cipher
def permute_alphabet():
    random.shuffle(mapping)



# swaps two elements of the reverse cipher in place
def swap_two(alphabet):
    new_mapping = alphabet.copy()
    i1, i2 =  random.sample(range(LENGTH), 2)
    new_mapping[i1], new_mapping[i2] = new_mapping[i2], new_mapping[i1]
    return new_mapping


''' creates transition matrix from the War and Peace text'''
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
                  #  take two neighbouring characters
                  ch1, ch2 = text[i], text[i+1]
                #   if both characters are in alphabet, ...
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
        df.to_csv('/Users/timur/CompMethods/cipher_cracker/transition_matrix.csv', sep=',', header=False, index=False)
#  end create_transition_matrix
        

''' reads previously generate transition matrix and returns the nparray object'''               
def read_transition_matrix():
    data = pd.read_csv('/Users/timur/CompMethods/cipher_cracker/transition_matrix.csv', header=None)
    # print(data)
    matrix = np.matrix(data.iloc[0:55, 0:55])
    # print(matrix)
    return matrix

                  
''' enciphers the string using the given cipher'''
def encipher(string, cipher):
    # for each character in the message
     my_list = list(string)
     for i in range(len(my_list)):
          char = my_list[i]
          index = ALPHABET.index(char)
          new_char = cipher[index]
          my_list[i] = new_char
    
     message = ''.join(str(x) for x in my_list)
     return message


     
          


''' calculates acceptance probability'''
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
     
def calc_acceptance(old_sum, new_sum):
     return math.exp(new_sum-old_sum)


def scramble(message):
     # create a random cipher from the alphabet
     permute_alphabet()
     # encipher the message using cipher/mapping
     return encipher(message, mapping)

if __name__ == "__main__":
     
     # record transition matrix from War and Peace
     matrix = read_transition_matrix()


    #  define the message
     message = "Hello my darling, I would like to kiss you. Nicholas and his wife lived together so happily that even Sonya and the old countess, who felt jealous and would have liked them to disagree, could find nothing to reproach them with but even they had their moments of antagonism. Occasionally, and it was always just after they had been happiest together, they suddenly had a feeling of estrangement and hostility, which occurred most frequently during Countess Mary pregnancies, and this was such a time."
     print(message)

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
