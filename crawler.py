import pandas as pd
import requests
import re
import random
import warnings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from lxml import html
from time import sleep
warnings.filterwarnings("ignore", "Unverified HTTPS request is being made.")

# Tests include biochemistry, serology, molecular, hematology, coagulation, virology, bacteriology, out-patient, cytology, and blood bank
tests = ["BC", "SER", "MO", "HE", "CT", "VI", "BA", "OP", "CY", "BK"]
# Open Chrome browser
browser = webdriver.Chrome("./chromedriver")

for test in tests:
    test_url = "https://www.ntuh.gov.tw/labmed/檢驗目錄/Lists/2015/{}.aspx".format(test)
    # roughtable = dict(test_ename = [], test_cname = [], specimen = [], reference_range = [], notes = [])
    expected_cols = [
        "test_ename", "test_cname", "ntuh_code", "specimen", "container", "sample_volume", "notice", "sent_condition",
        "taken_at", "operated_at", "turn_around_time", "add_order_before", "replicate_before", "storage_method", "storage_duration",
        "test_method", "reference_range", "interference", "clinical_significance", "nhi_point", "self_paid", "operated_by"
    ]
    detail_table = {col: [] for col in expected_cols}
    # Make the browser visit the page
    browser.get(test_url)
    # Attempt to turn the page 10 times
    for page in range(10):
        print("Crawling: {} tests, page {}".format(test, page+1))
        # Sleep three seconds to let all webpage components be rendered
        sleep(3)
        # Transform what browser gets into an element tree
        item_root = html.fromstring(browser.page_source)
        # Parse the information with Xpath
        for item_row in item_root.xpath("//table[@class='ms-listviewtable']/tbody/tr"):
            # Find text contents recursively in the children of the td node without markup
            # item_texts = [col.text_content().strip() for col in item_row.xpath("./td")]
            # roughtable["test_ename"].append(item_texts[1])
            # roughtable["test_cname"].append(item_texts[3])
            # roughtable["specimen"].append(item_texts[5])
            # roughtable["reference_range"].append(item_texts[6])
            # roughtable["notes"].append(item_texts[7])
            detail_url = item_row.xpath("./td/div/a/@href")[0].strip()
            # roughtable["detail_link"].append(detail_url)
            # Crawl details of the test
            found_id = re.search(r"(?<=ID=)(\d+)", detail_url).group(1)
            detail_url = "https://www.ntuh.gov.tw/labmed/檢驗目錄/Lists/2015/DispForm.aspx?ID={}&Source=https%3A%2F%2Fwww%2Entuh%2Egov%2Etw%2Flabmed%2F%25E6%25AA%25A2%25E9%25A9%2597%25E7%259B%25AE%25E9%258C%2584%2FLists%2F2015%2FBC%2Easpx%23InplviewHash872edfc1%2Dd61c%2D4d08%2D9ca4%2D5ff46206e6b6%3DPaged%253DTRUE%2Dp%5FTitle%253DCA15%25252d3%2Dp%5FID%253D434%2DPageFirstRow%253D51&ContentTypeId=0x01003E4C6DCCAFBEF64BACFA9B88DBDEF416".format(found_id)
            # Keep sending requests while the expected contents are not parsed (for some reasons the return content is not complete every time)
            detail_texts = []
            while len(detail_texts) == 0:
                detail = requests.get(detail_url, verify = False)
                detail_root = html.fromstring(detail.content)
                detail_rows = detail_root.xpath("//table[@id='onetIDListForm']/tr/td/div/div/div/div/table/tr[3]/td/table/tr")
                detail_texts = [row.xpath("./td[2]")[0].text_content().strip() for row in detail_rows]
                # Sleep one to three seconds to prevent frequent requests
                sleep(random.choice(range(1, 3)))
            print("Got: {}".format(detail_texts[0]))
            detail_table["test_ename"].append(detail_texts[0])
            detail_table["test_cname"].append(detail_texts[1])
            detail_table["ntuh_code"].append(detail_texts[2])
            detail_table["specimen"].append(detail_texts[3])
            detail_table["container"].append(detail_texts[6])
            detail_table["sample_volume"].append(detail_texts[7])
            detail_table["notice"].append(detail_texts[8])
            detail_table["sent_condition"].append(detail_texts[9])
            detail_table["taken_at"].append(detail_texts[10])
            detail_table["operated_at"].append(detail_texts[11])
            detail_table["turn_around_time"].append(detail_texts[12])
            detail_table["add_order_before"].append(detail_texts[13])
            detail_table["replicate_before"].append(detail_texts[14])
            detail_table["storage_method"].append(detail_texts[15])
            detail_table["storage_duration"].append(detail_texts[16])
            detail_table["test_method"].append(detail_texts[17])
            detail_table["reference_range"].append(detail_texts[18])
            detail_table["interference"].append(detail_texts[19])
            detail_table["clinical_significance"].append(detail_texts[20])
            detail_table["nhi_point"].append(detail_texts[21])
            detail_table["self_paid"].append(detail_texts[22])
            detail_table["operated_by"].append(detail_texts[23])
        try:
            browser.find_element_by_xpath("//td[@id='pagingWPQ2next']").click()
        except NoSuchElementException:
            # Write the csv and break the for loop if there is no next page
            pd.DataFrame(detail_table)[expected_cols].to_csv("tests/{}.csv".format(test), index = False)
            break
browser.quit()
