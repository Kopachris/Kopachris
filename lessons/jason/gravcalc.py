def gravforce(m1, m2, d):

    """This function calculates the gravitational force
    between two bodies given mass and distance.
    """
    
    #Employ formula
    force = (m1 * m2 * 6.67e-11)/(d ** 2)
	
    return force
	
	
def gravdisp(m1, m2, d, t, p):

    """This function calculates the distance travelled by two bodies
    due to gravitation over a given amount of time. It assumes both
    bodies are stationary to begin.
    """
    
    #Set up a loop with appropriate iterations for the time and
    #precision specified by the user
    v1 = 0
    v2 = 0
    d1 = 0
    d2 = 0
    for i in range(t * p):
        
        #Call gravforce for force and calculate velocity of each object
        F = gravforce(m1, m2, d)
        v1 = v1 + (F / (p * m1))
        v2 = v2 + (F / (p * m2))
        
        #Approximate distance travelled by each object and compute new
        #separation between objects
        d1 = d1 + (v1 / p)
        d2 = d2 + (v2 / p)
        d = d - d1 - d2
    
    ds = [d1, d2]
    return ds
    
    
if __name__=="__main__":
    print('Welcome to GravCalc!')
    
    #Put it in a loop to make it more civilized
    choice = 0
    while choice != 3:
    
        #Display a list of options for what to do with the information
        print('\nWhat would you like to do?')
        print('1: Calculate the force between two objects')
        print('2: Approximate the distance travelled by each object')
        print('3: Quit the program')
        choice = int(input())
        
        #Call the appropriate function
        if choice is 1:
        
            #Ask user for the masses of the two objects and the distance
            #between them
            m1 = (10 ** 21) * float(input('Mass of first object (Yg): '))
            m2 = (10 ** 21) * float(input('Mass of second object (Yg): '))
            d = float(input('Distance between objects (m): '))
            
            #Format the string and print the information
            s = 'The force of gravitation is %f Newtons.'% (gravforce(m1, m2, d))
            print(s)
            
        elif choice is 2:
            #Ask user for all relevant input
            m1 = (10 ** 21) * float(input('Mass of first object (Yg): '))
            m2 = (10 ** 21) * float(input('Mass of second object (Yg): '))
            d = float(input('Distance between objects (m): '))
            t = int(input('Test duration (s): '))
            p = int(input('Samples per second: '))
            
            #Format the strings and print the information
            ds = gravdisp(m1, m2, d, t, p)
            s1 = 'The first object moves %f meters.'% (ds[0])
            s2 = 'The second object moves %f meters.'% (ds[1])
            print(s1)
            print(s2)
            
        elif choice is 3:
            print('Goodbye')
            
        else:
            print('That is not a valid option.')

input()