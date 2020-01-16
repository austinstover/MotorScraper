# MotorScraper
Scrapes Hobbyking for brushless motor (BLDC) properties. Records the name, price, brand, mass, Kv, max power, max current, and max voltage for almost all BLDCs listed on the Hobbyking website.

Functions correctly as of January 2020. Make sure to change the line `driver = webdriver.Chrome('C:\Program Files (x86)\Google\chromedriver.exe')` to whichever webdriver you use and its install path (see [Selenium documentation](https://selenium-python.readthedocs.io/faq.html#how-to-use-chromedriver) for more details).

**Required Packages and Programs:**
  - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
  - [Selenium for Python](https://selenium-python.readthedocs.io/installation.html)
  - [A Selenium Webdriver](https://selenium-python.readthedocs.io/installation.html#drivers)
