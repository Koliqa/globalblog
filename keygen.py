from string import ascii_letters
from random import randint


symbols = ascii_letters + '0123456789'
key = ''
for i in range(10):
    key += symbols[randint(0, len(symbols) - 1)]
print(key)
