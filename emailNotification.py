from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import hashlib
import smtplib
from email.message import EmailMessage
import requests
import os

# Configuration
url = 'https://secure6.saashr.com/ta/6000630.careers?CareersSearch='
div_class = 'c-jobs-list'  # Replace with the actual class if different
GH_TOKEN = os.getenv('GH_TOKEN')
GIST_ID = os.getenv('GIST_ID')
GIST_FILENAME = 'hash.txt'

headers = {
    'Authorization': f'token {GH_TOKEN}'
}

def send_notification(body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'Change Detected!'
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = os.getenv('RECEIVER_EMAIL')

    # Configure the SMTP settings for your email server
    server = smtplib.SMTP('smtp.gmail.com', 587)  # 587 is typically used for starttls
    server.starttls()
    server.login(os.getenv('SENDER_EMAIL'), os.getenv('SMTP_PASSWORD'))
    server.send_message(msg)
    server.quit()

def get_previous_hash():
    response = requests.get(f'https://api.github.com/gists/{GIST_ID}', headers=headers)
    if response.status_code == 200:
        gist_content = response.json()
        return gist_content['files'][GIST_FILENAME]['content']
    else:
        print(f"Failed to get previous hash: {response.content}")
        return None

def set_previous_hash(hash_value):
    data = {
        'files': {
            GIST_FILENAME: {
                'content': hash_value
            }
        }
    }
    response = requests.patch(f'https://api.github.com/gists/{GIST_ID}', headers=headers, json=data)
    if response.status_code == 200:
        print("Successfully updated the hash on Gist.")
    else:
        print(f"Failed to update hash: {response.content}")
def check_div_change(previous_hash):
    # Setup Firefox options
    options = webdriver.FirefoxOptions()
    options.headless = True  # Important for running in GitHub Actions environment
    with webdriver.Firefox(options=options) as browser:
        # Open the website
        browser.get(url)
        try:
            # Find the div by class name
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, div_class))
            )
            div_content = browser.find_element(By.CLASS_NAME, div_class).get_attribute('innerHTML')

            # Calculate the current hash
            current_hash = hashlib.md5(div_content.encode('utf-8')).hexdigest()

            # Compare the current hash with the previous hash
            if previous_hash is not None:
                if current_hash != previous_hash:
                    send_notification(f"The div has changed.\n\n{div_content}")
                else:
                    send_notification("The div has not changed.")
            else:
                print("First check, notification will not be sent.")

            # Update the previous hash
            set_previous_hash(current_hash)

        except Exception as e:
            print(f"An error occurred: {e}")  # Print the exception
            send_notification(f"An error occurred while checking the div: {e}")

if __name__ == "__main__":
    previous_hash = get_previous_hash()
    check_div_change(previous_hash)

