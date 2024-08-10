import hashlib
import os
import requests
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json  # Add this line to import the json module


# Configuration
url = 'https://secure6.saashr.com/ta/6000630.careers?CareersSearch='
div_class = 'c-jobs-list'
GH_TOKEN = os.getenv('GH_TOKEN')
GIST_ID = os.getenv('GIST_ID')
GIST_FILENAME = 'contents.json'

headers = {
    'Authorization': f'token {GH_TOKEN}'
}
 
# Functions
def send_notification(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('SENDER_EMAIL')
    msg['To'] = os.getenv('RECEIVER_EMAIL')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('SENDER_EMAIL'), os.getenv('SMTP_PASSWORD'))
    server.send_message(msg)
    server.quit()

def get_previous_contents():
    response = requests.get(f'https://api.github.com/gists/{GIST_ID}', headers=headers)
    if response.status_code == 200:
        gist_content = response.json()
        return gist_content['files'][GIST_FILENAME]['content']
    else:
        print(f"Failed to get previous contents: {response.content}")
        return None

def set_previous_contents(contents):
    data = {
        'files': {
            GIST_FILENAME: {
                'content': contents
            }
        }
    }
    response = requests.patch(f'https://api.github.com/gists/{GIST_ID}', headers=headers, json=data)
    if response.status_code == 200:
        print("Successfully updated the contents on Gist.")
    else:
        print(f"Failed to update contents: {response.content}")

def check_div_change(previous_contents_list):
    options = webdriver.FirefoxOptions()
    options.headless = True
    with webdriver.Firefox(options=options) as browser:
        browser.get(url)
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, div_class))
            )
            job_labels = browser.find_elements(By.CSS_SELECTOR, f'.{div_class} .c-link__label')
            current_contents_list = [job_label.text for job_label in job_labels]

            # Determine changes
            added = [item for item in current_contents_list if item not in previous_contents_list]
            removed = [item for item in previous_contents_list if item not in current_contents_list]

            # Send notifications for changes
            if added:
                send_notification("New items added", f"The following new items were added:\n\n{added}")
            if removed:
                send_notification("Items removed", f"The following items were removed:\n\n{removed}")

            # Update the previous contents
            set_previous_contents(json.dumps({"contents": current_contents_list}))

        except Exception as e:
            print(f"An error occurred: {e}")
            send_notification("Error detected", f"An error occurred while checking the c-link__label elements: {e}")

# Main execution
if __name__ == "__main__":
    previous_contents_json = get_previous_contents()
    previous_contents_list = json.loads(previous_contents_json)["contents"] if previous_contents_json else []
    check_div_change(previous_contents_list)