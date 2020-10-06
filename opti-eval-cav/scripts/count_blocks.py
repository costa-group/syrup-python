import os

contracts_path = "./initial/blocks/"

if __name__ == '__main__':
    num = 0
    l = os.listdir(contracts_path)
    for c in l:
        num_bl = os.listdir(contracts_path+c+"/")
        num+=len(num_bl)
    print num
