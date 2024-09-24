from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

tug_url = "https://online.tugraz.at/tug_online/wbstpcs.showSpoTree?pSJNr=1685&pStpKnotenNr=&pStpStpNr=867&pFilterType=1&pPageNr=&pStartSemester=W"

driver = webdriver.Firefox()
driver.get(tug_url)

elem = driver.find_elements(By.CSS_SELECTOR, "span.KnotenText")

print([e.text for e in elem])

input()

driver.close()