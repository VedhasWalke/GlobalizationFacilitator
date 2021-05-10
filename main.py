from fileIO import encryptAll, setup				# If using Windows
# from fileIO_linux import encryptAll, setup  		# If using Linux
from yelp import process1, process2

#FILL OUT THIS REQUIRED INFORMATION PRIOR TO RUNNING
linkToClientBiz = ""
maximumDistanceFromClient = 30
minimumNumberOfReviewsPerUser = 7
password = "" #same as password to call encryption.exe

#RUN
if __name__ == '__main__':
    setup()
    p1 = process1(linkToClientBiz)
    print('\n\n\n--------------------------------------------------------------------\n\n\n')
    p2 = process2(linkToClientBiz, maximumDistanceFromClient, minimumNumberOfReviewsPerUser)
    encryptAll(password)