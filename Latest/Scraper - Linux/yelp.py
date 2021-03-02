import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from geopy.geocoders import Nominatim
from geopy import distance
import fileIO as f
import encryption as e

options = Options()
options.add_argument('--headless')
options.add_argument('--hide-scrollbars')
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")  # fatal
options.add_argument("--start-maximized")

chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

browser = webdriver.Chrome(options=options)
browser.implicitly_wait(7)
wait = WebDriverWait(browser, 10)
dist = distance.distance
geolocator = Nominatim(user_agent="GlobalizationFacilitator")

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
	pathToUL = "/html/body/yelp-react-root/div[1]/div[4]/div/div[1]/div[1]/div[2]/div/ul"
	try:
		ul = browser.find_element_by_xpath(pathToUL).find_elements_by_tag_name("li")
		for elem in range(1, len(ul) + 1):
			if numBiz > 0:
				try:
					newLink = ul[elem].find_element_by_xpath(pathToUL + "/li[" + str(elem) + "]/div/div/div/div[2]/div[1]/div/div[1]/div/div[1]/div/div/h4/span/a").get_attribute('href')
					if not (clientYelpID in newLink):
						links.append(newLink)
						numBiz -= 1
				except:
					pass
	except:
		pass
	
	print(f'Got links for {clientYelpID}')
	return links

#A function to get required attributes of a review
def getRevInfo(revPath, bizID):
	currRev = []
	currReviewer = []
	
	#Append the business ID for which this review was written
	currRev.append(bizID)
	
	#Try getting date of review
	try:
		revDate = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[2]/div/div[2]/span"))).text
	except:
		revDate = "No review date"
	currRev.append(revDate)

	#Try getting rating of review
	try:
		revRating = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[2]/div/div[1]/span/div"))).get_attribute("aria-label").split(" ")[0]
	except:
		revRating = "No rating"
	currRev.append(revRating)

	#Try getting content of review
	try:
		revContent = wait.until(EC.presence_of_element_located((By.XPATH, revPath + '/div[3]/p/span'))).text
	except:
		try:
			revContent = wait.until(EC.presence_of_element_located((By.XPATH, revPath + '/div[4]/p/span'))).text
		except:
			revContent = "No content"
	currRev.append(revContent)

	#Try getting name of reviewer
	try:
		userName = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[1]/div/div[1]/div/div/div[2]/div[1]/span/a"))).text
	except:
		userName = "No reviewer name"
	currReviewer.append(userName)

	#Try getting link to reviewer's profile
	try:
		userLink = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[1]/div/div[1]/div/div/div[2]/div[1]/span/a"))).get_attribute('href')
	except:
		userLink = "No link to reviewer profile"
	currReviewer.append(userLink)

	#Get the reviewer's internal ID
	reviewerID = f.getUserID(currReviewer[1].split('=')[1])
	currRev.insert(0, reviewerID)

	#Get our ID for the new review (returned by this function) while creating the file for the review
	newRevId = f.createReview(currRev)
	print(f'Created review {newRevId}')

	#Create or update a reviewer profile with the new review information
	f.createUser(currReviewer, reviewerID, newRevId)
	print(f'Created user {reviewerID}')

	return newRevId

