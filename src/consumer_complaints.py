import csv
import fileinput
import sqlite3
import sys, os

sys.path.append(os.path.realpath('..'))

def write_temp_csv():
    with open(os.path.realpath('complaints.csv'), encoding='utf8') as complaints:
        reader= csv.reader(complaints)
        for row in reader:
            included_cols = [1, 0, 7, 2]
            row = list(row[i] for i in included_cols)
            with open('csvtemp.csv', 'w+') as csvtemp:
                wr = csv.writer(csvtemp)
                wr.writerow(['product', 'date', 'company', 'p_y'])
                for row in reader:
                    row = list(row[i] for i in included_cols)
                    for i in range(len(row)):
                        row[i] = row[i].lower()
                    row[1] = row[1][-4:]
                    row[3] = row[0] + row[1]
                    wr.writerow(row)
                csvtemp.close
                complaints.close

write_temp_csv()

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE calculator (product, year, company, p_y);")
with open('csvtemp.csv', 'r') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['product'], i['date'], i['company'], i['p_y']) for i in dr]
    cur.executemany('INSERT INTO calculator (product, year, company, p_y) VALUES (?, ?, ?, ?);', to_db)
    cur.execute("CREATE TABLE calculator2 AS SELECT * FROM calculator ORDER BY product, year;")
    cur.execute("DROP TABLE calculator;")
    cur.execute("CREATE TABLE calculator AS SELECT * FROM calculator2 ORDER BY product, year;")
    cur.execute("DROP TABLE calculator2;")
    cur.execute('SELECT COUNT(DISTINCT p_y) FROM calculator;')
    count_distinct_p_y = [int(record[0]) for record in cur.fetchall()]
    cur.execute('SELECT DISTINCT p_y FROM calculator;')
    distinct_p_y = cur.fetchall()
    fin.close

def write_output_csv():
    with open(os.path.realpath('report.csv'), 'w+') as output_csv:
        wr = csv.writer(output_csv)
        wr.writerow(['product', 'year', 'total complaints', '# of companies recieving >=1 complaint', 'highest % of complaints against 1 company'])
        for i in range(0, count_distinct_p_y[0]):
            product = str(distinct_p_y[i])[2:-7]
            year = str(distinct_p_y[i])[-7:-3]
            cur.execute("SELECT count(*) FROM calculator WHERE year = '" + year + "' and product = '" + product + "';")
            total_complaints = str(cur.fetchall())[2:-3]
            cur.execute("SELECT count(DISTINCT company) FROM calculator WHERE year = '" + year + "' and product = '" + product + "';")
            at_least_1 = str(cur.fetchall())[2:-3]
            cur.execute("SELECT count(*) AS cnt FROM calculator WHERE year = '" + year + "' and product = '" + product + "' GROUP BY company ORDER BY cnt DESC LIMIT 1;")
            highest_percentage = str(cur.fetchall())[2:-3]
            highest_int = int(highest_percentage)
            total_int = int(total_complaints)
            final_highest = int(round(((highest_int / total_int) * 100), 2))

            row = list([product, year, total_complaints, at_least_1, final_highest])
            wr.writerow(row)
        output_csv.close

write_output_csv()

con.commit()
con.close()
