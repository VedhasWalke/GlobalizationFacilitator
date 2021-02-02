######################################IMPORTS##########################################################

from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import find_connectable_ip
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
import time
import os
import csv

#########################################SETUP##########################################################

pages = ["Books", "Groceries", "Coffee", "Dinner"] #Categories to scrape
numBusinessesToScrapePerPage = 5 #Number of businesses to scrape per category
numReviewsToScrapePerBusiness = 3 #Number of reviews to scrape per business

fields = ['Name', 'Rating', 'Location', 'Ph#', 'Website', 'Reviews', 'Description'] #Data to scrape from each business
#Title, Rating, Location, Ph#, Website, Description: string
#Reviews: list of dicts

revAtts = ['Reviewer', 'Date', 'Rating', 'Content', 'Link to Reviewer Profile'] #Data to scrape from each review
final = {}

chromedriver = "/Users/Yuvi/Documents/Learning/Coding/Python/chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
browser = webdriver.Chrome(chromedriver)
browser.implicitly_wait(5)
wait = WebDriverWait(browser, 10)
browser.maximize_window()

######################################FUNCTIONS##########################################################
#A function for writing scraped data to a .txt
def writeToFile(fName, obj=""):
    try:
        with open(fName+'.txt', 'w') as out:
            for k,v in obj.items():
                out.write(f'{k}: {v}')
                out.write('\n')
        return True
    except:
        pass
    return False

#A function to search Yelp for a certain good/service in a location
def searchYelp(goods="", location=""):

    #Go to Yelp homepage
    time.sleep(5)
    try:
        browser.get("https://www.yelp.com/")
    except:
        print("Can't open Yelp website")

    #Search for passed good/service
    try:
        searchBar = wait.until(EC.presence_of_element_located((By.ID, "find_desc")))
        searchBar.send_keys(goods)
    except:
        print("Can't find search bar")

    #Send preferred location, defaults to auto-detected location
    try:
        locationBar = wait.until(EC.presence_of_element_located((By.ID, "dropperText_Mast")))
        locationBar.send_keys(location + Keys.RETURN)
    except:
        print("Can't find location bar")

#A function to get the links for each business on page
def getBizLinks(numBiz=3):
    links = []
    pathToUnorderedList = "/html/body/yelp-react-root/div[1]/div[4]/div/div[1]/div[1]/div[2]/div/ul"
    limit = 0
    try:
        ul = browser.find_element_by_xpath(pathToUnorderedList).find_elements_by_tag_name("li")
        for elem in range(1, len(ul) + 1):
            if limit < numBiz:
                try:
                    currBizPath = pathToUnorderedList + "/li[" + str(elem) + "]/div/div/div/div[2]/div[1]/div/div[1]/div/div[1]/div/div"
                    link = ul[elem].find_element_by_xpath(currBizPath + "/h4/span/a").get_attribute('href')
                    limit += 1
                    links.append(link)
                except:
                    pass
            else:
                pass
    except:
        pass
    return links

#A function to get the name of a business
def getBizName():
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[2]/div[1]/div[1]/div/div/div[1]/h1'))).text
    except:
        pass
    return "No name found"

#A function to get the rating of a business
def getBizRating():
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/span/div'))).get_attribute("aria-label")
    except:
        pass
    return "No rating found"

#A function to get the address information of a business
def getBizLoc():
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[2]/div/div/section[1]/div/div[3]/div/div[1]/p/p'))).text
    except:
        pass
    return "No address found"

#A function to get the phone number of a business
def getBizPh():
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[2]/div/div/section[1]/div/div[2]/div/div[1]/p[2]'))).text
    except:
        pass
    return "No phone number found"

#A function to get the link to the website of the business
def getBizSite():
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[2]/div/div/section[1]/div/div[1]/div/div[1]/p[2]/a'))).text
    except:
        pass
    return "No website found"

#A function to get the description for a business
def getBizDesc():
    try:
        desc = ""
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="wrap"]/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[1]/section[5]/div[2]/button/div/span'))).click()
        container = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal-portal-container"]/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div'))).find_elements_by_tag_name("p")
        for p in container:
            desc += (p.text + " ")
        return desc
    except:
        pass
    return "No description found"

