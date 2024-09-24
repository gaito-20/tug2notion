from typing import List

from pydantic import BaseModel
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Knoten(BaseModel):
    id: str
    text: str
    children: List['Knoten']

    @classmethod
    def from_webelement(cls, webelement: WebElement, wait: WebDriverWait) -> 'Knoten':
        _id = webelement.get_property("id")

        try:
            # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.KnotenText')))
            _text = webelement.find_element(By.CSS_SELECTOR, 'span.KnotenText').text
        except NoSuchElementException:
            _text = webelement.text
        elems = webelement.parent.find_elements(By.CSS_SELECTOR, f".{_id}.hi")
        for elem in elems:
            try:
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "KnotenLink")))
                elem.find_element(By.CLASS_NAME, "KnotenLink").click()
            except NoSuchElementException:
                pass

        try:
            lv_selector = f"#{str(_id).replace('kn', 'GHK_')} tbody tbody span a"
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, lv_selector)))
            _children = [Knoten.from_webelement(webelement.parent.find_element(By.CSS_SELECTOR, lv_selector), wait)]
        except TimeoutException:
            _children = [Knoten.from_webelement(webelement=elem, wait=wait)
                         for elem
                         in filter(lambda elem: 'GHK' not in elem.get_property("id"), elems)]
        print(_text)
        return cls(id=_id, text=_text, children=_children)


class StudyPlanBuilder:

    @staticmethod
    def create(url) -> Knoten:
        driver = None
        try:
            driver = webdriver.Firefox()
            driver.get(url)

            wait = WebDriverWait(driver, 1)

            root = Knoten.from_webelement(webelement=driver.find_element(By.CSS_SELECTOR, "#tgt > tbody > tr:nth-child(1)"), wait=wait)
            return root
        finally:
            if driver:
                driver.close()
