from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no UI)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the webpage
driver.get("https://forms.hcssapps.com/Forms/Responses")

# Get the fully rendered page source
soup = BeautifulSoup(driver.page_source, "html.parser")

# Find the table
table = soup.find("table")

# Close the browser
driver.quit()

