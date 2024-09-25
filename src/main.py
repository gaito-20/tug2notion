import datetime
from typing import List, Any, Optional

from pydantic import BaseModel

from tug.data import StudyPlanBuilder, LVSubscriber, LV

curriculum_url = "https://online.tugraz.at/tug_online/wbstpcs.showSpoTree?pSJNr=1685&pStpKnotenNr=&pStpStpNr=867&pFilterType=1&pPageNr=&pStartSemester=W"


# TODO:
#  - notion integration

class LVPrinter(LVSubscriber):
    def update(self, lv: LV):
        print(lv.model_dump_json())


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


exclude_nodes = ["Masterarbeit", "Freifach"]

if __name__ == '__main__':
    start_time = datetime.datetime.now()

    courses = StudyPlan()

    with StudyPlanBuilder(subscribers=[LVPrinter(), courses], exclude=exclude_nodes) as builder:
        study_plan = builder.create(curriculum_url)

    with open("result.json", "w", encoding='utf-8') as file:
        file.write(courses.model_dump_json())

    print(f"Execution took: {datetime.datetime.now() - start_time}")
