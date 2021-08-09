import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from geopy.geocoders import Nominatim, base
from base64 import b64encode, b64decode
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random
from geopy import distance
from math import ceil
from string import printable
from sys import platform

options = Options()
options.add_argument('--headless')
options.add_argument("--log-level=3")  # fatal
options.add_argument("--start-maximized")

#Disable images to speed it up
chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

browser = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
browser.implicitly_wait(7)
dist = distance.distance
geolocator = Nominatim(user_agent="GlobalizationFacilitator")
BLOCK_SIZE = 16
validChars = set(printable)
baseDir = ""

"""
File I/O
"""

def setup():
    subdirs = ["R","U","B"]
    os.mkdir("Database")
    os.chdir("Database")
    global baseDir
    baseDir = os.getcwd()
    open("id.csv",'w').write("category,currid\nr,0\nu,0\nb,0")
    for dir in subdirs:
        os.mkdir(dir)
    for dir in subdirs[1:]:
        os.chdir(dir)
        open("lookup.csv",'w').write("yelpid,ourid\n")
        os.chdir(baseDir)
    return baseDir

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
readList = lambda fileObj: fileObj.read().split('\n')

#A function to remove invalid characters from strings
clean = lambda s: ''.join(filter(lambda x: x in validChars, s))

if platform.startswith("win"):
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
            os.chdir(baseDir + '\\' + upperCase)
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
            os.chdir(baseDir + '\\B')
            with open('lookup.csv') as lookup:
                for row in csv.DictReader(lookup):
                    if row['yelpid'] == id:
                        return row['ourid']

        #Check if user already exists; if it does, return our ID for the user
        elif fileType == 'U':
            os.chdir(baseDir +'\\U')
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
            os.chdir(baseDir + '\\B')
            with open('lookup.csv') as lookup:
                for row in csv.DictReader(lookup):
                    if row['ourid'] == id:
                        return row['yelpid']

        #Check if user already exists; if it does, return our ID for the user
        elif fileType == 'U':
            os.chdir(baseDir +'\\U')
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
        os.chdir(baseDir + '\\B')
        with open(newBizId+'.txt', 'w') as newBiz:
            writeList(newBiz, [str(inf) for inf in info])
        removeEmptyLines(newBizId+'.txt')
        return newBizId

    #A function to create a new review file 
    def createReview(info):
        revId = createID('r', "")
        os.chdir(baseDir + '\\R')
        with open(revId+'.txt', 'w') as newRev:
            writeList(newRev, [str(inf) for inf in info])
        removeEmptyLines(revId+'.txt')
        return revId

    #A function to create or update new reviewer/user file
    def createUser(info, userID, revID):
        os.chdir(baseDir + '\\U')
        userFileName = userID + '.txt'

        #If the user doesn't exist, create a file for that reviewer and associate them with current review (line 3)
        if not userFileName in os.listdir(os.getcwd()):
            info.append(revID)
            with open(userFileName, 'w') as newUser:
                writeList(newUser, [str(inf) for inf in info])
        
        #If the user already exists, just append the review number to that user's associated review ids line (line 3)
        else: #If not newFile
            with open(userFileName, 'a+') as existingUser:
                existingUser.write(' ' + revID)
            
        return userID

    #A function that appends new review ids to the business file to associate those reviews with the business
    def addRevsToBiz(bizId, revIDs, exists):
        os.chdir(baseDir + '\\B')
        fileName = bizId + '.txt'
        with open(fileName,'a+') as biz:
            #If this is the first time we're adding review ids, we have to add all the review ids in a new line
            if not exists:
                biz.write('\n' + revIDs)
            #If the business exists, we can just append ',' and the new review ids to the end of the last line, which should contain the list of review ids
            else:
                biz.write(' ' + revIDs)
        removeEmptyLines(fileName)
        return revIDs

    #A function that can be used to retrieve information from all the different types of files
    def retrieve(fileID, elementRow):
        #If it is a review file
        if fileID[0] == 'R':
            os.chdir(baseDir + '\\R')
            with open(fileID + '.txt', 'r') as reviewFile:
                try:
                    return readList(reviewFile)[elementRow]
                except:
                    pass
        elif fileID[0] == 'U':
            os.chdir(baseDir + '\\U')
            with open(fileID + '.txt', 'r') as userFile:
                try:
                    return readList(userFile)[elementRow]
                except:
                    pass
        elif fileID[0] == 'B':
            os.chdir(baseDir + '\\B')
            with open(fileID + '.txt', 'r') as bizFile:
                try:
                    return readList(bizFile)[elementRow]
                except:
                    pass
        return "Element/row not found"

    #A function to get the links to all the businesses (stored in our database) that a user has reviewed
    def getUserBizIDs(userID):
        reviews = retrieve(userID, 2).split(' ')
        bizIDs = []
        for review in reviews:
            bizIDs.append(retrieve(review, 1).strip())
        bizLinks = []
        os.chdir(baseDir + '\\B')
        with open('lookup.csv') as lookup:
            for row in csv.DictReader(lookup):
                if len(bizIDs) > 0 and row['ourid'] in bizIDs:
                    bizIDs.remove(row['ourid'])
                    bizLinks.append(str(row['yelpid']).strip())
        return bizLinks

    #A function to get all the user ids in our database, helps in process 2
    def getAllUserIDs():
        ids = []
        os.chdir(baseDir + '\\U')
        with open('lookup.csv') as lookup:
            for row in csv.DictReader(lookup):
                ids.append(row['ourid'])
        return ids

    #Called at the end of main() to encrypt all created files
    def encryptAll(password):
        #[R]eviews
        os.chdir(baseDir + "\\R")
        for r in os.listdir():
            content = open(r, 'rb').read()
            try:
                open(r, 'wb').write(encrypt(content, password))
                print(f"Successfully encrypted {r}")
            except:
                open(r, 'wb').write(content)
                print(f'Error encrypting {r}')
        #[U]sers
        os.chdir(baseDir + "\\U")
        for u in os.listdir():
            content = open(u, 'rb').read()
            try:
                open(u, 'wb').write(encrypt(content, password))
                print(f"Successfully encrypted {u}")
            except:
                open(u, 'wb').write(content)
                print(f'Error encrypting {u}')
        #[B]usinesses
        os.chdir(baseDir + "\\B")
        for b in os.listdir():
            content = open(b, 'rb').read()
            try:
                open(b, 'wb').write(encrypt(content, password))
                print(f"Successfully encrypted {b}")
            except:
                open(b, 'wb').write(content)
                print(f'Error encrypting {b}')
        return

    def decryptAll(password):
        os.chdir(baseDir + "\\R")
        for r in os.listdir():
            content = open(r, 'rb').read()
            try:
                open(r, 'wb').write(decrypt(content, password))
                print(f"Successfully decrypted {r}")
            except:
                open(r, 'wb').write(content)
                print(f'Error decrypting {r}')
        #[U]sers
        os.chdir(baseDir + "\\U")
        for u in os.listdir():
            content = open(u, 'rb').read()
            try:
                open(u, 'wb').write(decrypt(content, password))
                print(f"Successfully decrypted {u}")
            except:
                open(u, 'wb').write(content)
                print(f'Error decrypting {u}')
        #[B]usinesses
        os.chdir(baseDir + "\\B")
        for b in os.listdir():
            content = open(b, 'rb').read()
            try:
                open(b, 'wb').write(decrypt(content, password))
                print(f"Successfully decrypted {b}")
            except:
                open(b, 'wb').write(content)
                print(f'Error decrypting {b}')
        return

