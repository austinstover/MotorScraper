# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 16:41:59 2020

@author: Austin Stover
Date: January 2020
"""

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import csv

csv_file = "hobbyking_bldcs.csv"

hobbykingUrl = "https://hobbyking.com/en_us/power-systems/electric-motors/brushless-motors.html"

def main():
    
    '''
    First make a list of all  urls for brushless motors
    '''
    
    #Open chrome
    driver = webdriver.Chrome('C:\Program Files (x86)\Google\chromedriver.exe') #CHANGE THIS LINE TO DESIRED WEBDRIVER AND LOCATION
    
    #Open up page with list of brushless motors
    driver.get(hobbykingUrl)
    
    motorPgUrls = []
    
    counter = 1
    while(True):
        print("On page", counter)
        counter += 1
        
        #Wait for iframe with product links to load
        element = WebDriverWait(driver, 100).until(lambda x: x.find_element_by_id('instant-search-results-container'))
        
        #Now get the soup!
        soup = BeautifulSoup(driver.page_source, "lxml")
        
        #Find each item
        products = soup.find_all(class_="product-card-box", id=re.compile("list-item"))
        
        
        for product in products:
            #Find the soup with the link in it
            link_soup = product.find('a', class_="algolia-clearfix link -name")
            link = link_soup.get('href')
            motorPgUrls.append(link)  
        
        try: #Find button for next page
            button = driver.find_element_by_link_text('Next page')
            
            try: #Move cursor to button and hit enter to "click" on it
                button.send_keys(Keys.ENTER)
            except StaleElementReferenceException: #Try again if the 1st attempt fails
                try:
                    button.send_keys(Keys.ENTER)
                except StaleElementReferenceException: #Try again if the 2nd attempt fails
                    button.send_keys(Keys.ENTER)
                
        except NoSuchElementException: #Button no longer exists, so we have gotten to the last page
            break
    
    print(motorPgUrls)
    print('Number of motors to analyze:\n', len(motorPgUrls))
    
    driver.quit()
    
    
    '''
    Now to go to and pull data from all the pages
    '''
    
    motorLib = [] #A list of dictionaries containing motors and their specs
    num = 1 #Keep track of which motor we're on
    for url in motorPgUrls:
        try:
            #Open up motor page
            motorPgResult = requests.get(url) #requests.get(motorPgUrls[0])
            #print(motorPgResult.status_code)
            #print(motorPgResult.headers)
            motorPgContent = motorPgResult.content
            motorPgSoup = BeautifulSoup(motorPgContent, "lxml") #Generate page soup
            
            #Find motor name
            prodNameSoup = motorPgSoup.find(class_="product-name mobile-display")
            if(prodNameSoup):
                prodName = prodNameSoup.get_text()
            else:
                prodName = None
            #print("Motor: ", prodNameStr)
            
            #Get price
            prodPriceSoup = motorPgSoup.find(class_="regular-price").find(class_="price")
            if(prodPriceSoup):
                descrStr = prodPriceSoup.get_text()
                match = re.search('\$?([\d\.]+)', descrStr,re.IGNORECASE)
                if(match):
                    price = match[1]
                else:
                    price = None
            else:
                price = None
            
            #Get motor spec table
            specTab = motorPgSoup.find(class_="data-table specifications")
            #print(specTab.prettify())
            
            descrStrRaw = specTab.get_text()
            descrStr = descrStrRaw.replace(" ", "").replace("\xa0", "").lower() #Remove all spaces from motor properties string
            #print(descrStr)
            
            #Get Brand
            match = re.search('brand\n+(.+)', descrStr,re.IGNORECASE)
            if(match):
                brand = match[1] #[1] outputs last paren group, the brand
            else:
                brand = None
            
            #Get Kv
            match = re.search('kv\(rpm/v\)\n+([\d\.]+)', descrStr,re.IGNORECASE)
            if(match):
                kv = float(match[1]) #[1] outputs last paren group
            else:
                kv = None
            
            #Get max current
            match = re.search('maxcurrent\(motor\)\(a\)\n+([\d\.]+)', descrStr,re.IGNORECASE)
            if(match):
                current = float(match[1]) #[1] outputs last paren group
            else:
                current = None
            
            #Get max voltage
            match = re.search('maxvoltage\(v\)\n+([\d\.]+)', descrStr,re.IGNORECASE)
            if(match):
                voltage = float(match[1]) #[1] outputs last paren group
            else:
                voltage = None
            
            #Get max power
            match = re.search('power\(w\)\n+([\d\.]+)', descrStr,re.IGNORECASE)
            if(match):
                power = float(match[1]) #[1] outputs last paren group
            else:
                power = None
            
            #Get mass. This is in the description, not the specs, so it's a bit tricky
            prodDescription = motorPgSoup.find(id="tab-description") #Look in product description
            descrStrRaw = prodDescription.get_text()
            descrStr = descrStrRaw.replace(" ", "").replace("\xa0", "").lower() #Remove all spaces from motor properties string
            motorPropStr = re.split(r'(spec)s?\W', descrStr, maxsplit=1)[-1] #Return only description after specifications begin using regular expressions
            #TODO: If string does not have "spec" in name
            #print(motorPropStr)
            
            massMatch_g = re.search(r'(weight|mass)\W*([\d\.]+)g',motorPropStr)
            massMatch_kg = re.search(r'(weight|mass)\W*([\d\.]+)kg',motorPropStr)
            mass_kg = None #default
            if(massMatch_g): #A match found
                mass_kg = int(massMatch_g[2])/1000
            elif(massMatch_kg):
                mass_kg = int(massMatch_kg[2])
            else:
                mass_kg = None
            
            motorDict = {"name":prodName,
                         "price":price,
                         "brand":brand,
                         "kv":kv,
                         "i_a":current,
                         "v":voltage,
                         "p_w":power,
                         "m_kg":mass_kg
                         }
            motorLib.append(motorDict)
            
            print(num, prodName, "Done")
        except:
            print(num, "Error")
            pass
        num+=1
    
    print()  

    '''
    Now write data to csv
    '''
    
    csv_columns = motorLib[0].keys()
    
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile,delimiter=',',lineterminator='\n',fieldnames=csv_columns)
        writer.writeheader()
        for data in motorLib:
            writer.writerow(data)
    print("Finished!")
    
if __name__ == "__main__":
    main()
