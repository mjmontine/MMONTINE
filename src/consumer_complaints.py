'''
Mark Montine
Started 08/08/2020. Finished 08/06/2020
Insight Data Engineering - Coding CodeChallenge

Generally, this code writes a temporary csv to pull, sort, and scrub data from an input of standard column organization
Then it creates a temporary sqlite3 database used for calculating.  It sort of has to make two copies and delete one to
get everything in the ultimate order.  Then it writes the output csv called "report".  This is done with a combination
of data from the temporary database and calculations done using sqlite3 queries.  Then it closes the csv's and database.

'''
#Modules needed:
import csv
import fileinput
import sqlite3
import sys, os
import re

#Read input, organize data, and create temporary csv to move to db
def write_temp_csv():
    #open and read input data from "complaints.csv"
    with open('./input/complaints.csv', encoding='utf8') as complaints:
        reader= csv.reader(complaints)
        for row in reader:
            #row 2 is included as a dummy row to later place a product_year value that acts like a key
            included_cols = [1, 0, 7, 2]
            row = list(row[i] for i in included_cols)
            #create and fill a temporary CSV with data from the input csv, "complaints.csv"
            with open('csvtemp.csv', 'w+') as csvtemp:
                wr = csv.writer(csvtemp)
                #row headers, as it should be
                wr.writerow(['product', 'date', 'company', 'p_y'])
                for row in reader:
                    row = list(row[i] for i in included_cols)
                    for i in range(len(row)):
                        #convert everything to lowercase per instructions
                        row[i] = row[i].lower()
                    #the test data and example files had different date formats, so the next three lines
                    #look for a string of 4 digits in a row and use that as the year
                    regex="\d{4}"
                    year = (re.findall(regex, row[1]))
                    row[1] = str(year)[-6:-2]
                    #the dummy row gets filled with product and year to create a unique identifier
                    row[3] = row[0] + row[1]
                    wr.writerow(row)
                #no use keeping these open
                csvtemp.close
                complaints.close

write_temp_csv()

#Open a connection to a temporary sqlite3 db and label the rows to match the temp csv
con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE calculator (product, year, company, p_y);")

#Read temp csv, populate sql3 db, re-order data to ultimate order, and grab a couple useful variables
with open('csvtemp.csv', 'r') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['product'], i['date'], i['company'], i['p_y']) for i in dr]
    cur.executemany('INSERT INTO calculator (product, year, company, p_y) VALUES (?, ?, ?, ?);', to_db)
    #there must be a better way to re-order a db, but this worked and I couldn't figure anythign else out
    #create a clone table
    cur.execute("CREATE TABLE calculator2 AS SELECT * FROM calculator ORDER BY product, year;")
    #drop the old table
    cur.execute("DROP TABLE calculator;")
    #recreate the old table, copied from the clone and put in the correct order this time
    cur.execute("CREATE TABLE calculator AS SELECT * FROM calculator2 ORDER BY product, year;")
    #then drop the clone
    cur.execute("DROP TABLE calculator2;")
    #grab the number of distinct product-year pairs because that's how many rows the output csv will have
    cur.execute('SELECT COUNT(DISTINCT p_y) FROM calculator;')
    count_distinct_p_y = [int(record[0]) for record in cur.fetchall()]
    #grab the product-year as a string to reference when building the output
    cur.execute('SELECT DISTINCT p_y FROM calculator;')
    distinct_p_y = cur.fetchall()
    #shut the door on your way out, please
    fin.close

#Open/create the output csv, "report.csv" fill it with known values and sqlite3 query returns
def write_output_csv():
    with open('./output/report.csv', 'w+') as output_csv:
        wr = csv.writer(output_csv)
        #next line inserts headers into "output.csv", but the test-bot didn't like that, so it will stay grey
        #wr.writerow(['product', 'year', 'total complaints', '# of companies recieving >=1 complaint', 'highest % of complaints against 1 company'])
        for i in range(0, count_distinct_p_y[0]):
            #product is pulled from the p_y key and parsed based on position.  Fallible? Yes.  Functional? Also yes.
            product = str(distinct_p_y[i])[2:-7]
            #year is pulled similarly.  Much less worried about this failing because of the regex in write_temp_csv()
            year = str(distinct_p_y[i])[-7:-3]
            #total complaints is a count of all complaints for a given year and product combination
            cur.execute("SELECT count(*) FROM calculator WHERE year = '" + year + "' and product = '" + product + "';")
            total_complaints = str(cur.fetchall())[2:-3]
            #at least one is a count of distinct companies for a given year and product combination
            cur.execute("SELECT count(DISTINCT company) FROM calculator WHERE year = '" + year + "' and product = '" + product + "';")
            at_least_1 = str(cur.fetchall())[2:-3]
            #highest percentage is a multistep process. First, it counts all compaints, grouped by company, for a given year and product combination
            cur.execute("SELECT count(*) AS cnt FROM calculator WHERE year = '" + year + "' and product = '" + product + "' GROUP BY company ORDER BY cnt DESC LIMIT 1;")
            highest_percentage = str(cur.fetchall())[2:-3]
            #Then it divides the highest by the total complaints (from above), multiplies by 100 and rounds to a whole number, per the instrunctions
            highest_int = int(highest_percentage)
            total_int = int(total_complaints)
            final_highest = int(round(((highest_int / total_int) * 100), 2))
            #add everything to the row and loop back to do it again
            row = list([product, year, total_complaints, at_least_1, final_highest])
            wr.writerow(row)
        output_csv.close

write_output_csv()
#don't forget to turn the lights off, thanks
con.commit()
con.close()
