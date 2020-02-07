from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import pandas as pd
import time

# Load and clean up locations, one representing address per neighbourhood in Totonto
#   (entry 'Maple Leaf' & 'Rouge' miss addresses)
df=pd.read_csv('locations.csv', encoding='iso-8859-1') \
     .drop(columns=['Hood #'])
df=df.loc[:, ~df.columns.str.contains('^Unnamed')]
df=df.drop(df.index[df['Repr Addr'].isna()]).reset_index().drop(columns=['index'])
# Row 128's address contains "#10" invalidated by UberEats address search. Thus modify 
#   "3025 Kennedy Rd #10, Toronto, ON M1V 1S7, Canada" into
#   "3025 Kennedy Rd, Toronto, ON M1V 1S7, Canada"
err_ind=df.index[df['Repr Addr'].str.contains('#')][0] 
df['Repr Addr'][err_ind]=df['Repr Addr'][err_ind][:15]+df['Repr Addr'][err_ind][19:]
# Row 25's address contains "Unit 1" invalidated by UberEats address search. Thus modify
#   "2943 Major MacKenzie Dr W Unit 1, Maple, ON L6A 1C6, Canada" into
#   "2943 Major MacKenzie Dr W, Maple, ON L6A 1C6, Canada"
err_ind=df.index[df['Repr Addr'].str.contains('Unit 1')][0]
df['Repr Addr'][err_ind]=df['Repr Addr'][err_ind][:25]+df['Repr Addr'][err_ind][32:]

# Add options for the Chrome browser.
options=webdriver.ChromeOptions()
options.binary_location='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
options.add_argument('--diable-extensions')
options.add_argument('--diable-gpu')
options.add_argument('--incognito')
# Run the Chrome browser.
driver=webdriver.Chrome(chrome_options=options)

for addr in df['Repr Addr'][110:]:
  print(addr)
  # Navigate to "www.ubereats.com".
  driver.get("https://www.ubereats.com")
  # Wait for the address search bar to become clickable, and click it. 
  search_bar=WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                   "//input[@id='location-typeahead-home-input']")))
  search_bar.click()
  # Input target address into search bar. Sometimes the input get truncated or cleared
  #   as webpage refreshes during loading, thus we make 3 attempts to input the target
  #   address, interleaving with 1 second of wait time.
  for i in range(3):
    time.sleep(1)
    if(search_bar.get_attribute('value')==addr): None
    else:
      AC(driver).key_down(Keys.COMMAND).send_keys('a').send_keys(Keys.DELETE)
      search_bar.send_keys(addr) 
  # Press return after inputting target address in to address search bar. Page jumps.
  search_bar.send_keys(Keys.RETURN)
  # Wait for all the listing figures in the page to become visible.
  figures = WebDriverWait(driver, 120).until(EC.visibility_of_all_elements_located((By.XPATH, 
                                                                 "//figure[@height='240']")))
  # Keep clicking "Show more" until no more new figures appear.
  while True:
    L=len(figures)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                        "/html/body/div/div/div[3]/button"))).click()
    time.sleep(4)
    figures=WebDriverWait(driver, 120).until(EC.visibility_of_all_elements_located(
                                            (By.XPATH, "//figure[@height='240']")))
    if(len(figures)>L): None
    else: break
  # Get all the listings when no more new listings show up by clicking "Show more". 
  listings = driver.find_elements_by_xpath("//figure[@height='240']/ancestor::a")
  # Create output file with the name being the Hood Name. 
  filename = "UberEats_Crawler_Output/" + df['Hood Name'][df.index[df['Repr Addr']==addr].values[0]]
  output = open(filename,'w+')
  # For each listing, scrape its text information and link for details page
  for l in listings:
    info1 = l.text.replace("\n", ";")
    info2 = l.get_attribute('href')
    print(info1 + '\n' + info2 + '\n', file=output)
    print(info1 + '\n' + info2 + '\n')
  driver.delete_all_cookies()
driver.close()