#A function to get the name of the reviewer
def getReviewerName(revPath):
    try:
        name = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[1]/div/div[1]/div/div/div[2]/div[1]/span/a"))).get_attribute('innerText')
        return name
    except:
        pass
    return "No reviewer name"  

#A function to get the date of the review
def getRevDate(revPath):
    try:
        date = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[2]/div/div[2]/span"))).get_attribute('innerText')
        return date
    except:
        pass
    return "No review date"

#A function to get the rating of the review
def getRevRating(revPath):
    try:
        revRating = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[2]/div/div[1]/span/div"))).get_attribute("aria-label")
        return revRating
    except:
        pass
    return "No rating"

#A function to get the content of the review
def getRevContent(revPath):
    try:
        content = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "//p/span"))).get_attribute("innerText")
        return content
    except:
        pass
    return "No content"

#A function to get the link to the reviewer's profile
def getReviewerLink(revPath):
    try:
        reviewerLink = wait.until(EC.presence_of_element_located((By.XPATH, revPath + "/div[1]/div/div[1]/div/div/div[2]/div[1]/span/a"))).get_attribute('href')
        return reviewerLink
    except:
        pass
    return "No link to reviewer profile"

#A function to get required attributes of a review for a business
def getRevInfo(revPath):
    currRev = {}
    currRevAttr = 0

    #Try getting name of reviewer
    currRev[revAtts[currRevAttr]] = getReviewerName(revPath)
    currRevAttr += 1

    #Try getting date of review
    currRev[revAtts[currRevAttr]] = getRevDate(revPath)
    currRevAttr += 1

    #Try getting rating of review
    currRev[revAtts[currRevAttr]] = getRevRating(revPath)
    currRevAttr += 1
    
    #Try getting content of review
    currRev[revAtts[currRevAttr]] = getRevContent(revPath)
    currRevAttr += 1
    
    #Try getting link to reviewer's profile
    currRev[revAtts[currRevAttr]] = getReviewerLink(revPath)
    currRevAttr += 1

    return currRev

#A function to get all the required information from a single business - needs link to site & list of fields
def getBizInfo(link, fields, numRevsPerBiz):
    currBiz = {} #Temporary dict for storing current business info
    currField = 0 #For mapping key-value pairs for each field of business info

    browser.get(link) #Load business page

    # Try getting name of business on Yelp
    currBiz[fields[currField]] = getBizName()
    currField += 1

    #Try getting rating of business on Yelp
    currBiz[fields[currField]] = getBizRating()
    currField += 1

    #Try getting location of business on Yelp
    currBiz[fields[currField]] = getBizLoc()
    currField += 1

    #Try getting the phone number of business on Yelp
    currBiz[fields[currField]] = getBizPh()
    currField += 1

    #Try getting website of business on Yelp
    currBiz[fields[currField]] = getBizSite()
    currField += 1

    #Try getting top reviews of business on Yelp
    currBizRevs = []
    for k in range(1, numRevsPerBiz + 1):
        try:
            currRevPath = "//*[@id='wrap']/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div[1]/div[2]/section[2]/div[2]/div/ul/li[" + str(k) + "]/div"
            currBizRevs.append(getRevInfo(currRevPath))
        except:
            currBizRevs.append("Could not get reviews")
    currBiz[fields[currField]] = currBizRevs
    currField += 1

    #Try getting description of business on Yelp
    currBiz[fields[currField]] = getBizDesc()
    currField += 1

    writeToFile(".\\Biz\\"+currBiz['Name'], currBiz)
    return currBiz
    
#A function for printing deep-nested dicts with lists in a somewhat organized and visually pleasing format
def dumpclean(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print(v)
    else:
        print(obj)

##################################RUN###########################################

#Main function
def main():
    for i in range(len(pages)):
        #Search Yelp for current page/category
        searchYelp(pages[i])

        currPage = []
        
        links = getBizLinks(numBusinessesToScrapePerPage)
        
        #Scrape top businesses per product; the links to these businesses have already been stored by the getBizLinks() function
        for j in range(numBusinessesToScrapePerPage):
            currPage.append(getBizInfo(links[j], fields, numReviewsToScrapePerBusiness))
        final[pages[i]] = currPage

    browser.quit()
    writeToFile("final", final)
    dumpclean(final)
    return

if __name__ == '__main__':
    main()