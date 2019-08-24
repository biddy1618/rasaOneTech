

with open('./onetech/scriptsData/intents.txt', 'r') as f:
    data = f.readlines()

with open('./onetech/scriptsData/intentsClean.txt', 'w') as f:
    for line in data:
        f.write(line[4:])
