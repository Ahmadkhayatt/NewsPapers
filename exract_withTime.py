from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta

# Set up Selenium options
Options = Options()
Options.add_experimental_option("detach", True)
url = 'https://simpleflying.com/category/aviation-news/'


# Add a function to check the date

def is_recent_article(article_datetime_str, max_days=4):
    """Check if the article is within the last 'max_days' days."""
    try:
        # Parse the article datetime from the string
        article_datetime = datetime.strptime(article_datetime_str.split('T')[0], "%Y-%m-%d")
        current_time = datetime.now()
        
        # Calculate the difference in days
        days_difference = (current_time - article_datetime).days
        print(f"Article datetime: {article_datetime}, Days difference: {days_difference}")

        # Return True if within max_days, else False
        return days_difference <= max_days
    except Exception as e:
        print(f"Error processing article datetime: {article_datetime_str} - {e}")
        return False


def scrape_articles(url):
    driver = webdriver.Chrome(options=Options)
    driver.get(url)
    driver.find_element(By.ID, 'login-button-header').click()
    time.sleep(0.5)

    driver.find_element(By.ID, 'signin-with-email-button-popup').click()
    time.sleep(0.5)

    driver.find_element(By.ID, 'continue-email-popup').send_keys('603b10b0e4@emaildbox.pro')
    driver.find_element(By.ID, 'continue-button-popup').click()
    time.sleep(1)
    driver.find_element(By.ID, 'login-password-popup').send_keys('Qwertyuiop123')
    driver.find_element(By.ID, 'login-button-popup').click()
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    driver.find_element(By.CLASS_NAME, 'nav-left').click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, '#side-navigation > div > label.js-search-focus.css-menu--checkbox-wrapper.css-menu--toggle > span').click()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, '#js-search-input').send_keys('Qatar airways' + Keys.ENTER)

    # Collect data
    df = pd.DataFrame({'Article Name': [], 'context': [], 'summary from url': [], 'page_url': [], 'image_url': []})
    see_more_clicked = False

    try:
        while True:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'display-card')))

            # Collect the article elements
            articles = driver.find_elements(By.CLASS_NAME, 'display-card')
            for article in articles:
                try:
                    # Extract article datetime
                    datetime_element = article.find_element(By.CLASS_NAME, 'display-card-date')
                    article_datetime = datetime_element.get_attribute('datetime')
                    print(article_datetime)

                    # Check if the article is recent
                    if is_recent_article(article_datetime , max_days= 4):
                        # Extract the article link
                        link_element = article.find_element(By.CLASS_NAME, 'dc-img-link')
                        link = link_element.get_attribute('href')
                        

                        # Get the article title
                        title = article.find_element(By.CLASS_NAME, 'threads-prompt-title').text.strip()

                        # Extract the image URL
                        image_url = link_element.find_element(By.TAG_NAME, 'img').get_attribute('src')

                        # Navigate to the article page for further content and summary
                        driver.get(link)
                        time.sleep(2)

                        # Scrape the content
                        try:
                            body = driver.find_element(By.CLASS_NAME, 'w-thread-prompt-content')
                            content = body.text.strip() if body else "No Content"
                        except:
                            content = "No Content"

                        # Extract article summary
                        try:
                            summary_elements = driver.find_elements(By.CSS_SELECTOR, 'div.custom_block-content.key-points li')
                            summary = ''.join([summary.text.strip() for summary in summary_elements])
                        except:
                            summary = "No Summary"

                        # Append data
                        df = df._append({
                            'Article Name': title,
                            'context': content,
                            'summary from url': summary,
                            'page_url': link,
                            'image_url': image_url
                        }, ignore_index=True)

                        # Return to the search page
                        driver.back()
                        time.sleep(2)

                except Exception as e:
                    print(f"Error processing article: {e}")

            # Click the 'Next' button to go to the next page
            try:
                next_btn = driver.find_element(By.CLASS_NAME, 'next')
                next_href = next_btn.get_attribute('href')
                driver.get(next_href)
                print(f"Navigating to next page: {next_href}")
                time.sleep(5)
            except Exception as e:
                print(f"Error with 'Next' button: {e}")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        return df

# Fetch the data
df = scrape_articles(url)

# Save to CSV
df.to_csv('test3.csv', encoding='utf-8-sig', index=False)
