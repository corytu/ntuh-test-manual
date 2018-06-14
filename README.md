# NTUH Test Manual
A Python web crawler for NTUH clinical test manual

## 簡介
這個repository目的是爬取並整理[臺大醫院檢驗手冊](https://www.ntuh.gov.tw/labmed/檢驗目錄/DocLib/檢驗目錄.aspx)的資料，並輸出成csv檔以便日後存取或查詢。

本次主要使用的套件是`selenium`、`requests`以及`lxml`。前兩者用來模擬瀏覽器、在動態網頁上做出點擊動作，並向伺服器請求資料；後者則用來爬梳、抓取html網頁原始碼內容。[crawler.py](crawler.py)檔案中有整理過後的程式碼。

爬取下來的資料依檢驗類別分類如下（與原網站同），存放於[tests](tests/)子資料夾中：

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

## 系統需求與執行
### 瀏覽器
本次使用Chrome來執行爬取工作，因此若想自行執行本爬蟲程式，電腦中需要安裝Chrome瀏覽器。另外，為使`selenium`能操控Chrome，必須額外下載[chromedriver](https://sites.google.com/a/chromium.org/chromedriver/)並將其放在與crawler.py同一資料夾下。

### 套件
本爬蟲程式目前用到的有：`pandas`、`selenium`、`requests`、`lxml`、`time`、`random`、`re`、`warnings`。須額外安裝的套件請見[requirements.txt](requirements.txt)（使用[`pipreqs`](https://github.com/bndr/pipreqs)自動產生）。

### 啟動
全部安裝後僅須於終端機執行`python crawler.py`即可（我是用Python 3寫的）。程式執行結束時資料夾會多出上述十個csv檔，並關閉Chrome瀏覽器。

## 曾遭遇問題
1. 動態網頁爬取

    與靜態網頁不同，動態網頁（e.g. aspx）無法透過`requests`套件對單一網址請求資料就拿到全部內容，因為當網頁上的「下一頁」被點擊時，是一個Ajax call被傳入，使得新資料被回傳。下列的程式碼就永遠只能抓到`url`第一頁的資料：
    
    ```python
    import requests
    
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
    
    此外，`requests`套件不支援javascript物件，所以在用XPath搜尋物件時，[會少掉一層`tbody`結構](https://github.com/requests/requests/issues/4585)，而且對於不在HTML原始碼的元件，無法透過`requests`+`lxml`取得（[Can't find a td node with id in XPath](https://stackoverflow.com/questions/50763386/cant-find-a-td-node-with-id-in-xpath)）。因此本次最後選擇的解決方案，是透過`selenium`模擬點擊、並即時攔截瀏覽器上的資訊爬取。
    
2. 文字資訊被存在不同的html節點之下（雖然都在`td`之下但位置卻不同）

    解決方式是用`html.fromstring()`取代`etree.fromstring()`爬梳html原始碼，這兩者雖然都在`lxml`套件中，但[前者在爬梳網頁原始碼時更加支援html元件](http://lxml.de/lxmlhtml.html)。再使用`.text_content()`去尋找子結構下的文字內容。參考我在Stack Overflow問的問題：[Search for texts recursively under a td node in an html table](https://stackoverflow.com/questions/49808607/search-for-texts-recursively-under-a-td-node-in-an-html-table)。
