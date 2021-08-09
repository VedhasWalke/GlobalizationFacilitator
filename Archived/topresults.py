from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
browser = webdriver.Chrome()
pages = [["Furniture",["Couch", "Cabinet", "Table"]], ["Mattresses",["Bed", "Dresser", "Set"]]]
for j in range(len(pages)):
    print("\n***** " + pages[j][0] + " - Yelp *****\n")
    browser.get('http://www.yelp.com')
    elem = browser.find_element_by_id('find_desc')
    elem.send_keys(pages[j][0] + Keys.RETURN)
    for i in range(3):
        try:
            link = browser.find_element_by_xpath("(//h3[@class=' heading--h5__09f24__FyKNw undefined'])[2]/ancestor::li" + (i + 1) * "/following-sibling::li" + "//a")
            link.click()
            titlename = browser.title
            stars = browser.find_element_by_xpath("//*[@id='wrap']/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div/div[2]/div[1]/span/div")
            rating = stars.get_attribute("aria-label")
            print('Title: ' + titlename + '\nRating: ' + rating)
            desc = browser.find_element_by_xpath("//span[contains(text(), 'Read more')]")
            desc.click()
        except:
            pass
        try:
            desc2 = browser.find_element_by_xpath("//*[@id='modal-portal-container']/div/div/div/div/div/div[2]//p[1]")
            info = desc2.get_attribute('innerText')
            print('Description: ' + info)
        except:
           pass
        try:
            desc2 = browser.find_element_by_xpath("//*[@id='modal-portal-container']/div/div/div/div/div/div[2]//p[2]")
            info = desc2.get_attribute('innerText')
            print('Description: ' + info)
        except:
            pass
        pass
        browser.back()
for j in range(len(pages)):
    print("\n***** " + pages[j][0] + " - Google *****")
    browser.get('http://www.google.com')
    elem = browser.find_element_by_name('q')
    elem.send_keys(pages[j][0] + Keys.RETURN)
    largest = 0
    best = " "
    for i in range(3):
        try:
            print("\n", end="")
            link = browser.find_element_by_xpath("(//*[@id='rso']/div[@class='g'])[" + str(i + 1) + "]//a")
            desc = browser.find_element_by_xpath("(//*[@id='rso']/div[@class='g'])[" + str(i + 1) + "]/div/div[2]//span[@class='aCOpRe']/span")
            text = desc.get_attribute('innerText')
            link.click()
            titlename = browser.title
            print("Title: " + titlename)
            print("Description: " + text)
        except:
            pass
        try:
            html = browser.page_source
            total = 0
            for k in range(len(pages[j][1])):
                num = html.count(pages[j][1][k])
                print("Occurences of " + pages[j][1][k] + ": " + str(num))
                total += num
            if total > largest:
                largest = total
                best = titlename
            browser.back()
        except:
            pass
    print("\nBest website to look at: " + best + '\n')
browser.quit()
