import random

# sampling potential score
import csv
f = open('Data/new_potential_victim.csv', 'w')
writer = csv.writer(f)
with open('/Users/bill/Downloads/classify_victim.csv', newline='') as file:
    rows = csv.reader(file)
    next(rows)
    for i in rows:
        p = random.uniform(0.5, 1) if int(i[1]) else random.uniform(0, 0.5)
        writer.writerow([i[0], i[1], p])

f.close()