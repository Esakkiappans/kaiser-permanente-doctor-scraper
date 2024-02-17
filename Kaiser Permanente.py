from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

def locate_element_with_retry(driver, locator, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            return driver.find_element(*locator)
        except StaleElementReferenceException:
            attempts += 1
            print("Stale Element Reference Exception occurred. Retrying...")
    raise NoSuchElementException("Element could not be located after multiple attempts")

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Optional: Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Optional: Bypass OS security model
chrome_options.add_argument("--disable-logging")  # Disable logging
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

try:
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    driver.get("https://healthy.kaiserpermanente.org/northern-california/doctors-locations#/providers")
    driver.implicitly_wait(30) 
    page_count = 1
    header_printed = False 
    all_datas = ''
    if page_count<10:
        while True:
            print(f"Scraping doctors from page {page_count}")

            doctor_elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="kp-spa-root"]/provider-results/div/div/div[3]/div[2]/div/div[1]/div[1]/div')))

            for i in range(len(doctor_elements)):
                doctor_element = locate_element_with_retry(driver, (By.XPATH, f'//*[@id="kp-spa-root"]/provider-results/div/div/div[3]/div[2]/div/div[1]/div[1]/div[{i+1}]'))
                doctor_info = doctor_element.text.split('\n')
                if not header_printed: 
                    print("Name, Specialty, Center,Address,phone_number,accepting,plans_accepted")
                    header_printed = True
                name = doctor_info[0]
                specialty = doctor_info[1]
                center = doctor_info[2]
                address = ', '.join(doctor_info[3:5])
                contact = doctor_info[5]
                phone_number = contact.split()[-1] if "Directions" in contact else "N/A"
                accepting = doctor_info[6]
                plans_accepted = doctor_info[7]
                all_datas += f"name : {name}, specialty :{specialty}, center :{center}, address :{address}, phone_number: {phone_number}, accepting :{accepting}, plans_accepted :{plans_accepted}\n"
                print(all_datas)
            try:
                driver.implicitly_wait(30)
                next_button = WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="pagination-example"]/nav/ul/li[11]/span/a/span[2]')))
                driver.execute_script("arguments[0].click();", next_button)
            except NoSuchElementException:
                print("No more pages to navigate.")
                break

            page_count += 1
            with open("all_data.txt", "w") as file:
                file.write(all_datas)

except Exception as e:
    print("An error occurred:", e)

# Quit the driver
driver.quit()
