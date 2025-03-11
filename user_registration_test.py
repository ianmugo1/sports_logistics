import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

class UserRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
    
    def tearDown(self):
        self.driver.quit()
    
    def test_user_registration(self):
        driver = self.driver
        # Navigate to the registration page
        driver.get("http://127.0.0.1:8000/register/")
        
        # Wait until the registration form is loaded
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        
        # Fill out the registration form
        driver.find_element(By.NAME, "username").send_keys("testuser1")
        driver.find_element(By.NAME, "email").send_keys("testuser1@example.com")
        # Adjust password field name if needed; if it's password1/password2, change accordingly.
        driver.find_element(By.NAME, "password1").send_keys("TestPass123!")
        driver.find_element(By.NAME, "password2").send_keys("TestPass123!")
        
        # If your registration form includes a role selection, select the desired role.
        try:
            role_select = Select(driver.find_element(By.NAME, "role"))
            role_select.select_by_value("customer")  # Adjust the value as needed
        except Exception:
            pass
        
        # Submit the registration form; adjust the button text if necessary.
        driver.find_element(By.XPATH, "//button[text()='Register']").click()
        
        # Wait until registration is successful
        # Adjust the expected text to something that appears on the page after registration.
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Sports Logistics"))
        self.assertIn("Sports Logistics", driver.page_source)

if __name__ == '__main__':
    unittest.main()