#A function to get all the reviews for a business
def getAllReviews(bizId):
	nextPage = True
	ids = []
	baseRevPath = '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[1]/div[2]/section[2]/div[2]/div/ul'
	
	while nextPage:
		try:
			revs = len(wait.until(EC.presence_of_element_located((By.XPATH, baseRevPath))).find_elements_by_tag_name("li"))
			for k in range(1, revs + 1):
				ids.append(getRevInfo(baseRevPath + "/li[" + str(k) + "]/div", bizId))
		except:
			pass

		try:
			time.sleep(1)
			pageNums = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[1]/div[2]/section[2]/div[2]/div/div[4]/div[2]'))).text.strip().split(' ')
			pageNums.pop(1)
			if pageNums[0] != pageNums[-1]:
				wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[1]/div[2]/section[2]/div[2]/div/div[4]/div[1]/div'))).find_elements_by_tag_name("div")[-1].click()
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
	bizYelpID = browser.current_url.replace('https://www.yelp.com/biz/','').split('?')[0]
	duplicate = f.checkDuplicate('b', bizYelpID)

	#If the business isn't in the database, scrape the basic info of the business
	if not duplicate:

		# Try getting name of business on Yelp
		try:
			bizName = browser.find_element_by_xpath('//*[@id="wrap"]/div[3]/yelp-react-root/div/div[2]/div[1]/div[1]/div/div/div[1]/h1').text
		except:
			bizName = "No name found"
		currBiz.append(bizName)

		#Try getting rating of business on Yelp
		try:
			bizRating = browser.find_element_by_xpath('//*[@id="wrap"]/div[3]/yelp-react-root/div/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/span/div').get_attribute("aria-label").split(' ')[0]
		except:
			bizRating = "No rating found"
		currBiz.append(bizRating)

		#Try getting categories of business on Yelp
		try:
			bizCategories = browser.find_element_by_xpath('//*[@id="wrap"]/div[3]/yelp-react-root/div/div[2]/div[1]/div[1]/div/div/span[3]').text
		except:
			try:
				bizCategories = browser.find_element_by_xpath('//*[@id="wrap"]/div[3]/yelp-react-root/div/div[2]/div[1]/div[1]/div/div/span[2]').text
			except:
				bizCategories = "No categories found"
		currBiz.append(bizCategories.strip())

		#Try getting location of business on Yelp
		try:
			bizLoc = browser.find_element_by_xpath("//p/a[contains(text(), 'Get Directions')]//following-sibling::p").text.strip()
		except:
			bizLoc = "No address found"
		currBiz.append(bizLoc)

		#Try getting the phone number of business on Yelp
		try:
			bizPh = browser.find_element_by_xpath("//div/p[contains(text(), 'Phone number')]//following-sibling::p").text
		except:
			bizPh = "No phone number found"
		currBiz.append(bizPh)

		#Try getting website of business on Yelp
		try:
			bizWebsite = browser.find_element_by_xpath("//div/p[contains(text(), 'Business website')]//following-sibling::p").text
		except:
			bizWebsite = "No website found"
		currBiz.append(bizWebsite)

		#Try getting description of business on Yelp
		try:
			browser.find_element_by_xpath("//span[contains(text(), 'Read more')]").click()
			bizDesc = browser.find_element_by_xpath("//h5[contains(text(), 'Specialties')]//parent::div//following-sibling::p").text.replace('Specialties','',1).replace('\n','').strip()
			browser.find_element_by_xpath("//span[contains(text(), 'Close')]").click()
		except:
			bizDesc = "No description found"
		currBiz.append(bizDesc)

		#Create a file for the new business in database
		bizId = f.createBiz(currBiz, bizYelpID)
	
	else:
		bizId = duplicate

	print(f'Got basic business info for {bizId}')
	return bizId, duplicate

#A function to get all the required information from a single business
def getAllBizInfo(link):
	basicInfo = getBasicBizInfo(link)
	bizId = basicInfo[0]

	#Go back and add the associated reviews to the business file (parameter 2: generates string of new review IDs from list currBizRevIds)
	f.addRevsToBiz(bizId, str(getAllReviews(bizId)).replace('[','').replace(']','').replace("'","").replace(' ',''), basicInfo[1])
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
		# pass
		
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
		# pass
	
	#Get links from 'people also viewed'
	try:
		allLinks = browser.find_element_by_xpath("//h4[contains(text(), 'People Also Viewed')]//parent::div//parent::div//following-sibling::div").find_elements_by_tag_name("a")
		for i in range(len(allLinks)):
			if not (i + 1) % 2:
				finalCompetitors.append(allLinks[i].get_attribute('href'))
	except:
		print("Unable to find link to also searched businesses")
		# pass

	bizes = []
	for competitor in finalCompetitors:
		browser.get(competitor)
		bizes.append(browser.current_url.split('?')[0])

	print(f'Got list of competitors for business {clientYelpID}')
	return set(bizes)

#A function that will scrape info from all direct competitors
def getAllCompetitorsInfo(bizList):
	scrapedBiz = []
	for i in bizList:
		scrapedBiz.append(getAllBizInfo(i))
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
        revContent = reviewElementIndex.find_elements_by_tag_name('p')[0].text
    except:
        revContent = "No content"
    revInfo.append(revContent)

    #Scrape the business info
    try:
        bizLink = reviewElementIndex.find_elements_by_tag_name('a')[1].get_attribute('href')
        bizId = getBasicBizInfo(bizLink)[0]
        browser.back()
    except:
        print("Couldn't navigate to business page from reviewer profile")
    revInfo.insert(1, bizId) #Got the BizID after creating business, insert and then create review
    revID = f.createReview(revInfo)
    print(f"Created review {revID} from user {userID}'s page")

    f.addRevsToBiz(str(bizId), str(revID), getBasicBizInfo(bizLink)[1])
    print(f'Added review {revID} to business {bizId}')

    print(f'Added review {revID} to user {userID}')
    f.createUser("", str(userID), str(revID))

    return revID

