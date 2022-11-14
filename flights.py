from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import DriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import smtplib

# Dates in this format yyyy/mm/dd
x = "2022-12-10"
y = "2022-12-23"

a = int(x[8:10])
b = int(y[8:10])

if a > b:
	m = a - b
	t = b

else:
	m = b - a
	t = a
print(t)

low_price = ""
url_final = 'https://www.skyscanner.com/flights'
data = {}

for i in range(t, t + m+1):
	url = 'https://www.skyscanner.com/transport/flights/lhe/atla/221210/221223/?adults=1&adultsv2=1&cabinclass=economy&children=0&childrenv2=&destinationentityid=27541735&inboundaltsenabled=false&infants=0&originentityid=27544055&outboundaltsenabled=true&preferdirects=false&ref=home&rtn=1'+str(i)

	#print(url)	
	date = "2022-12-" + str(i)
	
	# enables the script to run without opening browser	(this is unattended mode)
	chrome_options = Options()
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--headless")
	
    # setting path to chromedriver to drive selenium code
	driver = webdriver.Chrome(executable_path = '/home/abu/Documents/flights_web_scrape/Flight-Ticket-Web-Scraping/chrome_tools/chromedriver.exe',
							options=chrome_options)
	
	driver.implicitly_wait(15) # for consistency, waiting for elements to load
	driver.get(url)
	
	g = driver.find_element_by_xpath("//*[@id=\"flights-search-controls-root\"]/div/div/form/div[3]/button")
	price = g.text
	
	x = price[0]
	y = price[2:5]
	z = str(x)+str(y)
	p = int(z)
	print(p)
	
	prices=[]
	if p <= 2000:
		data[date] = p
		
for i in data:
	low_price += str(i) + ": Rs." + str(data[i]) + "\n"
	
print(low_price)