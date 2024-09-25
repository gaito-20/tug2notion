import datetime
import json
import os

from dotenv import load_dotenv

from notion.client import NotionClient
from tug.data import StudyPlanBuilder, StudyPlan

load_dotenv()

curriculum_url = os.getenv('CURRICULUM_URL')
notion_api_key = os.getenv('NOTION_SECRET')
exclude_nodes = json.loads(os.getenv('EXCLUDES'))

if __name__ == '__main__':
    start_time = datetime.datetime.now()

    courses = StudyPlan()
    with StudyPlanBuilder(subscribers=[courses], exclude=exclude_nodes) as builder:
        study_plan = builder.create(curriculum_url)

    client = NotionClient(notion_api_key)
    client.import_study_plan(title=study_plan.text, lvs=courses.lvs)

    print(f"Execution took: {datetime.datetime.now() - start_time}")
