from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Node(BaseModel):
    parent: Optional['Node'] = Field(None, exclude=True)
    children: Optional[List['Node']] = None


class Knoten(Node):
    id: str
    category: str
    text: str
    empf_semester: Optional[str]
    ects: Optional[str]
    sst: Optional[str]


class LV(Node):
    nummer: str
    titel: str
    semester: List[str]
    typ: str
    ects: str
    sst: str
    vortragende: str
    link: str
    module: List[str]

    def extend(self, other: 'LV'):
        """Merge two lv objects that represent the same course"""
        if self.nummer == other.nummer:
            # the same LV could be offered in different semesters
            self.semester.sort()
            self.module.sort()
            other.semester.sort()
            other.module.sort()
            if self.semester != other.semester:
                self.semester.extend(other.semester)
                self.semester = list(dict.fromkeys(self.semester))
            # the same LV could be within different modules in a study
            if self.module != other.semester:
                self.module.extend(other.module)
                self.module = list(dict.fromkeys(self.module))
            return


class LVSubscriber(ABC):

    @abstractmethod
    def update(self, lv: LV):
        pass


class StudyPlan(LVSubscriber, BaseModel):
    lvs: List[LV] = []

    def lookup_lv(self, lv) -> Optional[LV]:
        if res := list(filter(lambda x: x.nummer == lv.nummer, self.lvs)):
            return res[0]
        return None

    def update(self, lv: LV):
        if existing_lv := self.lookup_lv(lv):
            existing_lv.extend(lv)
        else:
            self.lvs.append(lv)


class StudyPlanBuilder:

    def __init__(self, timeout=2, subscribers: List[LVSubscriber] = [], exclude: List[str] = []):
        try:
            self.driver = webdriver.Firefox()
        except Exception:
            self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, timeout)
        self.subscribers = subscribers
        self.exclude = exclude

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def notify_all_lv_created(self, lv: LV):
        for subscriber in self.subscribers:
            subscriber.update(lv)

    def __from_webelement(self, webelement: WebElement, parent: Optional[Knoten] = None) -> Optional[Knoten]:
        """ Get 'Knoten' infos from the <tr> webelement"""

        # Get id
        _id = webelement.get_property("id")

        # Get Knoten text and category
        try:
            title_span = webelement.find_element(By.CSS_SELECTOR, 'span.KnotenText')
            _text = title_span.text
            _category = title_span.get_attribute("title")
        except NoSuchElementException:
            _text = webelement.text
            _category = ""

        for exclude_elem in self.exclude:
            if exclude_elem in _text:
                return None

        columns = webelement.find_elements(By.CSS_SELECTOR, "td>div>span")
        # Get empf_semester
        semester_text = columns[2].text
        _empf_semester = semester_text if len(semester_text) > 0 and semester_text != "-" else None

        # Get ects
        ects_text = columns[3].text
        _ects = ects_text if len(ects_text) > 0 else None

        # Get sst
        sst_text = columns[4].text
        _sst = sst_text if len(ects_text) > 0 else None

        # Open Knoten by clicking on them
        elems = webelement.parent.find_elements(By.CSS_SELECTOR, f".{_id}.hi")
        for elem in elems:
            try:
                elem_id = elem.get_property('id')
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#{elem_id} .KnotenLink"))).click()
            except TimeoutException:
                pass

        knoten = Knoten(id=_id, text=_text, ects=_ects, empf_semester=_empf_semester, sst=_sst,
                        category=_category, parent=parent)

        # Get children
        try:
            lv_selector = f"#{str(_id).replace('kn', 'GHK_')} tbody tbody tr"
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, lv_selector)))
            # If there's no exception here then the following block contains the courses/LVs
            _children = []
            for elem in webelement.parent.find_elements(By.CSS_SELECTOR, lv_selector):
                # here: elem = <tr> of the course
                lv_fields = elem.find_elements(By.TAG_NAME, 'td')
                try:
                    lv_a = lv_fields[0].find_element(By.CSS_SELECTOR, 'span>a')

                    nummer, semester, sst, typ, titel = str(lv_a.text).split(maxsplit=4)

                    tmp = knoten
                    module = []
                    while tmp is not None:
                        if "Modulknoten" in tmp.category:
                            modultitel = tmp.text.split("]", maxsplit=1)[1].strip().split(maxsplit=1)[
                                1]  # Removes title from "[###] ## title"
                            module.append(modultitel)
                            break
                        else:
                            tmp = tmp.parent

                    lv = LV(
                        nummer=nummer,
                        titel=titel,
                        semester=["Wintersemester" if "W" in semester.upper() else "Sommersemester"],
                        typ=typ,
                        ects=_ects,
                        sst=sst.removesuffix("SSt"),
                        vortragende=lv_fields[2].text,
                        link=lv_a.get_attribute("href"),
                        parent=knoten,
                        module=module
                    )

                    _children.append(lv)
                    self.notify_all_lv_created(lv)
                except NoSuchElementException:
                    # That means that there are no entries for a course/LV
                    pass
        except TimeoutException:
            # If there's an exception, that means that this is still a Knoten with more children
            _children = list(filter(lambda x: x is not None, [self.__from_webelement(webelement=elem, parent=knoten)
                                                              for elem
                                                              in
                                                              filter(lambda elem: 'GHK' not in elem.get_property("id"),
                                                                     elems)]))
        knoten.children = _children
        self.exclude.append(knoten.text)  # dont crawl identical 'Knoten' multiple times

        return knoten

    def create(self, url) -> Knoten:
        self.driver.get(url)
        return self.__from_webelement(
            webelement=self.driver.find_element(By.CSS_SELECTOR, "#tgt > tbody > tr:nth-child(1)"))
