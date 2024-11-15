from scipy.stats import ks_2samp

file = open('commStartRelS1.txt', 'r')
Lines = file.readlines()

valuesS1 = []

for line in Lines:
    valuesS1.append(float(line))

file = open('commStartRelS2.txt', 'r')
Lines = file.readlines()

valuesS2 = []

for line in Lines:
    valuesS2.append(float(line))

print(ks_2samp(valuesS1, valuesS2))