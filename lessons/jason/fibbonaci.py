def fibbonaci(n):
	
	"""This function takes an input of n and returns the nth fibbonaci number.
	"""
	
	#hardcode the exact value of phi
	phi = ((1 + (5 ** 0.5)) / 2)
	
	#compute the nth fibbonaci number using Binet's Formula and round to an integer
	fib = ((phi ** n) - ((-phi) ** (-n))) / (5 ** 0.5)
	fib = round(fib)
	
	return fib

#obtain user input for n
n=input('Please provide a natural number: ')
n=int(n)

#Print the nth fibbonaci number
print(fibbonaci(n))

input()