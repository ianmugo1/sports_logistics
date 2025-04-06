import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sports_logistics.settings')
import django
django.setup()

import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class IntegratedUserFlowTest(LiveServerTestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        # Generate a unique ID for each test run
        self.unique_id = str(int(time.time()))
        self.username = f"integrateduser_{self.unique_id}"
        self.email = f"user{self.unique_id}@example.com"
        self.password = "TestPass123!"

    def tearDown(self):
        self.driver.quit()

    def test_complete_user_journey(self):
        driver = self.driver
        # Use self.live_server_url provided by LiveServerTestCase
        driver.get(f"{self.live_server_url}/register/")
        
        # --- User Registration ---
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.username)
        driver.find_element(By.NAME, "email").send_keys(self.email)
        # Updated field names: "password" and "confirm_password"
        driver.find_element(By.NAME, "password").send_keys(self.password)
        driver.find_element(By.NAME, "confirm_password").send_keys(self.password)
        driver.find_element(By.XPATH, "//button[text()='Register']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Welcome"))
        
        # --- Shipment Creation ---
        driver.find_element(By.LINK_TEXT, "Shipments").click()
        create_shipment_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-target='#createShipmentModal']"))
        )
        driver.execute_script("arguments[0].click();", create_shipment_btn)
        self.wait.until(EC.visibility_of_element_located((By.ID, "createShipmentForm")))
        tracking_number = f"INT_TRACK_{self.unique_id}"
        driver.find_element(By.NAME, "tracking_number").send_keys(tracking_number)
        driver.find_element(By.NAME, "status").send_keys("In Transit")
        driver.find_element(By.NAME, "origin").send_keys("CityA")
        driver.find_element(By.NAME, "destination").send_keys("CityB")
        driver.find_element(By.NAME, "contents").send_keys("Integrated Goods")
        driver.find_element(By.XPATH, "//button[text()='Create Shipment']").click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "shipmentSuccessAlert")))
        
        # --- Event Creation ---
        driver.find_element(By.LINK_TEXT, "Events").click()
        add_event_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add New Event")))
        add_event_link.click()
        event_name = f"Integrated Expo {self.unique_id}"
        self.wait.until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(event_name)
        driver.find_element(By.NAME, "location").send_keys("Expo Center")
        driver.find_element(By.NAME, "description").send_keys("Integrated event testing")
        driver.find_element(By.NAME, "date").send_keys("2025-10-01")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), event_name))
        
        # --- Profile Update ---
        driver.find_element(By.LINK_TEXT, "Profile").click()
        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.clear()
        updated_email = f"updated_{self.email}"
        email_field.send_keys(updated_email)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), updated_email))
        
        # --- Return to Homepage ---
        driver.find_element(By.LINK_TEXT, "Sports Logistics").click()

if __name__ == '__main__':
    import unittest
    unittest.main()
