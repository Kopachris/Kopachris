def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    print(i)
    
def main():
    file_len(input())
    
if __name__ == '__main__':
    main()