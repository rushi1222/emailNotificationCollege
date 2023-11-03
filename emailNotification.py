from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import hashlib
import smtplib
from email.message import EmailMessage
from selenium.webdriver.firefox.options import Options
import os

# Configuration
url = 'https://secure6.saashr.com/ta/6000630.careers?CareersSearch='
div_class = 'c-jobs-list'  # Replace with actual class if different
previous_hash = None

# Set Firefox to run in headless mode
options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)

def send_notification(body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'Change Detected!'
    msg['From'] = os.environ['SENDER_EMAIL']
    msg['To'] = os.environ['RECEIVER_EMAIL']

    # Configure the SMTP settings for your email server
    server = smtplib.SMTP('smtp.gmail.com', 587)  # 587 is typically used for starttls
    server.starttls()
    server.login(os.environ['SMTP_USERNAME'], os.environ['SMTP_PASSWORD'])
    server.send_message(msg)
    server.quit()

def check_div_change():
    global previous_hash
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

        # Check if the div has changed
        if previous_hash is not None and current_hash != previous_hash:
            send_notification(f"The div has changed.\n\n{div_content}")
        # Update the previous hash
        previous_hash = current_hash

    except Exception as e:
        print(f"An error occurred: {e}")  # Print the exception

if __name__ == "__main__":
    check_div_change()
    browser.quit()
