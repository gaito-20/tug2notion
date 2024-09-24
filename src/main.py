import datetime

from tug.data import StudyPlanBuilder

curriculum_url = "<curriculum_url>"

# TODO:
#  - get ects
#  - maybe -> already save courses when found => dont double iterate through data
#  - maybe link to course
#  - postprocessing
#  - notion integration

if __name__ == '__main__':
    start_time = datetime.datetime.now()

    root = StudyPlanBuilder.create(curriculum_url)

    with open("result.json", "w", encoding='utf-8') as file:
        file.write(root.model_dump_json())

    print(f"Execution took: {datetime.datetime.now() - start_time}")
