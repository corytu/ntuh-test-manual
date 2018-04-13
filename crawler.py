import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from lxml import html
from time import sleep

# Tests include biochemistry, serology, molecular, hematology, coagulation, virology, bacteriology, out-patient, cytology, and blood bank
tests = ["BC", "SER", "MO", "HE", "CT", "VI", "BA", "OP", "CY", "BK"]
# Open Chrome browser
browser = webdriver.Chrome("./chromedriver")

for test in tests:
    url = "https://www.ntuh.gov.tw/labmed/檢驗目錄/Lists/2015/{}.aspx".format(test)
    roughtable = dict(test_ename = [], test_cname = [], specimen = [], reference_range = [], notes = [], detail_link = [])
    # Make the browser visit the page
    browser.get(url)
    sleep(3)
    # Attempt to turn the page 10 times
    for i in range(10):
        # Transform what browser gets into an element tree
        root = html.fromstring(browser.page_source)
        # Parse the information with Xpath
        for row in root.xpath("//table[@class='ms-listviewtable']/tbody/tr"):
            # Find text contents recursively in the children of the td node without markup
            texts = [col.text_content() for col in row.xpath("./td")]
            roughtable["test_ename"].append(texts[1].strip())
            roughtable["test_cname"].append(texts[3].strip())
            roughtable["specimen"].append(texts[5].strip())
            roughtable["reference_range"].append(texts[6].strip())
            roughtable["notes"].append(texts[7].strip())
            roughtable["detail_link"].append(row.xpath("./td/div/a/@href")[0].strip())
        try:
            browser.find_element_by_xpath("//td[@id='pagingWPQ2next']").click()
            sleep(3)
        except NoSuchElementException:
            # Write the csv and break the for loop if there is no next page
            pd.DataFrame(roughtable)[["test_ename", "test_cname", "specimen", "reference_range", "notes", "detail_link"]].to_csv("{}.csv".format(test), index = False)
            break
browser.quit()
