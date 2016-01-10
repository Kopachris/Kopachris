def flag1(x):
    print("Ran flag1.")

def flag2(x):
    print("Ran flag2.")
    print("x = ", x)

def flag3(x):
    print("Ran flag3.")
    print("x + y = ", x[0] + x[1])

def flag4(x):
    print("Ran flag4.")

flags_dict = {0: flag1, 1: flag2, 2: flag3, 3: flag4}

flags = [1, 2, 0, 3, 1]
flag_args = [5, (7, 3), None, None, 4]

for i, f in enumerate(flags):
    flags_dict[f](flag_args[i])

#for f in flags:
#    print(f)