elif platform.startswith("linux"):
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
            writeList(newBiz, [str(inf) for inf in info])
        removeEmptyLines(newBizId+'.txt')
        return newBizId

    #A function to create a new review file 
    def createReview(info):
        revId = createID('r', "")
        os.chdir(baseDir + '/R')
        with open(revId+'.txt', 'w') as newRev:
            writeList(newRev, [str(inf) for inf in info])
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
                writeList(newUser, [str(inf) for inf in info])
        
        #If the user already exists, just append the review number to that user's associated review ids line (line 3)
        else: #If not newFile
            with open(userFileName, 'a+') as existingUser:
                existingUser.write(' ' + revID)
            
        return userID

    #A function that appends new review ids to the business file to associate those reviews with the business
    def addRevsToBiz(bizId, revIDs, exists):
        os.chdir(baseDir + '/B')
        fileName = bizId + '.txt'
        with open(fileName,'a+') as biz:
            #If this is the first time we're adding review ids, we have to add all the review ids in a new line
            if not exists:
                biz.write('\n' + revIDs)
            #If the business exists, we can just append ' ' and the new review ids to the end of the last line, which should contain the list of review ids
            else:
                biz.write(' ' + revIDs)
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
        reviews = retrieve(userID, 2).split(' ')
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

    #Called at the end of main() to encrypt all created files
    def encryptAll(password):
        #[R]eviews
        os.chdir(baseDir + "/R")
        for r in os.listdir():
            content = open(r, 'rb').read()
            try:
                open(r, 'wb').write(encrypt(content, password))
                print(f"Successfully encrypted {r}")
            except:
                open(r, 'wb').write(content)
                print(f'Error encrypting {r}')
        #[U]sers
        os.chdir(baseDir + "/U")
        for u in os.listdir():
            content = open(u, 'rb').read()
            try:
                open(u, 'wb').write(encrypt(content, password))
                print(f"Successfully encrypted {u}")
            except:
                open(u, 'wb').write(content)
                print(f'Error encrypting {u}')
        #[B]usinesses
        os.chdir(baseDir + "/B")
        for b in os.listdir():
            content = open(b, 'rb').read()
            try:
                open(b, 'wb').write(encrypt(content, password))
                print(f"Successfully encrypted {b}")
            except:
                open(b, 'wb').write(content)
                print(f'Error encrypting {b}')
        return

    def decryptAll(password):
        os.chdir(baseDir + "/R")
        for r in os.listdir():
            content = open(r, 'rb').read()
            try:
                open(r, 'wb').write(decrypt(content, password))
                print(f"Successfully decrypted {r}")
            except:
                open(r, 'wb').write(content)
                print(f'Error decrypting {r}')
        #[U]sers
        os.chdir(baseDir + "/U")
        for u in os.listdir():
            content = open(u, 'rb').read()
            try:
                open(u, 'wb').write(decrypt(content, password))
                print(f"Successfully decrypted {u}")
            except:
                open(u, 'wb').write(content)
                print(f'Error decrypting {u}')
        #[B]usinesses
        os.chdir(baseDir + "/B")
        for b in os.listdir():
            content = open(b, 'rb').read()
            try:
                open(b, 'wb').write(decrypt(content, password))
                print(f"Successfully decrypted {b}")
            except:
                open(b, 'wb').write(content)
                print(f'Error decrypting {b}')
        return

