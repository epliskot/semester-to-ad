import os
import json
import requests

class FsClient:

    #
    # Finne brukernavn fra løpenummer:
    # https://fsapi-test.uio.no/personer/{LØPENUMMER}?dbId=false&refId=false
    def read_data(self, endpoint, token, emnekode, arstall, terminkode) -> dict:
        self.endpoint = endpoint
        self.token = token
        self.emnekode = emnekode
        self.arstall = arstall
        self.terminkode = terminkode

        if token is not None:
            try:
                request_student_on_courses = requests.get(endpoint + "/studentundervisning?dbId=false&refId=false&page=1&limit=0&undervisning.emne.institusjon=192&undervisning.emne.kode=" +
                                                          emnekode + "&undervisning.emne.versjon=1&undervisning.semester.ar=" +
                                                          str(arstall) + "&undervisning.semester.termin=" + terminkode + "",
                                                          headers={'Authorization': 'Bearer {}'.format(token)})
                return request_student_on_courses.json()

            except Exception as e:
                print("Exception " + str(e))
        else:
            return None

    def token(self, endpoint):
        self.endpoint = endpoint

        print("endpoint er " + endpoint)
        token_url = self.endpoint + "/token"
        print ("token_url er:" + token_url)

        request_token = requests.get(token_url, auth=(os.getenv("fs_user"), os.getenv("fs_pass")))
        data = request_token.json()
        my_token = data["token"]

        return my_token

    def get_username(self, json_item, emnekode, arstall, terminkode, endpoint, token) -> dict:

        return_this_dict = {}
        if len(json_item) != 0:
            i = 0
            for href in json_item:
                i += 1
                href_sub = href['href'].split(',')

                if href_sub[6] is not None:

                    hent_brukernavn = requests.get(endpoint + "/personer/" + href_sub[6] + "?dbId=false&refId=false",
                                                          headers={'Authorization': 'Bearer {}'.format(token)})
                    en_student = hent_brukernavn.json()
                    har_brukernavn = bool(en_student.get('brukernavn'))

                    if har_brukernavn:

                        return_this_dict[en_student['brukernavn']] = en_student['brukernavn']
                    else:
                        print("Student med løpenummer " + href_sub[6] + " har ikke brukernavn")

            return return_this_dict
        else:
            print("Json har ingen href-items")
            print("Finished with no items for emnekode: " \
                   + emnekode + " Årstall: " \
                   + str(arstall) + " Terminkode: " + terminkode)

            return return_this_dict

    def read_data_kull(self, endpoint, token, studieprogram, arstall_kull, termin_kull) -> dict:
            self.endpoint = endpoint
            self.token = token
            self.studieprogram = studieprogram
            self.arstall_kull = arstall_kull
            self.termin_kull = termin_kull

            if token is not None:
                try:
                    request_student_on_courses = requests.get(
                        endpoint + "/studieretter?dbId=false&refId=false&page=1&limit=0&studentstatus.aktivStudent=true&studentstatus.visUtdanningsplan=true&studierettstatus.aktiv=true",
                        headers={'Authorization': 'Bearer {}'.format(token)})

                    return request_student_on_courses.json()

                except Exception as e:
                    print("Exception " + str(e))
            else:
                return None

            # https://api.fellesstudentsystem.no/studieretter?dbId=false&refId=false&page=1&limit=0&studieprogram.kode=B-BIOL&studentstatus.aktivStudent=true&studierettstatus.aktiv=true

    def get_username_from_kull(self, json_item, studieprogram, arstall_kull, termin_kull, endpoint, token) -> dict:

        return_this_dict = {}
        result = {}

        if len(json_item) != 0:
            i = 0
            for href in json_item:
                i += 1
                href_sub = href['href'].split(',')

                if href_sub[3] is not None:

                    hent_brukernavn = requests.get(endpoint + "/personer/" + href_sub[3] + "?dbId=false&refId=false",
                                                          headers={'Authorization': 'Bearer {}'.format(token)})
                    en_student = hent_brukernavn.json()
                    fodselsdato = hent_brukernavn.json()
                    personnummer = hent_brukernavn.json()
                    har_brukernavn = bool(en_student.get('eposter'))
                    har_fodselsdato = bool(en_student.get('fodselsdato0'))
                    har_personnr = bool(en_student.get('personnummer0'))

                    if har_brukernavn and har_fodselsdato and har_personnr:

                        variab = fodselsdato['fodselsdato0']
                        variabe = personnummer['personnummer0']
                        variablee= en_student['eposter']

                        for x in range(len(variablee)):
                            sub_variablee = variablee[x]

                        if sub_variablee == None:
                            print ("sub_variablee is None")

                        if sub_variablee is not None:

                            if(sub_variablee['adresse'] == "zsh.sayed@gmail.com"):
                                print(" ")

                            else:
                                #print(str(i) +"," +str(variab) + "" + str(variabe) + "," +sub_variablee['adresse'])

                                list_one_line = (str(variab) + "" + str(variabe) + "," +sub_variablee['adresse'])


                                print(list_one_line)


                        return_this_dict[sub_variablee['adresse']] = sub_variablee['adresse']

                    else:
                        print("Student med løpenummer " + href_sub[3] + " har ikke eposter")

            return return_this_dict

        else:
            print("Json har ingen href-items")
            print("Finished with no items for studieprogram: " \
                   + studieprogram + " Årstall: " \
                   + str(arstall_kull) + " Terminkode: " + termin_kull)

            return return_this_dict
