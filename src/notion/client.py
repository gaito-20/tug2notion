from typing import List

import requests

from tug.data import LV


class NotionClient:

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def search(self):
        """Returns page_id of connected Notion page."""
        data = {
            "filter": {
                "value": "page",
                "property": "object"
            }
        }
        resp = requests.post('https://api.notion.com/v1/search', headers=self.headers, json=data)
        return resp.json()["results"][0]["id"]

    def create_database(self, page_id, study_title: str):
        """Creates a database within the given page."""
        data = {
            "parent": {
                "type": "page_id",
                "page_id": page_id,
            },
            "icon": {
                "type": "emoji",
                "emoji": "\ud83c\udf93"
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": study_title,
                        "link": None
                    }
                }
            ],
            "properties": {
                "Name": {
                    "title": {}
                },
                "LV-Nummer": {
                    "rich_text": {}
                },
                "Angebotenes Semester": {
                    "multi_select": {
                        "options": [
                            {
                                "name": "Wintersemester",
                                "color": "blue"
                            },
                            {
                                "name": "Sommersemester",
                                "color": "green",
                            }
                        ]
                    }
                },
                "LV-Typ": {
                    "select": {
                        "options": [
                            {
                                "name": "VU",
                                "color": "gray"
                            },
                            {
                                "name": "VO",
                                "color": "red"
                            },
                            {
                                "name": "UE",
                                "color": "yellow"
                            },
                            {
                                "name": "KU",
                                "color": "purple"
                            },
                            {
                                "name": "KV",
                                "color": "green"
                            },
                            {
                                "name": "LU",
                                "color": "brown"
                            },
                            {
                                "name": "RU",
                                "color": "blue"
                            },
                            {
                                "name": "SE",
                                "color": "pink"
                            },
                            {
                                "name": "SP",
                                "color": "pink"
                            },
                            {
                                "name": "PR",
                                "color": "purple",
                            },
                            {
                                "name": "EX",
                                "color": "green"
                            }
                        ]
                    }
                },
                "ECTS": {
                    "number": {
                        "format": "number"
                    }
                },
                "SSt": {
                    "number": {
                        "format": "number"
                    }
                },
                "Modul": {
                    "multi_select": {
                        "options": []
                    }
                },
                "Vortragende": {
                    "rich_text": {}
                },
                "Kurs-Link": {
                    "url": {}
                }
            }

        }
        resp = requests.post('https://api.notion.com/v1/databases', headers=self.headers, json=data)
        return resp.json()["id"]

    def create_page(self, parent_id, lv: LV, parent_is_database: bool = False):
        data = {
            "parent": {"database_id": parent_id} if parent_is_database else {"page_id": parent_id},
            "properties": {
                "Name": {
                    "title": [{
                        "text": {
                            "content": lv.titel
                        }}
                    ]
                },
                "LV-Nummer": {
                    "rich_text": [{
                        "text": {
                            "content": lv.nummer
                        }
                    }]
                },
                "Angebotenes Semester": {
                    "multi_select": [{"name": semester} for semester in lv.semester]
                },
                "LV-Typ": {
                    "select": {
                        "name": lv.typ
                    }
                },
                "ECTS": {
                    "number": float(lv.ects)
                },
                "SSt": {
                    "number": float(lv.sst)
                },
                "Modul": {
                    "multi_select": [{"name": modul} for modul in lv.module]
                },
                "Vortragende": {
                    "rich_text": [{
                        "text": {
                            "content": lv.vortragende
                        }
                    }]
                },
                "Kurs-Link": {
                    "url": lv.link
                }
            }
        }
        resp = requests.post("https://api.notion.com/v1/pages", headers=self.headers, json=data)
        return resp.json()["id"]

    def import_study_plan(self, title: str, lvs: List[LV]):
        page_id = self.search()
        database_id = self.create_database(page_id, title)

        for lv in lvs:
            self.create_page(database_id, lv, parent_is_database=True)
