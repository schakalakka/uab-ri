import csv

# Read from a csv file and save as list of tuple
# https://stackoverflow.com/questions/18776370/converting-a-csv-file-into-a-list-of-tuples-with-python
with open('Arbeitsmappe1.csv', 'r') as f:
    my_data = [tuple(line) for line in csv.reader(f, delimiter=';')]

print((my_data[0][0]))
# print(len(my_data[0]))

for element in my_data:
    for x in element:
        print(type(x))
#        float(x)

#list(map(float,my_data[0][0]))

#print(type(my_data[0][0]))