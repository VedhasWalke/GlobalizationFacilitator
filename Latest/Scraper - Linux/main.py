from yelp import getUserReviews, process1, process2

#FILL OUT THIS REQUIRED INFORMATION PRIOR TO RUNNING AS WELL AS IN FILEIO.PY
linkToClientBiz = 'https://www.yelp.com/biz/crown-of-india-plainsboro-2'
maximumDistanceFromClient = 30
minimumNumberOfReviewsPerUser = 7

#RUN
if __name__ == '__main__':
    p1 = process1(linkToClientBiz)
    print(p1)
    print('\n\n\n--------------------------------------------------------------------\n\n\n')
    p2 = process2(linkToClientBiz, maximumDistanceFromClient, minimumNumberOfReviewsPerUser)
    print(p2)