from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from savePostInfo import df
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

download_dir = r"C:\Users\lawre\Desktop\TikTok Posting Script\program downloads"
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,  # Set download directory
    "download.prompt_for_download": False,       # Disable download prompt
    "download.directory_upgrade": True,          # Allow directory upgrade
    "safebrowsing.enabled": True                 # Enable safe browsing
})

def get_latest_downloaded_mp4(directory):
    file_list = []
    for f in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(".mp4"):
            file_list.append(os.path.join(directory, f))
    if not file_list:
        raise ValueError("No files found in directory")
    return max(file_list, key=os.path.getmtime)

def wait_for_import_completion(driver, timeout=300): #FOR LARGE FILES OTHERWISE SLEEP 2-5
    import time
    start_time = time.time()
    while True:
        try:
            # Attempt to locate the uploading indicator
            print("Checking for uploading indicator...")
            wait_and_find(driver, By.CSS_SELECTOR, ".uploading-card-container-ODzFLx")
            print("File is still uploading...")
        except TimeoutException:
            # If TimeoutException is raised, the upload is likely complete
            print("Upload completed.")
            break
        except Exception as e:
            # Catch any other exceptions and print the error
            print(f"An error occurred: {e}")
            break
        # Check if the timeout has been reached
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            print("Timeout reached. Exiting the wait loop.")
            break
        # Wait a short period before checking again
        time.sleep(2)

def make_tts_and_import(driver, df): 
    number_of_tabs = len(driver.window_handles)
    print(number_of_tabs)
    if number_of_tabs == 2:
        text = df['Title'].iloc[-1]
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://app.clipchamp.com/")
        perform_clipchamp_actions(driver, text)
        driver.switch_to.window(driver.window_handles[0])
        import_to_capcut(driver, get_latest_downloaded_mp4(download_dir))

    else: #number of tabs is 1 (meaning Clipchamp has not yert been used/opened, so we have to open it and login for the first time)
        text = df['Content'].iloc[-1]
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get("https://app.clipchamp.com/")
        login_clipchamp(driver)
        perform_clipchamp_actions(driver, text)
        driver.switch_to.window(driver.window_handles[0])
        import_to_capcut(driver, get_latest_downloaded_mp4(download_dir))

def perform_clipchamp_actions(driver, text):
    wait_and_click(driver, By.XPATH, "//button[@data-testid='create-project-button']")

    #Step 14: Click on Record&Create from sidebar
    wait_and_click(driver, By.ID, "sidebar-button-recordCreate")

    #Step 15: Click on TTS button 
    wait_and_click(driver, By.ID, "voiceover")

    wait_and_click(driver, By.XPATH, "//button[@data-testid='voice-dropdown']")

    #Step 17: Click on Andrew Multilingual option
    wait_and_click(driver, By.ID, "en-US-AndrewMultilingualNeural")

    text_area = wait_and_find(driver, By.XPATH, "//textarea[@data-testid='voice-script-textarea']")
    text_area.send_keys(text)
    time.sleep(2)
    wait_and_click(driver, By.XPATH, "//button[@data-testid='voice-save-button']")
    is_ready_for_export(driver)
    wait_and_click(driver, By.XPATH, "//button[@data-testid='button-export']")
    wait_and_click(driver, By.XPATH, "//div[@data-testid='id-480p']")
    wait_for_download_completion(download_dir)
    
def wait_for_download_completion(download_dir, timeout=600):
    """
    Waits for the download to complete in the specified directory.

    Args:
    download_dir (str): The directory where the file is being downloaded.
    timeout (int): The maximum time to wait for the download to complete.

    Returns:
    bool: True if download completed, False if timeout occurred.
    """
    start_time = time.time()
    while True:
        files = os.listdir(download_dir)
        if any([filename.endswith(".mp4") and not filename.endswith(".crdownload") for filename in files]):
            # Find the newest .mp4 file (excluding .crdownload files)
            mp4_files = [os.path.join(download_dir, f) for f in files if f.endswith(".mp4") and not f.endswith(".crdownload")]
            if mp4_files:
                return max(mp4_files, key=os.path.getctime)
        elif time.time() - start_time > timeout:
            raise Exception("Download did not complete within the timeout period.")
        else:
            # Wait and continue checking
            time.sleep(1)

def is_ready_for_export(driver):
    while True:
        preview_button = wait_and_find(driver, By.CSS_SELECTOR, 'button[data-testid="voice-preview-button"]' )
        save_button = wait_and_find(driver, By.CSS_SELECTOR, 'button[data-testid="voice-save-button"]')
        is_preview_button_clickable = (preview_button.is_enabled() and preview_button.get_attribute('aria-disabled') != 'true')
        is_save_button_not_clickable = (save_button.get_attribute('aria-disabled') == 'true')
        if is_preview_button_clickable and is_save_button_not_clickable:
            break
        else:
            time.sleep(3)

