
import csv

def read_csv(filename):
    """
    Read a csv file with only event locations
    :param: filename
    :return:
    """
    with open(filename, 'r') as f:
        my_data = [tuple(line) for line in csv.reader(f, delimiter=';')]
        float_my_data = [(float(e[0]), float(e[1])) for e in my_data]
        return float_my_data
