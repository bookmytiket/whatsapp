
import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WhatsAppBridge:
    def __init__(self, session_dir="wa_session"):
        self.session_dir = os.path.join(os.getcwd(), session_dir)
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
            
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={self.session_dir}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless=new") # Recommended for production/Railway
        
        # Check for system paths (for Docker/Railway)
        chrome_bin = os.getenv("CHROME_BIN")
        if chrome_bin:
            chrome_options.binary_location = chrome_bin
            
        driver_path = os.getenv("CHROMEDRIVER_PATH")
        if driver_path:
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Fallback to local auto-install
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 60)

    def is_logged_in(self):
        self.driver.get("https://web.whatsapp.com/")
        try:
            # Check for search bar or side pane
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            return True
        except:
            return False

    def send_message(self, phone, message):
        """
        Sends a message to a specific phone number.
        phone: string with country code (e.g., '919876543210')
        """
        encoded_message = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        
        print(f"Initiating message to {phone}...")
        self.driver.get(url)
        
        try:
            # Wait for the send button to appear and be clickable
            # The send button usually has a specific data-testid or is an icon inside a button
            send_btn_xpath = '//span[@data-icon="send"]'
            self.wait.until(EC.element_to_be_clickable((By.XPATH, send_btn_xpath)))
            
            # Click send
            send_btn = self.driver.find_element(By.XPATH, send_btn_xpath)
            send_btn.click()
            
            # Give it a moment to actually send
            time.sleep(2)
            print(f"Message sent to {phone}")
            return True
        except Exception as e:
            print(f"Error sending message to {phone}: {str(e)}")
            return False

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    # Test block
    bridge = WhatsAppBridge()
    if bridge.is_logged_in():
        bridge.send_message("910000000000", "Hello from BookMyTicket Bridge!")
    else:
        print("Please scan the QR code in the browser window first.")
