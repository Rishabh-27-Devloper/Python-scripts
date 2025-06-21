from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import sys

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
user_data_dir = Path(r"C:/Users/RajeshShukla/AppData/Local/Google/Chrome/User Data/Profile 1")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
chrome_options.add_argument("--profile-directory=Scraper")

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://web.telegram.org/k/#@Prayas_2_0_JEE_2024_lec")  # Replace with your group link

def scroll_to_top(element, driver, max_tries=100):
    """Scrolls the element to the top."""
    for _ in range(max_tries):
        driver.execute_script("arguments[0].scrollTop = 0;", element)
        time.sleep(0.1)
        # Optionally, break if already at top

def is_on_top(text):
    """Checks if the chat is at the top."""
    lines = text.strip().split('\n')
    if len(lines) > 4 and lines[4] == "1":
        return True
    return False

def main():
    DATA = {}

    # Wait for chat column to load
    wait = WebDriverWait(driver, 30)
    chat = wait.until(EC.presence_of_element_located((By.ID, "column-center")))
    scrollable = chat.find_element(By.CLASS_NAME, "scrollable")

    while True:
        driver.execute_script("arguments[0].scrollBy(0, -100);", scrollable)
        date_groups = chat.find_elements(By.CLASS_NAME, "bubbles-date-group")
        for group in date_groups:
            date = group.find_element(By.CLASS_NAME, "is-date").text.strip()
            messages = group.find_elements(By.CLASS_NAME, "bubble-group")
            for message in messages:
                msg_text = message.text.strip()
                if "-" * 45 in msg_text:
                    print(msg_text.split('\n')[0])
        time.sleep(0.1)
        if is_on_top(chat.text):
            break

    print("Chat Captured")
    print(chat.text)
    input("Press Enter to exit...")
    driver.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        driver.quit()