#A function to get all reviews from a user's profile according to the conditions stated above
def getUserReviews(userID, clientID, minNumReviews, locationRadius):
	browser.get(f.retrieve(userID.strip(), 1))
	categories = f.retrieve(clientID, 2).split(',')
	revScraped = len(f.retrieve(userID, 3).split(',')) 		#Number of reviews already scraped from this user

	browser.find_element_by_link_text('Reviews').click()
	reviewerHomePage = browser.current_url
	clientAddr = geolocator.geocode(f.retrieve(clientID, 3).strip().split(' ')[-1] + ' ' + f.retrieve(clientID, 3).strip().split(' ')[-2])
	print(f.retrieve(clientID, 3).strip().split(' ')[-1] + ' ' + f.retrieve(clientID, 3).strip().split(' ')[-2], clientAddr)
	client = (clientAddr.latitude, clientAddr.longitude)

	page = 1

	for category in categories:
		print(category)
		browser.get(reviewerHomePage)
		browser.find_element_by_link_text('All Categories').click()
		time.sleep(2)
		try:
			browser.find_element_by_xpath("//div/div/div/ul//*[contains(text(),'" + str(category) + "')]").click()
			nextPage = True

			while nextPage:
				numRevsOnCurrPage = len(browser.find_elements_by_class_name("review"))
				for r in range(numRevsOnCurrPage):
					reviews = browser.find_elements_by_class_name("review")
					alreadyScrapedFromThisUser = f.getUserBizIDs(userID) #Have to refresh the reviews of this user because it may have increased from previous iteration
					bizYelpID = reviews[r].find_elements_by_tag_name('a')[1].get_attribute('href').replace('https://www.yelp.com/biz/','').split('?')[0]
				
					#If the review for this business from this user isn't already in our database, then we move forward
					if bizYelpID not in alreadyScrapedFromThisUser:
						currentAddr = geolocator.geocode(reviews[r].find_element_by_tag_name("address").text.split('\n')[1].strip())
						print(currentAddr)
						current = (currentAddr.latitude, currentAddr.longitude)
						far = dist(current, client).miles

						#If the business is within the x mile radius
						if float(far) <= locationRadius:
							getRevInfoReviewerPage(reviews[r], userID)
							revScraped += 1
						else:
							print(f'Attempted review #{revScraped}, too distant: {far} miles')
					
					else:
						print(f'{bizYelpID} for {userID} was already in the database')

				#Try going to next page (if there is one)
				try:
					browser.find_element_by_xpath("//span[contains(text(), 'Next')]").click()
					page += 1
				except:
					print(f'Reached end of reviews for {category} for {userID} at page {page}')
					nextPage = False
		except:
			print(f'No category {category} found')

	#If the minimum number of reviews haven't been fulfilled for this user
	if revScraped < minNumReviews:
		nextPage = True
		browser.get(reviewerHomePage)

		while revScraped < minNumReviews and nextPage:
			numRevsOnCurrPage = len(browser.find_elements_by_class_name("review"))
			for r in range(numRevsOnCurrPage):
				reviews = browser.find_elements_by_class_name("review")
				bizYelpID = reviews[r].find_elements_by_tag_name('a')[1].get_attribute('href').replace('https://www.yelp.com/biz/','').split('?')[0]					
				alreadyScrapedFromThisUser = f.getUserBizIDs(userID)
				
				#Ensure that the business being scraped has not already been scraped for this userp
				if bizYelpID not in alreadyScrapedFromThisUser:
					getRevInfoReviewerPage(reviews[r], userID)
					revScraped += 1
				else:
					print(f'{bizYelpID} for {userID} was already in the database')
			
			#Try going to next page (if there is one)
			try:
				browser.find_element_by_xpath("//span[contains(text(), 'Next')]").click()
				page += 1
			except:
				print(f'Reached end of reviews for {userID} at page {page}')
				nextPage = False
	
	return True

#MAIN function for PROCESS 2
def process2(clientLink, locationRadius, minNumReviewsPerUser):
	clientID = f.checkDuplicate('b', clientLink.replace('https://www.yelp.com/biz/',"").split('?')[0])
	userIDs = f.getAllUserIDs()
	for id in userIDs:
		getUserReviews(id, clientID, minNumReviewsPerUser, locationRadius)
	browser.quit()

	print('FINISHED PROCESS 2')
	return True
	
############################################# 	END OF IMPORTANT FUNCTIONS	#############################################




#[not in use] A function to search Yelp for a certain good/service in a location
def searchYelp(goods, numResults, location=""):

	#Search yelp for passed product/service and area
	
	#Go to Yelp homepage
	try:
		browser.get("https://www.yelp.com/")
	except:
		print("Can't open Yelp website")

	#Search for passed good/service
	try:
		searchBar = wait.until(EC.presence_of_element_located((By.ID, "find_desc")))
		searchBar.clear()
		searchBar.send_keys(goods)
	except:
		print("Can't find search bar")

	#Send preferred location, defaults to auto-detected location
	try:
		locationBar = wait.until(EC.presence_of_element_located((By.ID, "dropperText_Mast")))
		locationBar.clear()
		locationBar.send_keys(location + Keys.RETURN)
	except:
		print("Can't find location bar")

	links = getLinks(numResults)

	#Scrape top businesses for product; the links to these businesses have already been stored by the getBizLinks() function
	for i in range(numResults):
		getAllBizInfo(links[i])

	return True