def login_clipchamp(driver):
    wait_and_click(driver, By.XPATH, "//button[@data-testid='provider-google']")
    google_email_input_field = wait_and_find(driver, By.XPATH, "//input[@type='email']")
    google_email_input_field.send_keys("taprojectlawrence@gmail.com")

    #Step 9: Click next after entering email
    wait_and_click(driver, By.XPATH, "//button[span[text()='Next']]")
    time.sleep(5)

    #Step 10: Enter password 
    google_password_input_field = wait_and_find(driver, By.XPATH, "//input[@type='password']")
    google_password_input_field.send_keys("TAPProject123")

    #Step 11: Click next after entering password
    wait_and_click(driver, By.XPATH, "//button[span[text()='Next']]")

    #Step 12: Click continue on Google authentication
    wait_and_click(driver, By.XPATH, "//button[span[text()='Continue']]")

def login_capcut(driver):
    email_input = wait_and_find(driver, By.NAME, "signUsername")
    email_input.send_keys("tapcapcut@gmail.com")

    wait_and_click(driver, By.CSS_SELECTOR, ".lv_sign_in_panel_wide_base_page-main-content button")

    # Step 3: Enter password
    password_input = wait_and_find(driver, By.XPATH, "//input[@type='password' and @placeholder='Enter password']")
    password_input.send_keys("TAPProject123")

    # Step 4: Click continue after entering password
    wait_and_click(driver, By.CSS_SELECTOR, ".lv_sign_in_panel_wide-sign-in-button")

def wait_and_find(driver, by, value, timeout=30):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def wait_and_click(driver, by, value, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
            element.click()
            return element
        except Exception as e:
            print(f"Wait and click: Attempt {attempt + 1} failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    print("Max retries reached. Failed to click element")
    return None

def seperate_audio_and_delete(driver):
    time.sleep(5)
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('s').key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
    time.sleep(2)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(2)

def import_to_capcut(driver, filepath):
    vid_file_input = wait_and_find(driver, By.CSS_SELECTOR, "input[type='file']")
    vid_file_input.send_keys(filepath)
    wait_for_download_completion(download_dir)
    
def perform_actions(driver):
    try:
        #Login
        login_capcut(driver)
        
        #Handle tutorial dialogs
        for _ in range(3): 
            wait_and_click(driver, By.CLASS_NAME, "guide-confirm-button")

        #Change aspect ratio to 9:16
        wait_and_click(driver, By. CSS_SELECTOR, "footer.lv-layout-footer")
        wait_and_click(driver, By.XPATH, "//p[text()='9:16']/ancestor::li")
        
        #Make content TTS and import to Capcut
        make_tts_and_import(driver, df)
    
        time.sleep(5)
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('s').key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
        time.sleep(2)
        actions.send_keys(Keys.BACKSPACE).perform()
        time.sleep(2)
        
        #Make title TTS and import to Capcut
        make_tts_and_import(driver, df)
        
        seperate_audio_and_delete(driver)

        #29: Click on background video to bring to timeline
        wait_and_click(driver, By.XPATH, "//div[contains(@class, 'card-item-label-vULukr') and contains(text(), '5 minute parkour.mp4')]/ancestor::div[@class='card-item-wrapper-HYfM9J card-item-U4KsAj']")
        time.sleep(5)
        fill_element = wait_and_find(driver, By.CSS_SELECTOR, "div.segment-widget-toolbar-button-lJbaUn")
        driver.execute_script("arguments[0].click();", fill_element)
        time.sleep(3600)



        # # Step 7: Export the video file
        # while True:
        #     try:
        #         wait_and_click(driver, By.ID, "export-video-btn")
        #         if check_for_empty_popup(driver):
        #             print("Popup detected: Project is empty and cannot be exported. Trying again")
        #         else:
        #             break
        #     except Exception as e:
        #         print(f"Error during export button click: {e}. Retrying...")

            


        # # Step 8: Download video
        # wait_and_click(driver, By.XPATH, "//button[@class='lv-btn lv-btn-secondary lv-btn-size-large lv-btn-shape-square lv-btn-long button_7ddfe' and @type='button']")
        # wait_and_click(driver, By.CLASS_NAME, "lv-select-view-value")
        # wait_and_click(driver, By.XPATH, "//li[@role='option']//span[text()='1080p']")
        # wait_and_click(driver, By.ID, "export-confirm-button")

        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def check_for_empty_popup(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Project is empty and cannot be exported')]"))
        )
        return True
    except:
        return False

def isDownloadDone(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "lv_share_export-container"))
        )
        return True
    except:
        return False

def main():
    while True:
        while True:
            try:
                service = Service(executable_path="chromedriver.exe")
                driver = webdriver.Chrome(service=service, options = chrome_options)
                driver.get("https://www.capcut.com/editor?start_tab=videom&enter_from=page_header&current_page=landing_page&from_page=landing_page&scenario=custom")
                driver.maximize_window()
                success = perform_actions(driver)

                if success:
                    break
                else:
                    driver.quit()
                    time.sleep(5)
            except Exception as e:
                print(f"Error detected with driver and/or window: {e}. Restarting...")
        if isDownloadDone(driver):
            break
    print("Download completed")
    driver.quit()

if __name__ == "__main__":
    main()