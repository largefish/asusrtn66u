import time
from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class rtn66u:
    def __init__(self, loginURL, username, password):
        self.loginURL = loginURL
        self.username = username
        self.password = password

        self.driver = None
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chromeOptions)


    def loginrouter(self):
        try:
            self.driver.get(self.loginURL)
            e = self.driver.find_element_by_id("login_username")
            e.send_keys(self.username)
            e = self.driver.find_element_by_name("login_passwd")
            e.send_keys(self.password)
            e = self.driver.find_element_by_class_name("button")
            e.click()

            #Wait for home page to load
            self.driver.implicitly_wait(10)

        except Exception as e:
            print(e)
            self.driver.quit()

    def logoutrouter(self):

        try:
            #This works!
            #logoutbutton = driver.find_element_by_xpath("//div[@class='titlebtn']")
            logoutbutton = self.driver.find_element_by_xpath("//div[@style='margin-top:13px;margin-left:25px; *width:136px;']")
            logoutbutton.click()
            self.driver.implicitly_wait(1)
            logoutconfirmalert = self.driver.switch_to.alert
            logoutconfirmalert.accept()

            #self.driver.save_screenshot("loggedout.png")
        except Exception as e:
            print(e)
        
        finally:
            self.driver.quit()

    def rebootrouter(self):
        try:
            rebootbutton = self.driver.find_element_by_xpath("//div[@style='margin-top:13px;margin-left:0px;*width:136px;']")
            rebootbutton.click()
            self.driver.implicitly_wait(1)
            rebootconfirmalert = self.driver.switch_to.alert
            rebootconfirmalert.accept()

            #self.driver.save_screenshot("reboot.png")

            #Allow time for the router to come back up
            time.sleep(90)

        except Exception as e:
            print(e)

        finally:
            self.driver.quit()

    #A method that can activate a VPN client connection, provided the configurations
    #    are already loaded in the web interface
    #Will return 0 if successful, or an error message if not
    def changeVPN(self, location):
        location = location.lower()

        try:
            VPNpagebutton = self.driver.find_element_by_id("Advanced_VPN_PPTP_menu")
            VPNpagebutton.click()

            #Wait for next page to load
            self.driver.implicitly_wait(15)

            VPNclienttab = self.driver.find_element_by_id("Advanced_VPNClient_Content_tab")
            VPNclienttab.click()

            #Wait for next page to laod
            self.driver.implicitly_wait(15)

            #Get a list of exit locations currently configured in the rourter
            staleElement = True
            while(staleElement):
                try:
                    vpntable = self.driver.find_element_by_id("vpnc_clientlist_table")
                    vpntablerows = vpntable.text.lower()
                    staleElement = False
                except StaleElementReferenceException as e:
                    staleElement = True
            
            exitlocations = vpntablerows.split('\n')

            #Find currently activated location in list
            currentlocation = ""
            for exitlocation in exitlocations:
                if not "-" in exitlocation:
                    currentlocation = exitlocation
                    break
            if location in currentlocation:
                return(location + " is already the active location")

            #Delete currently activated location from list
            #This is done because when we get the list of location options to activate, current location is not included
            exitlocations.remove(currentlocation)

            #Find the list index of the desired exit location
            locationposition = -1
            n = 0
            for exitlocation in exitlocations:
                if location in exitlocation:
                    locationposition = n
                    break
                else: n = n + 1

            #If locationposition is never updated then the passed in locatioon is not an option
            if locationposition == -1:
                options = ""
                for exitlocation in exitlocations:
                    options = options + str(exitlocation).replace("- ", "").replace("OpenVPN", "").strip() + ", "
                options = options[:-2]
                return("No configuration available for " + location + "\nOptions are " + options)

            #Click button to change VPN location
            staleElement = True 

            while(staleElement):
                try:
                    buttons = self.driver.find_elements_by_xpath("//input[@value='Activate']")
                    buttons[locationposition].click()
                    staleElement = False

                except StaleElementReferenceException as e:
                    staleElement = True

            #Allow time for the new VPN connection to be established
            time.sleep(10)

            return(0)

        except Exception as e:
            print(e)
            self.driver.quit()
