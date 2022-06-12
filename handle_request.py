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
        __CLIENT_ID = "8tp0hqx71y1dwuql"
        __CLIENT_SECRET = "gpfIT9Sv"
        url = "https://auth.emsicloud.com/connect/token"

        payload = f"client_id={__CLIENT_ID}&client_secret={__CLIENT_SECRET}&grant_type=client_credentials&scope=emsi_open"
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

        file_temp = open(f'./Tempary_Files/temp_cv_{self.username}.txt', 'w', encoding="utf-8")
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
        with open(f"./Tempary_Files/temp_cv_{self.username}.txt", "r", encoding="utf-8") as txt_file:
            return txt_file.read()

    @staticmethod
    def clean_text(output_string):
        text = re.sub('[^A-Za-z0-9]+', ' ', output_string)
        text = text.replace('\n', '\\n').replace('\t', '\\t')
        return text


class RetrieveSkills:
    def __init__(self, attached_file=None, username=None, language="en", text=None):
        api_call = EMSIAPIManagement()
        if EMSIAPIManagement().get_api_status():
            self.token = api_call.access_token()
            url = "https://emsiservices.com/skills/versions/latest/extract"
            querystring = {"language": f"{language}"}
            if text:
                text = FileManager(initiated=True).set_clean_text(text=text)
            else:
                text = FileManager(attached_file=attached_file, username=username, initiated=False).set_clean_text()
            payload = '{\"text\": \"' + text + '\", \"confidenceThreshold\": 0.6}'
            headers = {
                'Authorization': f"Bearer {self.token}",
                'Content-Type': "application/json",
            }
            self.response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers,
                                             params=querystring)
        else:
            raise Exception("Unable to connect to APIs")

    def retrieve_skills(self):
        return self.response.json().get("data")

    def all_skill_names(self):
        skill_list = []
        for skill in self.retrieve_skills():
            skill_list.append(skill.get("skill").get("name"))
        return skill_list


class RetrieveContactInformation:
    def __init__(self, attached_file=None, username=None, text=None):
        if not text:
            text = FileManager(attached_file=attached_file, username=username, initiated=False).set_clean_text()
        else:
            text = FileManager(initiated=True).set_clean_text(text=text)




RetrieveContactInformation(text=FileManager(username="gigum", attached_file="./resume.pdf").read_file())
