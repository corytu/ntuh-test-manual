# NTUH Test Manual
A Python web crawler for NTUH clinical test manual

## 簡介
這個repository目的是爬取並整理[臺大醫院檢驗手冊](https://www.ntuh.gov.tw/labmed/檢驗目錄/DocLib/檢驗目錄.aspx)的資料，並輸出成csv檔以便日後存取或查詢。

本次主要使用的套件是`selenium`以及`lxml`。前者用來模擬瀏覽器、在動態網頁上做出點擊動作，並向伺服器請求資料；後者則用來爬梳、抓取html網頁原始碼內容。[crawler.py](crawler.py)檔案中有整理過後的程式碼。

爬取下來的資料依檢驗類別分類如下（與原網站同）：
- BC: biochemistry
- SER: serology and immunology
- MO: molecular diagnosis
- HE: hematology
- CT: coagulation
- VI: virology
- BA: bacteriology
- OP: clinical microscopy (out patients)
- CY: cytology
- BK: transfusion and transplantation (blood bank)

目前已完成對每一檢驗項目之基本資料的爬取，並將詳細資料的超連結附於每項之表末，待日後進一步爬取整合（[issue #2](https://github.com/corytu/NTUHTestManual/issues/2)）。

## 系統需求與執行
本次使用Chrome來執行爬取工作，因此若想自行執行本爬蟲程式，電腦中需要安裝Chrome。另外，為使`selenium`能操控瀏覽器，必須額外下載[chromedriver](https://sites.google.com/a/chromium.org/chromedriver/)並將其放在同一資料夾下。之後僅須於終端機執行`python crawler.py`即可。

上述過程於MacOS 10.13.4、Python 3環境下測試無問題。

## 曾遭遇問題
1. 動態網頁爬取

    與靜態網頁不同，動態網頁（e.g. aspx）無法透過`requests`套件對單一網址請求資料就拿到全部內容，因為當網頁上的「下一頁」被點擊時，實際上網址並沒有改變，而是有一個Ajax call被傳入，使得新資料被回傳（這裡研究了好久...）。下列的程式碼就永遠只能抓到`url`第一頁的資料：
    
    ```python
    result = ""
    while result == "":
    try:
        # Certificate is not verified to bypass the SSLError
        # Not secure though
        result = requests.get(url, verify = False)
        break
    except:
        sleep(5)
        continue
    ```
    
    此外，`requests`套件不支援javascript物件，所以在用XPath搜尋物件時，[會少掉一層`tbody`結構](https://github.com/requests/requests/issues/4585)。因此本次最後選擇的解決方案，是透過`selenium`模擬點擊、並即時攔截瀏覽器上的資訊爬取。
    
2. 文字資訊被存在不同的html節點之下（雖然都在`td`之下但位置卻不同，[issue #1](https://github.com/corytu/NTUHTestManual/issues/1)）

    解決方式是用`html.fromstring()`取代`etree.fromstring()`爬梳html原始碼，這兩者雖然都在`lxml`套件中，但[前者在爬梳網頁原始碼時更加支援html元件](http://lxml.de/lxmlhtml.html)。再使用`.text_content()`去尋找子結構下的文字內容。參考我在Stack Overflow問的問題：[Search for texts recursively under a td node in an html table](https://stackoverflow.com/questions/49808607/search-for-texts-recursively-under-a-td-node-in-an-html-table)。
