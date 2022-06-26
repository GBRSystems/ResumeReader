import json
import re
import time
from io import StringIO
import requests
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class EMSIAPIManagement:
    def __init__(self):
        __CLIENT_ID = "15vr6i8p2mx92c09"
        __CLIENT_SECRET = "VSO1EWcM"
        url = "https://auth.emsicloud.com/connect/token"

        payload = (
            f"client_id={__CLIENT_ID}&client_secret={__CLIENT_SECRET}&grant_type=client_credentials&scope=emsi_open"
        )
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, data=payload, headers=headers)
        time.sleep(2)
        self.__access_token = response.json().get("access_token")

    def _api_status(self) -> bool:
        url = "https://emsiservices.com/titles/status"
        headers = {'Authorization': f'Bearer {self.__access_token}'}
        response = requests.request("GET", url, headers=headers)
        return response.json().get("data").get("healthy")

    def access_token(self):
        if self.get_api_status():
            return self.__access_token
        else:
            return False

    def get_api_status(self):
        if self._api_status():
            return True
        else:
            return False


class FileManager:
    def __init__(self, attached_file=None, username=None, initiated=False):
        if not initiated:
            self.attached_file_location = attached_file
            self.username = username
            if self.attached_file_location:
                if self.attached_file_location[-4:] == ".pdf":
                    self.work_file()
            else:
                self.username = input("\nAdd your username here? \n")
                self.attached_file_location = input("\nAdd your PDF file here? \n")
                if self.attached_file_location[-4:] == ".pdf":
                    self.work_file()
                else:
                    raise Exception("Only PDF allowed")

    def work_file(self):
        output_string = StringIO()
        with open(self.attached_file_location, 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            resource_manager = PDFResourceManager()
            device = TextConverter(resource_manager, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)

        file_temp = open(f'./temp_files/temp_cv_{self.username}.txt', 'w', encoding="utf-8")
        text = self.clean_text(output_string.getvalue())
        file_temp.write(text)

    def set_clean_text(self, text=None):
        if text:
            return self.clean_text(text)
        else:
            if self.attached_file_location and self.username:
                return self.clean_text(self.read_file())
            else:
                raise Exception("Need username and file to process")

    def read_file(self):
        with open(f"./temp_files/temp_cv_{self.username}.txt", "r", encoding="utf-8") as txt_file:
            return txt_file.read()

    @staticmethod
    def clean_text(output_string):
        text = re.sub('[^A-Za-z0-9@.]+', ' ', output_string)
        text = text.replace('\n', '\\n').replace('\t', '\\t')
        return text


class RetrieveSkills:
    def __init__(self, attached_file=None, username=None, language="en", text=None):
        api_call = EMSIAPIManagement()
        self.username = username
        if EMSIAPIManagement().get_api_status():
            self.token = api_call.access_token()
            url = "https://emsiservices.com/skills/versions/latest/extract"
            querystring = {"language": f"{language}"}
            if text:
                self.text = FileManager(initiated=True).set_clean_text(text=text)
            else:
                self.text = FileManager(attached_file=attached_file, username=username, initiated=False).set_clean_text()
            payload = '{\"text\": \"' + self.text + '\", \"confidenceThreshold\": 0.6}'
            headers = {
                'Authorization': f"Bearer {self.token}",
                'Content-Type': "application/json",
            }
            self.response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers,
                                             params=querystring)
        else:
            raise Exception("Unable to connect to APIs")

    def retrieve_skills(self):
        if self.response.json().get("data"):
            return self.response.json().get("data")
        else:
            RetrieveSkillsCV(username=self.username, text=self.text).retrieve_data()

    def all_skill_names(self):
        skill_list = []
        for skill in self.retrieve_skills():
            skill_list.append(skill.get("skill").get("name"))
        return skill_list

    def retrieve_cleaned_skills(self):
        pass


class RetrieveContactInformation:
    def __init__(self, attached_file=None, username=None, text=None):
        if not text:
            self.text = FileManager(attached_file=attached_file, username=username, initiated=False).set_clean_text()
        else:
            self.text = FileManager(initiated=True).set_clean_text(text=text)

    def get_email(self):
        email_list = []
        emailRegex = re.compile(r'''([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))''', re.VERBOSE)
        email_groups = emailRegex.findall(self.text)
        for group in email_groups:
            email_list.append(group)
        if email_list:
            email = email_list[0][0]
            return email
        else:
            return None

    def get_phones(self):
        pass

    def get_experience_education(self):
        pass

    def get_address(self):
        pass


class ReturnCollectedDataSet:
    def __init__(self, attached_file=None, username=None, text=None):
        self.username = username
        self.skill_dictionary = (
            RetrieveSkills(attached_file=attached_file, username=username, text=text).retrieve_skills()
        )
        self.contact_phone = (
            RetrieveContactInformation(attached_file=attached_file, username=username, text=text).get_phones()
        )
        self.contact_emails = (
            RetrieveContactInformation(attached_file=attached_file, username=username, text=text).get_email()
        )

    def collected_data_set(self):
        data_json = (
            "{{'user_name':'{0}', 'phone':'{2}', 'email':'{3}','skills':'{1}'}}".format(
                self.username, self.skill_dictionary, self.contact_phone, self.contact_emails)
        )
        return data_json


class RetrieveSkillsCV:
    def __init__(self, username=None, text=None):
        pass

    def retrieve_data(self):
        pass
