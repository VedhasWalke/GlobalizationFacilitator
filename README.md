# GlobalizationFacilitator Yelp Scraper

Python modules:
  pycrypto (https://pypi.org/project/pycrypto/)
  selenium (https://pypi.org/project/selenium/)
  geopy (https://pypi.org/project/geopy/)
  Make sure to download latest version of Chomedriver and add to path
  
Setup in main.py:
  Windows - comment out fileIO_linux
  Linux - comment out fileIO
  Change numerical parameters.
  Change password to desired encryption password.
  Change client link.

Setup in yelp.py:
  Windows - comment out fileIO_linux
  Linux - comment out fileIO

Database folder will be found in same directory as .py files — no need to download template folder anymore.

encryption.exe:
  Run through command line with 3 parameters - 
    1. encrypt/decrypt
    2. absolute path to file
    3. password