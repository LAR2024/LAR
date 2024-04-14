

data = []

while True:
    with open('data.txt', 'r', encoding='utf-8') as FILE:
        all_data = FILE.read()
        print(all_data)


with open('data.txt', 'r', encoding='utf-8') as FILE:
    letter = FILE.read(1)
    print(letter)






