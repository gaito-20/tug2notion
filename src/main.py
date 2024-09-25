import datetime
import json
import os
from dotenv import load_dotenv

from typing import List, Optional
from pydantic import BaseModel

from notion.client import NotionClient
from tug.data import StudyPlanBuilder, LVSubscriber, LV

load_dotenv()

curriculum_url = os.getenv('CURRICULUM_URL')
notion_api_key = os.getenv('NOTION_SECRET')


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
    with StudyPlanBuilder(subscribers=[courses], exclude=exclude_nodes) as builder:
        study_plan = builder.create(curriculum_url)

    client = NotionClient(notion_api_key)
    client.import_study_plan(title=study_plan.text, lvs=courses.lvs)

    print(f"Execution took: {datetime.datetime.now() - start_time}")
