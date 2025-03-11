import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class IntegratedUserFlowTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
    
    def tearDown(self):
        self.driver.quit()
    
    def test_complete_user_journey(self):
        driver = self.driver
        
        # 1. Create or ensure a test user exists (this might be handled via fixtures)
        # For the purposes of an integrated test, you could navigate to a registration page,
        # fill out a registration form, and create a new user.
        driver.get("http://127.0.0.1:8000/register/")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("integrateduser")
        driver.find_element(By.NAME, "email").send_keys("integrated@example.com")
        driver.find_element(By.NAME, "password1").send_keys("TestPass123!")
        driver.find_element(By.NAME, "password2").send_keys("TestPass123!")
        # If there's a role field, select an appropriate role (e.g., warehouse_manager)
        # Then submit the form:
        driver.find_element(By.XPATH, "//button[text()='Register']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Welcome"))
        
        # 2. Log in as the new user (if not automatically logged in)
        # You can add login steps here if necessary.
        
        # 3. Create a Shipment
        driver.find_element(By.LINK_TEXT, "Shipments").click()
        create_shipment_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-target='#createShipmentModal']"))
        )
        driver.execute_script("arguments[0].click();", create_shipment_btn)
        self.wait.until(EC.visibility_of_element_located((By.ID, "createShipmentForm")))
        driver.find_element(By.NAME, "tracking_number").send_keys("INT_TRACK001")
        driver.find_element(By.NAME, "status").send_keys("In Transit")
        driver.find_element(By.NAME, "origin").send_keys("CityA")
        driver.find_element(By.NAME, "destination").send_keys("CityB")
        driver.find_element(By.NAME, "contents").send_keys("Integrated Goods")
        driver.find_element(By.XPATH, "//button[text()='Create Shipment']").click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "shipmentSuccessAlert")))
        # Optionally, close the modal if needed, then refresh and assert the shipment appears.
        
        # 4. Create an Event
        driver.find_element(By.LINK_TEXT, "Events").click()
        add_event_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add New Event")))
        add_event_link.click()
        self.wait.until(EC.presence_of_element_located((By.NAME, "name"))).send_keys("Integrated Expo")
        driver.find_element(By.NAME, "location").send_keys("Expo Center")
        driver.find_element(By.NAME, "description").send_keys("Integrated event testing")
        driver.find_element(By.NAME, "date").send_keys("2025-10-01")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Integrated Expo"))
        
        # 5. Update Profile (if applicable)
        driver.find_element(By.LINK_TEXT, "Profile").click()
        # For example, update email:
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.clear()
        email_field.send_keys("updated_integrated@example.com")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "updated_integrated@example.com"))
        
        # 6. Return to Homepage and verify the welcome message
        driver.find_element(By.LINK_TEXT, "Sports Logistics").click()
        self.assertIn("Welcome to Sports Logistics", driver.page_source)

if __name__ == '__main__':
    unittest.main()
