def refactorial(n):
    """This function finds the factorial of a user-provided integer.
    """
    
    # Recursively compute the factorial of n
    if n <= 1:
        return 1
    else:
        return n * refactorial(n - 1)

n = input('Provide a natural number: ')
n = int(n)
print(refactorial(n))

input()