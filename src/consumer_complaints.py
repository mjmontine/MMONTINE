#Test Python Script
#print("Please God, don't let me embarrass myself in front of Denise")

import csv

fields = ['Name', 'Department']

rows = [ ['Mark', 'Records'],
         ['Macy', 'Collections'] ]

filename = "name_department.csv"

with open(filename, 'w') as csvfile:
  csvwriter = csv.writer(csvfile)

  csvwriter.writerow(fields)

  csvwriter.writerows(rows)
