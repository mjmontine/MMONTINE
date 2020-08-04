#Test Python Script
#print("Please God, don't let me embarrass myself in front of Denise")

import csv

fields = ['Name', 'Department']

rows = [ ['Mark', 'Records'],
         ['Macy', 'Collections'] ]

filename = "./src/report.csv"

with open(filename, 'w') as csvfile:
  csvwriter = csv.writer(csvfile)

  csvwriter.writerow(fields)

  csvwriter.writerows(rows)
