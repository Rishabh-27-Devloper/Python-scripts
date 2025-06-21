# Telegram Chat Scraper

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Automation-green)
![ChromeDriver](https://img.shields.io/badge/ChromeDriver-Required-red)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A simple Python-based automation script to **scrape Telegram chat messages** from the official Telegram web client using Selenium WebDriver. This is useful for archiving or analyzing chat history from a group or channel.

---

## Features

* Uses an existing Chrome profile to avoid manual login.
* Scrolls to the top of the chat to extract full history.
* Captures and prints specific messages based on content pattern.

---

## Requirements

* Python 3.10 or above
* Google Chrome (installed)
* [ChromeDriver](https://chromedriver.chromium.org/downloads) (compatible with your Chrome version)
* Python libraries:

  ```bash
  pip install selenium
  ```

---

## Setup

1. **Clone or download** the repository.

2. Update the `user_data_dir` and `--profile-directory` in the script:

   ```python
   user_data_dir = Path(r"C:/Users/YourUsername/AppData/Local/Google/Chrome/User Data/Profile 1")
   chrome_options.add_argument("--profile-directory=Scraper")
   ```

   This avoids needing to re-login every time.

3. Replace the Telegram group URL:

   ```python
   driver.get("https://web.telegram.org/k/#@GroupUsername")
   ```

4. Run the script:

   ```bash
   python telegram_scraper.py
   ```

---

## How It Works

* Opens the Telegram Web using Chrome with your profile.
* Waits for the chat area to load.
* Scrolls up gradually to load older messages.
* Detects and prints messages that contain a specific horizontal-line pattern (`---------------------------------------------`).
* Stops when it reaches the top of the chat.

---

## Example Output

```
---------------------------------------------
Date: 2024-06-01
Message: Lecture Notes Uploaded
...
```

---

## Customization

* Adjust the `is_on_top()` function logic to better determine when the oldest message is reached.
* Modify the filter condition inside the `for message in messages:` loop to capture different types of content.

---

## Disclaimer

This script is for educational and personal archival use only. Make sure you have permission to scrape or archive any group or channel.

---

## License

This project is licensed under the MIT License.

---

## Author

**Rishabh Shukla**
[GitHub Profile](https://github.com/Rishabh-27-Devloper)
