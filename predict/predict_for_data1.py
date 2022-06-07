import json
import csv

with open('predict_user1.json', 'r') as f1:
    data1 = f1.read()
    user1 = json.loads(data1)

with open('predict_user2.json', 'r') as f2:
    data2 = f2.read()
    user2 = json.loads(data2)

f = open('output.csv', 'w')
writer = csv.writer(f)

with open('/Users/bill/Downloads/real_fake_users.csv', newline='') as ad_file:
    rows = csv.reader(ad_file)
    true1 = 0
    true2 = 0
    for i in rows:
        type = 'human' if int(i[0]) <= 220 else 'faker'
        if user1[i[1]][-1] == type:
            true1 += 1
        if user2[i[1]][-1] == type:
            true2 += 1
        writer.writerow([i[0], i[1], user1[i[1]][-1], user1[i[1]][0]])
    print(f'SybilRank Accuracy = { true1/429}')
    print(f'Integro Accuracy = { true2/429}')
f.close()