"""
Encryption
"""

#A function to encrypt a decrypted phrase
def encrypt(raw, password):
	private_key = sha256(password.encode("utf-8")).digest()
	raw = pad(raw, BLOCK_SIZE)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(private_key, AES.MODE_CBC, iv)
	return b64encode(iv + cipher.encrypt(raw))

#A function to decrypt an encrypted phrase
def decrypt(enc, password):
	private_key = sha256(password.encode("utf-8")).digest()
	enc = b64decode(enc)
	iv = enc[:16]
	cipher = AES.new(private_key, AES.MODE_CBC, iv)
	return unpad(cipher.decrypt(enc[16:]), BLOCK_SIZE)

"""
Yelp Scraper
"""

"""
	Process 1:

	Starting at the client business, scrape all basic business information and reviews
	Then, move to competitor businesses found using various features of Yelp such as:
	"People also viewed"
	"[client business type] near [client business name]"
	"Best [client business type] in [client location]"
	Get the basic business information as well as all reviews for these businesses
"""

#A function to get the links for each business on a search results page
def getLinks(numBiz, clientYelpID):
    #If you want the client business as part of the results, just put "GlobalizationFacilitator" as the clientYelpID
	links = []
	try:
		ul = browser.find_element_by_xpath("(//ul)[1]").find_elements_by_tag_name("li")
		for li in ul:
			if numBiz > 0:
				try:
					newLink = li.find_element_by_xpath("(//a)[2]").get_attribute('href')
					if clientYelpID not in newLink:
						links.append(newLink)
						numBiz -= 1
				except:
					pass
	except:
		pass
	
	print(f'Got links for {clientYelpID}')
	return links

