from yelp import process1, process2
from fileIO import encryptAll

#FILL OUT THIS REQUIRED INFORMATION PRIOR TO RUNNING
linkToClientBiz = 'https://www.yelp.com/biz/crown-of-india-plainsboro-2'
maximumDistanceFromClient = 30
minimumNumberOfReviewsPerUser = 7
password = "" #same as password to call encryption.exe

#RUN
if __name__ == '__main__':
    p1 = process1(linkToClientBiz)
    print('\n\n\n--------------------------------------------------------------------\n\n\n')
    p2 = process2(linkToClientBiz, maximumDistanceFromClient, minimumNumberOfReviewsPerUser)
    encryptAll(password)