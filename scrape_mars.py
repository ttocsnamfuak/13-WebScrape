
# Dependencies
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import os
import time
import pandas as pd
from splinter import Browser
import pymongo


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    # executable_path = {"executable_path": "./chromedriver"}
    return Browser("chrome", headless=False)


def scrape():
    browser = init_browser()
    #listings = {}

    # Get Mars Headlines

    url = 'https://mars.nasa.gov/news'

    # scrape web page
    chromedriver = "/usr/local/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    
    # Create soup object
    soup = BeautifulSoup(html, 'lxml')

    # results are returned as an iterable list
    results = soup.find_all('li', class_="slide")

    # find text as a list from all 'a' tags in first/latest news
    text = results[0].find_all('a')

    # find news title
    news_title = text[1].text

    # find news paragraph
    news_p = text[0].find('div', class_="rollover_description_inner").text  

    # print out results to server console to see it worked
    print(f"Title: {news_title}")
    print("---------")
    print(f"Paragraph: {news_p}")  


    # Get Mars images

    # # config chromedriver and generate browser object
    # executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    # browser = Browser('chrome', **executable_path, headless=False)

    # open the web page using browser - specific for mars images
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars#submit'
    browser.visit(url)
        
    # Click the 'Full Image' button
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)

    # Click the 'more info' button
    browser.click_link_by_partial_text('more info')

    # generate link found object
    links_found = browser.find_link_by_partial_href('images/largesize')

    # find link to the feature image
    featured_image_url = links_found['href']

    # print link to check
    print(featured_image_url)

    # Mars weather

    # URL of page to be scraped
    url = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    response = requests.get(url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')

    # results are returned as an iterable list
    results = soup.find_all('div', class_="js-tweet-text-container")

    # find weather text, assign to a variable
    mars_weather = results[0].find('p').text

    # print to server console
    print(mars_weather) 


    # Mars Facts to Pandas

    # url
    url = 'https://space-facts.com/mars/'

    # scrape tables using Pandas read_html function
    tables = pd.read_html(url)

    # assign target table to a data frame
    mars_df = tables[0]

    # generate html table string using Pandas
    html_table = mars_df.to_html(header=None,index=False)

    # replace line breaks
    html_table = html_table.replace('\n', '')

    # Hemisphere data-image urls

    # generate empty list
    hemisphere_image_urls =[]

    # define a function to scrape full resolution image link using splinter
    def find_hemisperes(name):
        browser = Browser('chrome', headless=False)
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
        browser.click_link_by_partial_text(name)
        links_found = browser.find_link_by_partial_href(name.split()[0].lower())
        url = links_found['href']
        dic = {"title": f"{name} Hemisphere", "img_url": url}
        hemisphere_image_urls.append(dic)
        browser.quit()
        
    # Mars hemisperes
    hemisperes_list = ['Cerberus', 'Schiaparelli', 'Syrtis Major', 'Valles Marineris']

    # loop through above list and scrape information
    for hemispere in hemisperes_list:
        find_hemisperes(hemispere)

    # urls to console
    print(hemisphere_image_urls)


    # Save results in dictionary into Mongo
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    db = client.app

    # drop marsNews collection if it exists
    db.marsNews.drop()

    db.marsNews.insert(
        [
            {
                "newsTitle": news_title,
                "newsPara": news_p,
                "imageod":  featured_image_url,
                "weather": mars_weather,
                "mFacts": html_table,
                "hemi1Image": hemisphere_image_urls[0]['img_url'],
                "hemi1Title": hemisphere_image_urls[0]['title'],
                "hemi2Image": hemisphere_image_urls[1]['img_url'],
                "hemi2Title": hemisphere_image_urls[1]['title'],
                "hemi3Image": hemisphere_image_urls[2]['img_url'],
                "hemi3Title": hemisphere_image_urls[2]['title'],
                "hemi4Image": hemisphere_image_urls[3]['img_url'],
                "hemi4Title": hemisphere_image_urls[3]['title']
            }
        ]
    )
    # Print to console that the insert worked
    print("Database populated")

    #Generate dictionary to pass to html
    mars_dict = {"newsTitle": news_title,
            "newsPara": news_p,
            "imageod":  featured_image_url,
            "weather": mars_weather,
            "mFacts": html_table,
            "hemi1Image": hemisphere_image_urls[0]['img_url'],
            "hemi1Title": hemisphere_image_urls[0]['title'],
            "hemi2Image": hemisphere_image_urls[1]['img_url'],
            "hemi2Title": hemisphere_image_urls[1]['title'],
            "hemi3Image": hemisphere_image_urls[2]['img_url'],
            "hemi3Title": hemisphere_image_urls[2]['title'],
            "hemi4Image": hemisphere_image_urls[3]['img_url'],
            "hemi4Title": hemisphere_image_urls[3]['title']
            }



    # # url = "https://raleigh.craigslist.org/search/hhh?max_price=1500&availabilityMode=0"
    # # browser.visit(url)
    # # #time.sleep(1)
    # # html = browser.html
    # # soup = BeautifulSoup(html, "html.parser")

    # page1_results = soup.find_all("li", {"class":"result-row"})

    # def parse_result(result):
    #     output = {"headline":"","price":"","hood":""}
    #     if(result.find("a", {"class":"result-title"})): output['headline'] = result.find("a", {"class":"result-title"}).text
    #     if(result.find("span", {"class":"result-price"})): output['price'] = result.find("span", {"class":"result-price"}).text
    #     if(result.find("span", {"class":"result-hood"})): output['hood'] = result.find("span", {"class":"result-hood"}).text
    #     return output

    # page1_listings = [parse_result(x) for x in page1_results]

    # browser.click_link_by_partial_text("next")

    # page2_results = soup.find_all("li", {"class":"result-row"})
    # page2_listings = [parse_result(x) for x in page1_results]

    listings = mars_dict

    return listings