#A function to get required attributes of a review
def getRevInfo(revObj, bizID):
	currRev = []
	currReviewer = []
	
	#Append the business ID for which this review was written
	currRev.append(bizID)
	
	#Try getting date of review
	try:
		revDate = revObj.find_element_by_xpath("div[2]/div/div[2]/span").text
	except:
		revDate = "No review date"
	currRev.append(revDate)

	#Try getting rating of review
	try:
		revRating = revObj.find_element_by_xpath("div[2]/div/div[1]/span/div").get_attribute("aria-label").split()[0]
	except:
		revRating = "No rating"
	currRev.append(revRating)

	#Try getting content of review
	try:
		revContent = clean(revObj.find_element_by_xpath("div[3]/p/span").text.replace('\n', ' ').strip())
	except:
		try:
			revContent = clean(revObj.find_element_by_xpath("div[4]/p/span").text.replace('\n', ' ').strip())
		except:
			revContent = "No content"
	currRev.append(revContent)

	#Try getting name of reviewer & link to profile
	userName = "No reviewer name"
	userLink = "No link to reviewer profile"
	try:
		user = revObj.find_element_by_xpath("div[1]/div/div[1]/div/div/div[2]/div[1]/span/a")
		try:
			userName = clean(user.text)
		except:
			pass
		try:
			userLink = user.get_attribute('href')
		except:
			pass
	except:
		pass
	currReviewer.append(userName)
	currReviewer.append(userLink)

	#Get the reviewer's internal ID
	reviewerID = getUserID(currReviewer[1].split('=')[1])
	currRev.insert(0, reviewerID)

	#Get our ID for the new review (returned by this function) while creating the file for the review
	newRevId = createReview(currRev)
	print(f'Created review {newRevId}')

	#Create or update a reviewer profile with the new review information
	createUser(currReviewer, reviewerID, newRevId)
	print(f'Created user {reviewerID}')

	return newRevId

#A function to get all the reviews for a business
def getAllReviews(bizId):
    nextPage = True
    ids = []

    while nextPage:
        time.sleep(3)
        try:
            revs = browser.find_element_by_xpath("//section[last()]/div[2]/div/ul").find_elements_by_tag_name("li")
            for rev in revs:
                rev = rev.find_element_by_xpath("div")
                try:
                    ids.append(getRevInfo(rev, bizId))
                except:
                    pass
        except:
            pass
        try:
            time.sleep(1)
            pageNums = browser.find_element_by_xpath("//div[2]/div/div[4]/div[2]").text.strip().split(" of ")
            if pageNums[0] != pageNums[-1]:
                browser.find_element_by_xpath("(//div[2]/div/div[4]/div[1]/div//div[last()])[last()]").click()
            else:
                print(f'{bizId}: got to end of review pages at page {pageNums[-1]}')
                nextPage = False
        except:
            print(f'{bizId}: got to end of review pages at page 1')
            nextPage = False
    return ids

