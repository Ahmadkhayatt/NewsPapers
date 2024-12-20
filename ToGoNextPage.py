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
