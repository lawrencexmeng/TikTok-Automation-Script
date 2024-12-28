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
import subprocess
import re

# Setup download directory and Chrome options
download_dir = r"c:\Users\lawre\Desktop\TAP DL Files"
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

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

def perform_clipchamp_actions(driver, text, key):
    wait_and_click(driver, By.XPATH, "//button[@data-testid='create-project-button']")
    project_name_box = wait_and_find(driver, By.XPATH, "//input[@type='text' and @data-testid='text-input']")
    if key == 1:
        project_name_box.send_keys("Title")
    elif key == 2:
        project_name_box.send_keys("Content")

    wait_and_click(driver, By.ID, "sidebar-button-recordCreate")
    wait_and_click(driver, By.ID, "voiceover")
    wait_and_click(driver, By.XPATH, "//button[@data-testid='voice-dropdown']")
    wait_and_click(driver, By.ID, "en-US-AndrewMultilingualNeural")

    text_area = wait_and_find(driver, By.XPATH, "//textarea[@data-testid='voice-script-textarea']")
    text_area.send_keys(text)
    time.sleep(2)
    wait_and_click(driver, By.XPATH, "//button[@data-testid='voice-save-button']")
    is_ready_for_export(driver)
    wait_and_click(driver, By.XPATH, "//button[@data-testid='button-export']")
    wait_and_click(driver, By.XPATH, "//div[@data-testid='id-480p']")

def login_clipchamp(driver):
    wait_and_click(driver, By.XPATH, "//button[@data-testid='provider-google']")
    google_email_input_field = wait_and_find(driver, By.XPATH, "//input[@type='email']")
    google_email_input_field.send_keys("taprojectlawrence@gmail.com")
    wait_and_click(driver, By.XPATH, "//button[span[text()='Next']]")
    time.sleep(5)
    google_password_input_field = wait_and_find(driver, By.XPATH, "//input[@type='password']")
    google_password_input_field.send_keys("TAPProject123")
    wait_and_click(driver, By.XPATH, "//button[span[text()='Next']]")
    wait_and_click(driver, By.XPATH, "//button[span[text()='Continue']]")

def is_ready_for_export(driver):
    while True:
        preview_button = wait_and_find(driver, By.CSS_SELECTOR, 'button[data-testid="voice-preview-button"]')
        save_button = wait_and_find(driver, By.CSS_SELECTOR, 'button[data-testid="voice-save-button"]')
        is_preview_button_clickable = (preview_button.is_enabled() and preview_button.get_attribute('aria-disabled') != 'true')
        is_save_button_not_clickable = (save_button.get_attribute('aria-disabled') == 'true')
        if is_preview_button_clickable and is_save_button_not_clickable:
            break
        else:
            time.sleep(3)

def make_title_tts_vid(driver, df):
    login_clipchamp(driver)
    text = df['Title'].iloc[-1]
    perform_clipchamp_actions(driver, text, 1)

def make_content_tts_vid(driver, df):
    text = df['Content'].iloc[-1]
    perform_clipchamp_actions(driver, text, 2)

def get_audio_length(audio_path):
    result = subprocess.run(
        ["ffmpeg", "-i", audio_path],
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    duration_match = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", result.stderr)
    if duration_match:
        return duration_match.group(1)
    return "Unknown"

def extract_and_concatenate_audio(title_video_path, content_video_path, output_audio_path):
    title_audio_path = title_video_path.replace(".mp4", "_Audio.wav")
    content_audio_path = content_video_path.replace(".mp4", "_Audio.wav")

    subprocess.run([
        "ffmpeg", "-i", title_video_path, "-q:a", "0", "-map", "a", title_audio_path
    ], check=True)

    subprocess.run([
        "ffmpeg", "-i", content_video_path, "-q:a", "0", "-map", "a", content_audio_path
    ], check=True)

    subprocess.run([
        "ffmpeg", "-i", f"concat:{title_audio_path}|{content_audio_path}",
        "-c", "copy", output_audio_path
    ], check=True)

    subprocess.run(["del", title_audio_path], shell=True)
    subprocess.run(["del", content_audio_path], shell=True)

    return output_audio_path

def adjust_video_to_audio(video_path, audio_length, output_video_path):
    subprocess.run([
        "ffmpeg", "-i", video_path, "-t", audio_length, "-c", "copy", output_video_path
    ], check=True)

def merge_audio_with_video(video_path, audio_path, final_output_path):
    subprocess.run([
        "ffmpeg", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", final_output_path
    ], check=True)

def process_video_and_audio(title_video_path=r"c:\Users\lawre\Desktop\TAP DL Files\Title - Made with Clipchamp.mp4",
                            content_video_path=r"c:\Users\lawre\Desktop\TAP DL Files\Content - Made with Clipchamp.mp4",
                            video_path=r"C:\Users\lawre\Desktop\TikTok Posting Script\5 minute parkour.mp4",
                            final_output_path=r"c:\Users\lawre\Desktop\TikTok Videos\vid_and_audio.mp4"):
    output_audio_path = extract_and_concatenate_audio(title_video_path, content_video_path, "output_audio.wav")
    audio_length = get_audio_length(output_audio_path)
    adjusted_video_path = video_path.replace(".mp4", "_Adjusted.mp4")
    adjust_video_to_audio(video_path, audio_length, adjusted_video_path)
    merge_audio_with_video(adjusted_video_path, output_audio_path, final_output_path)
    subprocess.run(["del", adjusted_video_path], shell=True)
    subprocess.run(["del", output_audio_path], shell=True)
    print(f"Final video with synced audio created: {final_output_path}")

def perform_actions(driver):
    make_title_tts_vid(driver, df)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://app.clipchamp.com/")
    make_content_tts_vid(driver, df)
    time.sleep(5)
    process_video_and_audio()

def main():
    try:
        service = Service(executable_path="chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://app.clipchamp.com/")
        driver.maximize_window()
        perform_actions(driver)
        time.sleep(10)
        driver.quit()
    except Exception as e:
        print(f"Error detected with driver and/or window: {e}. Restarting...")

if __name__ == "__main__":
    main()