#A function to get only the basic information from a single business
def getBasicBizInfo(link):
	currBiz = []
	browser.get(link) #Load business page
	
	#Check if the business already exists in our database
	bizYelpID = link.replace('https://www.yelp.com/biz/','').split('?')[0]
	duplicate = checkDuplicate('b', bizYelpID)

	#If the business isn't in the database, scrape the basic info of the business
	if not duplicate:
	
		# Try getting name of business on Yelp
		try:
			bizName = clean(browser.find_element_by_tag_name("h1").text)
		except:
			bizName = "No name found"
		currBiz.append(bizName)

		#Try getting rating of business on Yelp
		try:
			bizRating = browser.find_element_by_xpath("//div[2]/div[1]/span/div").get_attribute("aria-label").split()[0]
		except:
			bizRating = "No rating found"
		currBiz.append(bizRating)

		#Try getting categories of business on Yelp
		try:
			bizCategories = browser.find_element_by_xpath('//div/div[2]/div[1]/div[1]/div/div/span[last()]').text
		except:
			bizCategories = "No categories found"
		currBiz.append(bizCategories.strip())

		#Try getting location of business on Yelp
		try:
			bizLoc = browser.find_element_by_xpath("//p/a[text()='Get Directions']/parent::p/following-sibling::p").text.strip()
		except:
			bizLoc = "No address found"
		currBiz.append(bizLoc)

		#Try getting the phone number of business on Yelp
		try:
			bizPh = browser.find_element_by_xpath("//div/p[text()='Phone number']/following-sibling::p").text
		except:
			bizPh = "No phone number found"
		currBiz.append(bizPh)

		#Try getting website of business on Yelp
		try:
			bizWebsite = browser.find_element_by_xpath("//div/p[text()='Business website']/following-sibling::p").text
		except:
			bizWebsite = "No website found"
		currBiz.append(bizWebsite)

		#Try getting description of business on Yelp
		try:
			browser.find_element_by_xpath("//span[text()='Read more']").click()
			bizDesc = clean(browser.find_element_by_xpath("//h5[contains(text(), 'Specialties')]/parent::div/following-sibling::p").text.replace('Specialties','',1).replace('\n',' ').strip())
			browser.find_element_by_xpath("//span[text()='Close']").click()
		except:
			bizDesc = "No description found"
		currBiz.append(bizDesc)

		#Create a file for the new business in database
		bizId = createBiz(currBiz, bizYelpID)
	
	else:
		bizId = duplicate

	print(f'Got basic business info for {bizId}')
	return bizId, duplicate

#A function to get all the required information from a single business
def getAllBizInfo(link):
	bizId, duplicate = getBasicBizInfo(link)

	#Go back and add the associated reviews to the business file (parameter 2: generates string of new review IDs from list currBizRevIds)
	allRevs = getAllReviews(bizId)
	print(allRevs)
	addRevsToBiz(bizId, ' '.join(allRevs), duplicate)
	print(f'Got allBizInfo for business {bizId}')
	return bizId

#A function that will get direct competitor business links (Nearby & Also Searched For)
def getAllCompetitorsList(clientYelpID):
	finalCompetitors = []

	#Get links from 'other places nearby' menu
	try:
		for i in range(len(browser.find_elements_by_partial_link_text('Find more'))):
			refreshedList = browser.find_elements_by_partial_link_text('Find more')
			refreshedList[i].click()
			finalCompetitors += getLinks(10, clientYelpID)
			browser.back()
	except:
		print("Error scraping business information for nearby businesses")
		
	#Get links from 'people also searched for' menu
	try:
		peopleSearchedFor = browser.find_element_by_xpath("//h4[contains(text(), 'by searching for')]//following-sibling::ul").find_elements_by_tag_name("li")
		for i in range(len(peopleSearchedFor)):
			refreshedList = browser.find_element_by_xpath("//h4[contains(text(), 'by searching for')]//following-sibling::ul").find_elements_by_tag_name("li")
			refreshedList[i].click()
			finalCompetitors += getLinks(10, clientYelpID)
			browser.back()
	except:
		print("Error scraping business information for also searched businesses")
	
	#Get links from 'people also viewed'
	try:
		allLinks = browser.find_element_by_xpath("//h4[contains(text(), 'People Also Viewed')]//parent::div//parent::div//following-sibling::div").find_elements_by_tag_name("a")
		for i in range(len(allLinks)):
			if not (i + 1) % 2:
				finalCompetitors.append(allLinks[i].get_attribute('href'))
	except:
		print("Unable to find link to also searched businesses")

	bizes = []
	for competitor in finalCompetitors:
		browser.get(competitor)
		bizes.append(browser.current_url.split('?')[0])

	print(f'Got list of competitors for business {clientYelpID}')
	return set(bizes)

