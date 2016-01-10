print('Hello, World!\n\nI\'m glad to be here!')
for i in range(100):
    if not i%3 and not i%5:
        print('fizz buzz')
    elif not i%5:
        print('buzz')
    elif not i%3:
        print('fizz')
    else:
        print(i)