import csv
import os

baseDir = '' #ENTER DIRECTORY FOR DATABASE FOLDER HERE

def removeEmptyLines(filename):
    if not os.path.isfile(filename):
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()
    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)

#A function to write a list to text file with newlines
def writeList(writerObj, lst):
    for i in range(len(lst)):
        if i > 0 and i < len(lst):
            writerObj.write('\n')
        writerObj.write(lst[i])
    return

#A function to read from a written text file, negating the \n that occurs
def readList(fileObj):
    return fileObj.read().split('\n')

#A function to read and create unique ID for next business(b)/reviewer or user(u)/review(r)
def createID(case, yelpid):
    os.chdir(baseDir)
    newIdStr = None
    upperCase = case.strip().upper()

    #Read the csv and make the new ID
    lines = []
    with open('id.csv') as id:
        for row in csv.DictReader(id):
            if row['category'] == upperCase.lower():
                newIdNum = str(int(row['currid']) + 1)
                newIdStr = upperCase + str(newIdNum)
                temprow = row
                temprow['currid'] = str(newIdNum)
                lines.append(temprow)
            else:
                lines.append(row)

    #Write the new ID to the csv
    with open('id.csv', 'w') as id:
        writer = csv.DictWriter(id, fieldnames=['category','currid'])
        writer.writeheader()
        writer.writerows(lines)
    removeEmptyLines('id.csv')

    #Go to directory for the case and update lookup file (only applicable for business or user files)
    if (upperCase == 'B') or (upperCase == 'U'):
        os.chdir(baseDir + '/' + upperCase)
        with open('lookup.csv','a+', newline='') as lookup:
            writer = csv.DictWriter(lookup, fieldnames=['yelpid', 'ourid'])
            writer.writerow({'yelpid' : yelpid, 'ourid' : newIdStr})
        removeEmptyLines('lookup.csv')

    return newIdStr

#A function to search and make sure that a business or user doesn't already exist in our database
def checkDuplicate(fileType, id):
    fileType = fileType.upper()

    #Check if business already exists; if it does, return our ID for the business
    if fileType == 'B':
        os.chdir(baseDir + '/B')
        with open('lookup.csv') as lookup:
            for row in csv.DictReader(lookup):
                if row['yelpid'] == id:
                    return row['ourid']

    #Check if user already exists; if it does, return our ID for the user
    elif fileType == 'U':
        os.chdir(baseDir +'/U')
        with open('lookup.csv') as lookup:
            for row in csv.DictReader(lookup):
                if row['yelpid'] == id:
                    return row['ourid']
    return None

#A function to do the opposite of checkDuplicate(); uses ourID to get yelpID
def getYelpID(id):
    id = id.upper()
    fileType = id[0]

    #Check if business already exists; if it does, return our ID for the business
    if fileType == 'B':
        os.chdir(baseDir + '/B')
        with open('lookup.csv') as lookup:
            for row in csv.DictReader(lookup):
                if row['ourid'] == id:
                    return row['yelpid']

    #Check if user already exists; if it does, return our ID for the user
    elif fileType == 'U':
        os.chdir(baseDir +'/U')
        with open('lookup.csv') as lookup:
            for row in csv.DictReader(lookup):
                if row['ourid'] == id:
                    return row['yelpid']
    return None

#A function to get the reviewer's internal ID using their Yelp ID
def getUserID(yelpID):
    duplicate = checkDuplicate('u', yelpID)

    if not duplicate:
        return createID('u', yelpID)
        
    return duplicate #Else, return existing ID

#A function to create a new business file
def createBiz(info, yelpid):
    newBizId = createID('b', yelpid)
    os.chdir(baseDir + '/B')
    with open(newBizId+'.txt', 'w') as newBiz:
        writeList(newBiz, info)
    removeEmptyLines(newBizId+'.txt')
    return newBizId

#A function to create a new review file 
def createReview(info):
    revId = createID('r', "")
    os.chdir(baseDir + '/R')
    with open(revId+'.txt', 'w') as newRev:
        writeList(newRev, info)
    removeEmptyLines(revId+'.txt')
    return revId

#A function to create or update new reviewer/user file
def createUser(info, userID, revID):
    os.chdir(baseDir + '/U')
    userFileName = userID + '.txt'

    #If the user doesn't exist, create a file for that reviewer and associate them with current review (line 3)
    if not userFileName in os.listdir(os.getcwd()):
        info.append(revID)
        with open(userFileName, 'w') as newUser:
            writeList(newUser, info)
    
    #If the user already exists, just append the review number to that user's associated review ids line (line 3)
    else: #If not newFile
        with open(userFileName, 'a+') as existingUser:
            existingUser.write(',' + revID)
        
    return userID

#A function that appends new review ids to the business file to associate those reviews with the business
def addRevsToBiz(bizId, revIDs, exists):
    os.chdir(baseDir + '/B')
    fileName = bizId + '.txt'
    
    with open(fileName,'a+') as biz:
        #If this is the first time we're adding review ids, we have to add all the review ids in a new line
        if not exists:
            biz.write('\n' + revIDs)
        #If the business exists, we can just append ',' and the new review ids to the end of the last line, which should contain the list of review ids
        else:
            biz.write(',' + revIDs)
    removeEmptyLines(fileName)
    return revIDs

#A function that can be used to retrieve information from all the different types of files
def retrieve(fileID, elementRow):
    #If it is a review file
    if fileID[0] == 'R':
        os.chdir(baseDir + '/R')
        with open(fileID + '.txt', 'r') as reviewFile:
            try:
                return readList(reviewFile)[elementRow]
            except:
                pass
    elif fileID[0] == 'U':
        os.chdir(baseDir + '/U')
        with open(fileID + '.txt', 'r') as userFile:
            try:
                return readList(userFile)[elementRow]
            except:
                pass
    elif fileID[0] == 'B':
        os.chdir(baseDir + '/B')
        with open(fileID + '.txt', 'r') as bizFile:
            try:
                return readList(bizFile)[elementRow]
            except:
                pass
    return "Element/row not found"

#A function to get the links to all the businesses (stored in our database) that a user has reviewed
def getUserBizIDs(userID):
    reviews = retrieve(userID, 2).split(',')
    bizIDs = []
    for review in reviews:
        bizIDs.append(retrieve(review, 1).strip())
    bizLinks = []
    os.chdir(baseDir + '/B')
    with open('lookup.csv') as lookup:
        for row in csv.DictReader(lookup):
            if len(bizIDs) > 0 and row['ourid'] in bizIDs:
                bizIDs.remove(row['ourid'])
                bizLinks.append(str(row['yelpid']).strip())

    return bizLinks

#A function to get all the user ids in our database, helps in process 2
def getAllUserIDs():
    ids = []
    os.chdir(baseDir + '/U')
    with open('lookup.csv') as lookup:
        for row in csv.DictReader(lookup):
            ids.append(row['ourid'])
    return ids