#A function that will scrape info from all direct competitors
def getAllCompetitorsInfo(bizList):
	scrapedBiz = [getAllBizInfo(i) for i in bizList]
	print(f'Got all competitor info for competitors {scrapedBiz}')
	return scrapedBiz

#MAIN function for PROCESS 1
def process1(clientLink):
	clientLink = clientLink.strip()
	getAllBizInfo(clientLink)
	competitorIDs =  getAllCompetitorsInfo(getAllCompetitorsList(clientLink.split('https://www.yelp.com/biz/')[1].split('?')[0]))	
	print("FINISHED PROCESS 1")
	return competitorIDs

"""
	Process 2:

	Navigate to each related reviewer's profile and find similar businesses they have reviewed in a certain location radius
	If the number of relevant reviews < number specified, get enough reviews to fulfill the minimum requirement
	If the total number of reviews for that user is less than the minimum requirement, gets all present reviews
	This process is used to aid the ML algorithm in getting an idea of the reviewer
"""

#A function to get the individual attributes of each review from a user profile (different layout/elements so different function)
def getRevInfoReviewerPage(reviewElementIndex, userID):
    #Scrape the review info
	revInfo = []                

	#The first attribute is the user ID, we already know that
	revInfo.append(userID)

	#Insert business ID at end after creation of file

	#Try getting the date of the review
	try:
		revDate = reviewElementIndex.find_elements_by_class_name("rating-qualifier")[0].text
	except:
		revDate = "No review date"
	revInfo.append(revDate)

	#Try getting the rating of the review
	try:
		revRating = reviewElementIndex.find_element_by_xpath("//div[@class='biz-rating__stars']/div").get_attribute('title').split()[0].strip()
	except:
		revRating = "No rating"
	revInfo.append(revRating)

	#Try getting the content of the review
	try:
		revContent = clean(reviewElementIndex.find_element_by_tag_name('p').text.replace('\n',' ').strip())
	except:
		revContent = "No content"
	revInfo.append(revContent)

    #Scrape the business info
	try:
		bizLink = reviewElementIndex.find_element_by_tag_name('a').get_attribute('href')
		bizId, duplicate = getBasicBizInfo(bizLink)
		browser.back()
	except:
		print("Couldn't navigate to business page from reviewer profile")
	
	revInfo.insert(1, bizId)
	revID = createReview(revInfo)
	print(f"Created review {revID} from user {userID}'s page")
	addRevsToBiz(bizId, revID, duplicate)
	print(f'Added review {revID} to business {bizId}')
	print(f'Added review {revID} to user {userID}')
	createUser("", userID, revID)

	return revID

