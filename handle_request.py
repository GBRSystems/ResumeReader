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
from pdf2image import convert_from_path
import pytesseract
from pytesseract import image_to_string

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


class EMSIAPIManagement:
    def __init__(self):
        self.response = None
        self.token = None
        __CLIENT_ID = "15vr6i8p2mx92c09"
        __CLIENT_SECRET = "VSO1EWcM"
        url = "https://auth.emsicloud.com/connect/token"
        payload = f"client_id={__CLIENT_ID}&client_secret={__CLIENT_SECRET}&grant_type=client_credentials&scope=emsi_open"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        time.sleep(2)
        self.__access_token = response.json().get("access_token")

    def _api_status(self) -> bool:
        url = "https://emsiservices.com/titles/status"
        headers = {"Authorization": f"Bearer {self.__access_token}"}
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

    def get_data(self, language="en", text_input=None):
        if self.get_api_status() and text_input:
            self.token = self.access_token()
            url = "https://emsiservices.com/skills/versions/latest/extract"
            querystring = {"language": f"{language}"}
            payload = '{"text": "' + text_input + '", "confidenceThreshold": 0.6}'
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            self.response = requests.request(
                "POST",
                url,
                data=payload.encode("utf-8"),
                headers=headers,
                params=querystring,
            )
            if self.response.json().get("data"):
                return self.response.json().get("data")
            else:
                return None

    def all_skill_names(self):
        skill_list = []
        if self.get_data():
            for skill in self.get_data():
                skill_list.append(skill.get("skill").get("name"))
            return skill_list
        else:
            return None


class FileManager:
    def __init__(self, attached_file=None, username=None, initiated=False):
        if not initiated:
            self.attached_file_location = attached_file
            self.username = username
            if self.attached_file_location and username:
                if self.attached_file_location[-4:] == ".pdf":
                    self.__work_file()
            else:
                self.username = input("\nAdd your username here? \n")
                self.attached_file_location = input("\nAdd your PDF file here? \n")
                if self.attached_file_location[-4:] == ".pdf":
                    self.__work_file()
                else:
                    raise Exception("Only PDF allowed")

    def __work_file(self):
        output_string = StringIO()
        with open(self.attached_file_location, "rb") as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            resource_manager = PDFResourceManager()
            device = TextConverter(resource_manager, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
        text = self.__set_clean_text(output_string.getvalue())
        file_temp = open(
            f"./temp_files/temp_cv_{self.username}.txt", "w+", encoding="utf-8"
        )
        if text and len(text) > 2:
            file_temp.write(text)
            return text
        elif text:
            try:
                images = convert_from_path(self.attached_file_location)
                final_text = ""
                for pg, img in enumerate(images):
                    final_text += image_to_string(img)
                text = self.__set_clean_text(final_text)
                file_temp.write(text)
                return text
            except Exception as e:
                print(e)
                return None
        else:
            return None

    def __set_clean_text(self, text=None):
        if text:
            return self.__clean_text(text)
        else:
            if self.attached_file_location and self.username:
                return self.__clean_text(self.read_file())
            else:
                raise Exception("Need username and file to process")

    def read_file(self, file_path=None):
        if not file_path and self.username:
            file_path = f"./temp_files/temp_cv_{self.username}.txt"
        try:
            with open(file_path, "r", encoding="utf-8") as txt_file:
                return txt_file.read()
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def __clean_text(output_string):
        text = re.sub("[^A-Za-z0-9@.]+", " ", output_string)
        text = text.replace("\n", "\\n").replace("\t", "\\t")
        return text


class RetrieveSkills:
    def __init__(self):
        pass


class RetrieveContactInformation:
    def __init__(self, attached_file=None, username=None, text=None):
        pass

    def get_email(self, text_input=None):
        email_list = []
        emailRegex = re.compile(
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))", re.VERBOSE
        )
        if text_input:
            email_groups = emailRegex.findall(text_input)
            for group in email_groups:
                email_list.append(group)
            if email_list:
                return email_list[0][0]
            else:
                return None

    def get_phones(self, text):
        reg = re.compile(
            r"[\+\d]?(\d{2,3}[-\.\s]??\d{2,3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
        )
        phone_no = re.findall(reg, text)
        return phone_no

    def get_address(self):
        pass


FileManager(attached_file="resume_scanned.pdf", username="scanned")
