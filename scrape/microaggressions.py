from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Open the webpage
url = "https://www.microaggressions.com/tagged/race"  # Replace with actual URL
driver.get(url)

# Scroll and load more content
SCROLL_PAUSE_TIME = 2  # Adjust this based on the site's loading time

last_height = driver.execute_script("return document.body.scrollHeight")
i = 0
while i < 50:
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    # Check for new scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:  # Break if no new content is loaded
        break
    last_height = new_height

    i += 1

# Extract the page source
html_source = driver.page_source
driver.quit()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_source, "html.parser")

# Extract the post texts
posts = []
for content in soup.select("div.content_wrap"):
    # Check if the post contains an <img> tag
    if content.find("img") is None:
        # Get the text content from the first matching element
        post_caption = content.select_one("div.post_caption > p")  # Use select_one for a single element
        if post_caption:  # Ensure it exists
            text = post_caption.get_text(strip=True)
            posts.append(text)

with open("data/posts.jsonl", "w", newline="", encoding="utf-8") as file:
    for txt in posts:
        file.write(fr"""
        {{
            "messages": [
                {{
                    "role": "user",
                    "parts": [
                        {{
                            "text": "{txt}"
                        }}
                    ]
                }},
                {{
                    "role": "model",
                    "parts": [
                        {{
                            "text": "microaggression"
                        }}
                    ]
                }}
            ]
        }}
        """)
