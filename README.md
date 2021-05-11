# GFacil Yelp Scraper

* Check you have Python installed
  * `python --version`
* Check you have pip installed
  * `pip --version`

You will need certain Python modules and Chromedriver to run the scraper.

Python modules:
  * pycryptodome (https://pypi.org/project/pycryptodome/)
    * `pip install pycryptodome`
  * selenium (https://pypi.org/project/selenium/)
    * `pip install selenium`
  * geopy (https://pypi.org/project/geopy/)
    * `pip install geopy`

Chromedriver: https://chromedriver.chromium.org/downloads
  1. Download latest version to match Chrome install
  1. Add `chromedriver.exe` to this folder

Setup in main.py:
  * Windows - comment out `fileIO_linux`
  * Linux - comment out `fileIO`
  * Change numerical parameters.
  * Change password to desired encryption password.
  * Change client link.

Setup in yelp.py:
  * Windows - comment out `fileIO_linux`
  * Linux - comment out `fileIO`

encryption.exe: run through command line with 3 parameters
  1. encrypt/decrypt
  2. absolute path to file
  3. password

 Database folder will be found in same directory as .py files — no need to download template folder anymore.