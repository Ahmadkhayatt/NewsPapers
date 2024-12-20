from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Set up Selenium options
Options = Options()
Options.add_experimental_option("detach", True)
url = 'https://simpleflying.com/category/aviation-news/'

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

    # Collect data
    df = pd.DataFrame({'Article Name':[], 'context':[], 'summary from url':[], 'page_url':[], 'image_url':[]})
    see_more_clicked = False  

    try:
        while True:
            
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'display-card')))
            
            # Collect the article links and image URLs from the dc-img-link
            elements = driver.find_elements(By.CLASS_NAME, 'dc-img-link')
            article_links = [element.get_attribute('href') for element in elements]
            image_elements = driver.find_elements(By.CLASS_NAME, 'dc-img-link')
            image_urls = [element.find_element(By.TAG_NAME, 'img').get_attribute('src') for element in image_elements]

            # Loop through the collected article links and image URLs
            for i, link in enumerate(article_links):
                driver.get(link) 
                time.sleep(5)
                
                # Scrape the article content
                try:
                    title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'threads-prompt-title')))
                    title = title_element.text if title_element else "No Title"
                except Exception as e:
                    print(f"Could not find article title: {e}")
                    try:
                        title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'article-header-title')))
                        title = title_element.text if title_element else "No Title"
                    except Exception as e:
                        print(f"Could not find article title with old class: {e}")
                        title = "No Title"

                # Scrape the content 
                try:
                    body = driver.find_element(By.CLASS_NAME, 'w-thread-prompt-content')
                    content = body.text.strip() if body else "No Content"
                    print("Extracted content.")
                except Exception as e:
                    content = "No Content"
                    print(f"Could not find article content (new class): {e}")
                    try:
                        body = driver.find_element(By.CLASS_NAME, 'content-block-regular')
                        content = body.text.strip() if body else "No Content"
                        print("Extracted content from old class.")
                    except Exception as e:
                        content = "No Content"
                        print(f"Could not find article content (old class): {e}")
                
                # Extract article summary
                try:
                    summary_elements = driver.find_elements(By.CSS_SELECTOR, 'div.custom_block-content.key-points li')
                    summary = ''.join([summary.text.strip() for summary in summary_elements])
                except Exception as e:
                    summary = "No Summary"
                    print(f"Could not find article summary with new class: {e}")
                    try:
                        summary_elements = driver.find_elements(By.CSS_SELECTOR, 'div.key-points li')
                        summary = ''.join([summary.text.strip() for summary in summary_elements])
                    except Exception as e:
                        summary = "No Summary"
                        print(f"Could not find article summary with old class: {e}")

                # Get the image
                image_url = image_urls[i] if i < len(image_urls) else "No Image"

                # Append data 
                if content:
                    df = df._append({
                        'Article Name': title, 
                        'context': content, 
                        'summary from url': summary, 
                        'page_url': link,
                        'image_url': image_url
                    }, ignore_index=True)

                # Go back to the main 
                driver.back()
                time.sleep(5)

            # Click the 'See More' button only once
            if not see_more_clicked:
                try:
                    more_btn = driver.find_element(By.XPATH, '/html/body/main/section[5]/div/section/a[1]')
                    driver.execute_script("arguments[0].click();", more_btn)
                    time.sleep(5)
                    see_more_clicked = True  
                    print("Clicked 'See More' button.")
                except Exception as e:
                    print(f"Error with 'See More' button: {e}")
                    break
            
            # Click the 'Next' 
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
