import csv


file_path = "simulation/../output/"

def write_file(results, file_name):
    path = file_path + file_name
    with open(path, "a", newline = '', encoding='utf-8') as csvfile:
        write = csv.DictWriter(csvfile, fieldnames=results.keys())
        write.writerow(results)