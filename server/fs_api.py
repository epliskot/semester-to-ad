import json
import os
import io
import sys

from server.fs_client import FsClient

class FsApi:

    def __init__(self, fs_client):
        self.fs_client = fs_client


    def start(self, emnekode, arstall, terminkode):
        # Gå i loop
        # fs_data = self.fs_client.read_data()
        # groupsname = fs_data["gruppe1"]

        endpoint= "https://api.fellesstudentsystem.no"

        the_token = self.fs_client.token(endpoint)
        if the_token is not None:
            try:
                get_courses = self.fs_client.read_data_kull(endpoint, the_token, emnekode, arstall, terminkode)

                if get_courses is None:
                    print("get_course is none")
                else:
                    json_item = get_courses['items']

                    get_kull_vet_termin = self.fs_client.get_username_from_kull(json_item, emnekode, arstall, terminkode, endpoint, the_token)

                    result = {}
                    for key, value in get_kull_vet_termin.items():
                        if value not in result.values():
                            result[key] = value

            except Exception as e:
                raise Exception("FEILER: sjekk denne 2022-04-11" + str(e))

fs_client = FsClient()

fs_api = FsApi(fs_client=fs_client)
fs_api.start("VET", "2021", "SOMMER")


