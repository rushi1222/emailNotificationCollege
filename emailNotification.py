from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import hashlib
import smtplib
from email.message import EmailMessage

# Configuration
url = 'https://secure6.saashr.com/ta/6000630.careers?CareersSearch='
div_class = 'c-jobs-list'  # Replace with actual class if different
previous_hash = None
browser = webdriver.Firefox()

def send_notification(body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'Change Detected!'
    msg['From'] = 'k.rushi15108@gmail.com'
    msg['To'] = 'k.rushi1222@gmail.com'

    # Configure the SMTP settings for your email server
    server = smtplib.SMTP('smtp.gmail.com', 587)  # 587 is typically used for starttls
    server.starttls()
    server.login('k.rushi15108@gmail.com', 'qtwk vicf cfua obpl')  # Replace with actual credentials
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
        else:
            # This is the first time we're checking or the div has not changed; don't notify
            pass

        # Update the previous hash
        previous_hash = current_hash

    except Exception as e:
        print(f"An error occurred: {e}")  # Print the exception

    finally:
        browser.quit()

if __name__ == "__main__":
    check_div_change()
