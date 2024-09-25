import datetime

from tug.data import StudyPlanBuilder, LVSubscriber, LV

curriculum_url = "<curriculum_url>"


# TODO:
#  - deducplication
#  - skip unncessary courses (freifach, sprachen, softskills etc.)
#  - notion integration

class LVPrinter(LVSubscriber):
    def update(self, lv: LV):
        print(lv.model_dump_json())


if __name__ == '__main__':
    start_time = datetime.datetime.now()

    with StudyPlanBuilder(subscribers=[LVPrinter()]) as builder:
        study_plan = builder.create(curriculum_url)

    with open("result.json", "w", encoding='utf-8') as file:
        file.write(study_plan.model_dump_json())

    print(f"Execution took: {datetime.datetime.now() - start_time}")
