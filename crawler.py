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
    item_url = "https://www.ntuh.gov.tw/labmed/檢驗目錄/Lists/2015/{}.aspx".format(test)
    roughtable = dict(test_ename = [], test_cname = [], specimen = [], reference_range = [], notes = [], detail_link = [])
    # Make the browser visit the page
    browser.get(item_url)
    # Attempt to turn the page 10 times
    for page in range(10):
        print("Crawling: {} tests, page {}".format(test, page+1))
        # Sleep three seconds to prevent unexpected errors
        sleep(3)
        # Transform what browser gets into an element tree
        item_root = html.fromstring(browser.page_source)
        # Parse the information with Xpath
        for item_row in item_root.xpath("//table[@class='ms-listviewtable']/tbody/tr"):
            # Find text contents recursively in the children of the td node without markup
            item_texts = [col.text_content() for col in item_row.xpath("./td")]
            roughtable["test_ename"].append(item_texts[1].strip())
            roughtable["test_cname"].append(item_texts[3].strip())
            roughtable["specimen"].append(item_texts[5].strip())
            roughtable["reference_range"].append(item_texts[6].strip())
            roughtable["notes"].append(item_texts[7].strip())
            detail_url = item_row.xpath("./td/div/a/@href")[0].strip()
            roughtable["detail_link"].append(detail_url)
        try:
            browser.find_element_by_xpath("//td[@id='pagingWPQ2next']").click()
        except NoSuchElementException:
            # Write the csv and break the for loop if there is no next page
            pd.DataFrame(roughtable)[["test_ename", "test_cname", "specimen", "reference_range", "notes", "detail_link"]].to_csv("{}.csv".format(test), index = False)
            break
browser.quit()