#A function to get all reviews from a user's profile according to the conditions stated above
def getUserReviews(userID, client, categories, minNumReviews, locationRadius):
    print(f'\nCURRENT USER: {userID}\n')
    browser.get(retrieve(userID, 1))
    revScraped = len(retrieve(userID, 3).split(' ')) 		#Number of reviews already scraped from this user

    try:
        browser.find_element_by_link_text('Reviews').click()
        reviewerHomePage = browser.current_url

        page = 1

        #This part requires client address to find nearby competitors, so it is impossible to do without the client address
        for category in categories:
            try:
                print(f'Category: {category}')
                browser.get(reviewerHomePage)
                browser.find_element_by_link_text('All Categories').click()
                time.sleep(2)
                try:
                    browser.find_element_by_xpath("//li/a/span[contains(text(), '" + str(category) + "')]").click()
                    nextPage = True

                    while nextPage:
                        numRevs = len(browser.find_elements_by_class_name("review"))
                        print(f'# reviews on pg. {page}: {numRevs}')
                        for r in range(1, numRevs + 1):
                            try:
                                currRev = browser.find_element_by_xpath(f"(//div[@class='review'])[{r}]")
                                print(f'# rev scraped = {revScraped}')
                                alreadyScrapedFromThisUser = getUserBizIDs(userID) #Have to refresh the reviews of this user because it may have increased from previous iteration
                                bizYelpID = currRev.find_element_by_tag_name('a').get_attribute('href').replace('https://www.yelp.com/biz/','').split('?')[0]
                            
                                #If the review for this business from this user isn't already in our database, then we move forward
                                if bizYelpID not in alreadyScrapedFromThisUser:
                                    currentAddr = geolocator.geocode(currRev.find_element_by_tag_name("address").text.split('\n')[1].strip())
                                    print(currentAddr)
                                    current = (currentAddr.latitude, currentAddr.longitude)
                                    far = ceil(dist(current, client).miles)

                                    #If the business is within the x mile radius
                                    if far <= locationRadius:
                                        getRevInfoReviewerPage(currRev, userID)
                                        revScraped += 1
                                    else:
                                        print(f'Attempted review #{revScraped}, too distant: {far} miles')
                                else:
                                    print(f'{bizYelpID} for {userID} was already in the database')
                            except:
                                pass
                        #Try going to next page (if there is one)
                        try:
                            browser.find_element_by_xpath("//span[contains(text(), 'Next')]").click()
                            page += 1
                        except:
                            print(f'Reached end of reviews for {category} for {userID} at page {page}')
                            nextPage = False
                except:
                    print(f'No category {category} found')
            except:
                print(f'Couldn\'t get to All Categories for {userID}')
        print(f'Reached end for CATEGORIZED reviews for {userID}')

        page = 1

        #If the minimum number of reviews haven't been fulfilled for this user
        if revScraped < minNumReviews:
            nextPage = True
            browser.get(reviewerHomePage)
        try:    
            while revScraped < minNumReviews and nextPage:
                numRevs = len(browser.find_elements_by_class_name("review"))
                print(f'# reviews on pg. {page}: {numRevs}')
                for r in range(1, numRevs + 1):
                    try:
                        currRev = browser.find_element_by_xpath(f"(//*[@class='review'])[{r}]")
                        print(f'# rev scraped = {revScraped}')
                        alreadyScrapedFromThisUser = getUserBizIDs(userID)
                        bizYelpID = currRev.find_element_by_tag_name('a').get_attribute('href').replace('https://www.yelp.com/biz/','').split('?')[0]				
                        
                        #Ensure that the business being scraped has not already been scraped for this userp
                        if bizYelpID not in alreadyScrapedFromThisUser:
                            getRevInfoReviewerPage(currRev, userID)
                            revScraped += 1
                        else:
                            print(f'{bizYelpID} for {userID} was already in the database')
                    except:
                        pass
                #Try going to next page (if there is one)
                try:
                    browser.find_element_by_xpath("//span[contains(text(), 'Next')]").click()
                    page += 1
                except:
                    print(f'Reached end of ALL reviews for {userID} at page {page}')
                    nextPage = False
        except:
            print(f'Error while getting UNCATEGORIZED reviews for {userID}')
        print(f'Scraped a total of {revScraped} reviews for {userID}')
        return True
    
    except:
        return False

#MAIN function for PROCESS 2
def process2(clientLink, locationRadius, minNumReviewsPerUser):
    global baseDir
    os.chdir("Database")
    baseDir = os.getcwd()
    clientID = checkDuplicate('b', clientLink.replace('https://www.yelp.com/biz/',"").split('?')[0])
    addr = retrieve(clientID, 3).strip()
    print(addr)
    if addr != "No address found":
        addr = addr.split()
        clientAddr = geolocator.geocode(addr[-1] + ' ' + addr[-2])
        client = (clientAddr.latitude, clientAddr.longitude)
    else:
        print("WARNING: ADDRESS FOR CLIENT BUSINESS NOT STORED ON FILE. PLEASE OPEN B1.txt AND MANUALLY ENTER THE ADDRESS ONTO LINE 4 OF THE FILE.")
        return False
    userIDs = getAllUserIDs()
    categories = retrieve(clientID, 2).split(',')
    for id in userIDs: getUserReviews(id, client, categories, minNumReviewsPerUser, locationRadius)
    browser.quit()
    print('FINISHED PROCESS 2')
    return True