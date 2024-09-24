import datetime

from tug.data import StudyPlanBuilder

curriculum_url = "<curriculum_url>"

driver = webdriver.Firefox()
driver.get(tug_url)

if __name__ == '__main__':
    start_time = datetime.datetime.now()

    root = StudyPlanBuilder.create(curriculum_url)

    with open("result.json", "w", encoding='utf-8') as file:
        file.write(root.model_dump_json())

    print(f"Execution took: {datetime.datetime.now() - start_time}")
