from scraper import process1, process2, encryptAll, setup
from shutil import copytree
from random import randint
from os import getcwd, chdir

# FILL OUT THIS REQUIRED INFORMATION PRIOR TO RUNNING
# -------------------------------------------------------------------------------------------
linkToClientBiz = ""                               # link to client Yelp business
maximumDistanceFromClient = 0
minimumNumberOfReviewsPerUser = 0
password = ""                                                                           # same as password to call encryption.exe

# RUN
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # uncomment line 17 & line 24 to run only Process 2 so that it comments lines 18-23 (Process 1)
    # """
    base = getcwd()
    print(f'Files can be found at "{setup()}"')
    p1 = process1(linkToClientBiz)
    chdir(base)
    copytree('Database', f'P1_Backup_{randint(1,1000)}')
    print('\n\n\n--------------------------------------------------------------------\n\n\n')
    # """
    p2 = process2(linkToClientBiz, maximumDistanceFromClient, minimumNumberOfReviewsPerUser)
    if p2: encryptAll(password)
    else: print("Process 2 was terminated. Please review the error output and perform the necessary changes.")