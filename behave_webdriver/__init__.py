from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
import time


class BehaveDriver(object):
    def __init__(self, driver):
        self.driver = driver

    def __getattr__(self, item):
        if hasattr(self.driver, item):
            return getattr(self.driver, item)
        else:
            raise AttributeError('{} has no attribute {}'.format(self, item))

    @classmethod
    def chrome(cls, *args, **kwargs):
        driver = webdriver.Chrome(*args, **kwargs)
        return cls(driver=driver)

    @classmethod
    def headless_chrome(cls, *args, **kwargs):
        chrome_options = kwargs.pop('chrome_options', None)
        if chrome_options is None:
            chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(*args, chrome_options=chrome_options, **kwargs)
        return cls(driver=driver)

    @property
    def alert(self):
        return Alert(self.driver)
    @property
    def screen_size(self):
        size = self.driver.get_window_size()
        x = size['width']
        y = size['height']
        return (x, y)

    @screen_size.setter
    def screen_size(self, size):
        x, y = size
        if x is None:
            x = self.screen_size[0]
        if y is None:
            y = self.screen_size[1]
        self.driver.set_window_size(x, y)


    @property
    def cookies(self):
        return self.driver.get_cookies()

    @property
    def has_alert(self):
        e = EC.alert_is_present()
        return e(self.driver)

    def get_cookie(self, cookie_name):
        return self.driver.get_cookie(cookie_name)

    def get_element(self, selector, by=None):
        """
        :param selector: An xpath or CSS selector
        :return:
        """
        if by:
            return self.driver.find_element(by, selector)
        if selector.startswith('//'):
            return self.driver.find_element_by_xpath(selector)
        else:
            return self.driver.find_element_by_css_selector(selector)

    def get_element_text(self, element):
        elem = self.get_element(element)
        return elem.text

    def get_element_attribute(self, element, attr, css=False):
        elem = self.get_element(element)
        if css:
            value = elem.value_of_css_property(attr)
        else:
            value = elem.get_attribute(attr)
        return value

    def get_element_size(self, element):
        elem = self.get_element(element)
        return elem.size

    def get_element_location(self, element):
        elem = self.get_element(element)
        return elem.location

    def open_url(self, url):
        return self.driver.get(url)

    def element_exists(self, element):
        try:
            elem = self.get_element(element)
            return True
        except NoSuchElementException:
            return False

    def element_visible(self, element):
        elem = self.get_element(element)
        return elem.is_displayed()

    def element_enabled(self, element):
        elem = self.get_element(element)
        return elem.is_enabled()

    def element_selected(self, element):
        elem = self.get_element(element)
        return elem.is_selected()

    def click_element(self, element, n=1, delay=0.1):
        if n < 1:
            return
        elem = self.get_element(element)
        elem.click()
        for _ in range(n-1):
            time.sleep(delay)
            elem.click()

    def click_link_text(self, text, partial=False):
        if partial:
            self.driver.find_element_by_partial_link_text(text).click()
        else:
            self.driver.find_element_by_link_text(text).click()

    def drag_element(self, element, to_element):
        elem = self.get_element(element)
        to_elem = self.get_element(to_element)
        self.driver.drag_and_drop(elem, to_elem)

    def submit(self, element):
        elem = self.get_element(element)
        elem.submit()

    def send_keys(self, keys):
        actions = ActionChains(self.driver)
        actions.send_keys(keys)
        actions.perform()

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_element(self, element):
        location = self.get_element_location(element)
        x = location['x']
        y = location['y']
        self.scroll_to(x, y)

    def scroll_to(self, x, y):
        # prevent script injection
        x = int(x)
        y = int(y)
        self.driver.execute_script('window.scrollTo({}, {});'.format(x, y))


