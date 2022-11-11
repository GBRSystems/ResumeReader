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
import os.path
import phonenumbers
from phonenumbers import timezone
from datetime import datetime
import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
import pypostalwin

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


class _EMSIAPIManagement:
    def __init__(self, client_id="15vr6i8p2mx92c09", client_secret="VSO1EWcM"):
        self.response = None
        self.token = None
        __CLIENT_ID = client_id
        __CLIENT_SECRET = client_secret
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


class _FileManager:
    def __init__(
        self, attached_file=None, username=None, initiated=False, verification=False
    ):
        if not verification:
            self.attached_file_location = attached_file
            self.username = username
            if self.attached_file_location:
                if self.attached_file_location[-4:] == ".pdf":
                    self._work_file()
            elif initiated:
                self.username = input("\nAdd your username here? \n")
                self.attached_file_location = input("\nAdd your PDF file here? \n")
                if self.attached_file_location[-4:] == ".pdf":
                    self._work_file()
                else:
                    raise Exception("Only PDF allowed")
            else:
                raise Exception("Please input sufficient data to process")

    def _work_file(self):
        output_string = StringIO()
        with open(self.attached_file_location, "rb") as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            resource_manager = PDFResourceManager()
            device = TextConverter(resource_manager, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
        text = self._set_clean_text(output_string.getvalue())
        if not self.username or self.username == "":
            self.username = datetime.now()
        file_temp = open(
            f"./temp_files/temp_cv_{self.username}.txt", "w+", encoding="utf-8"
        )
        if text and len(text) > 2:
            file_temp.write(text)
            return text, f"{self.username}.txt"
        elif text:
            try:
                images = convert_from_path(self.attached_file_location)
                final_text = ""
                for pg, img in enumerate(images):
                    final_text += image_to_string(img)
                text = self._set_clean_text(final_text)
                file_temp.write(text)
                return text, self.username
            except Exception as e:
                print(e)
                return None
        else:
            return None

    def _set_clean_text(self, text=None):
        if text:
            return self._clean_text(text)
        else:
            if self.attached_file_location and self.username:
                return self._clean_text(self.read_file())
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
    def _clean_text(output_string):
        text = re.sub("[^A-Za-z0-9@.]+", " ", output_string)
        text = text.replace("\n", "\\n").replace("\t", "\\t")
        return text

    @staticmethod
    def is_pdf(file_path=None):
        if file_path:
            if file_path[-4:] in [".pdf", ".txt"]:
                return True
            else:
                return False
        else:
            return False


class RetrieveSkills:
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        data_test=None,
        username=None,
        file_path=None,
        language="en",
    ):

        nlp = spacy.load("en_core_web_lg")
        skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
        self.file_path = file_path
        self.data_test = data_test
        self.username = username
        self.file_path = file_path
        self.language = language
        if not self.data_test:
            attached = (
                self.file_path
                if _FileManager(verification=True).is_pdf(self.file_path)
                else None
            )
            self.data_text = _FileManager(
                attached_file=attached, username=self.username, initiated=False
            ).read_file(file_path=self.file_path)
        if self.data_test:
            self.skills_set = skill_extractor.annotate(self.data_text)
            if not self.skills_set:
                if client_id is not None and client_secret is not None:
                    self.skills_set = _EMSIAPIManagement(
                        client_id=client_id, client_secret=client_secret
                    ).get_data(language=self.language, text_input=self.data_test)

    def get_skills(self):
        if self.skills_set:
            return self.skills_set
        else:
            return None


class RetrieveContactInformation:
    def __init__(self, attached_file=None, username=None, text=None, region_code="US"):
        self.username = username
        self.attached_file = attached_file
        self.text = text
        self.email = None
        self.phone = None
        self.address = None
        self.region_code = region_code
        status, path_type, path = _check_file(
            username=self.username, file_path=self.attached_file
        )
        if status and path:
            self.file_temp = _read_file(path)

    def get_email(self):
        email_list = []
        email_regex = re.compile(
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))", re.VERBOSE
        )
        if self.text:
            email_groups = email_regex.findall(self.text)
            for group in email_groups:
                email_list.append(group)
            if email_list:
                return email_list[0][0]
            else:
                return None

    def get_phones(self):
        phone_numbers = {}
        for match in phonenumbers.PhoneNumberMatcher(self.text, self.region_code):
            phone_numbers[match] = timezone.time_zones_for_number(match.number)
        return phone_numbers

    def get_address(self):
        parser = pypostalwin.AddressParser()
        return parser.runParser(self.text)

    def get_contact_information(self):
        if self.file_temp:
            self.email = self.get_email()
            self.phone = self.get_phones()
            self.address = self.get_address()
        return self.email, self.phone, self.address


def _check_file(username=None, file_path=None):
    if os.path.exists(f"./temp_files/temp_cv_{username}.txt") and username:
        return True, "generated", f"./temp_files/temp_cv_{username}.txt"
    elif os.path.exists(file_path):
        return True, "inserted", file_path
    else:
        return False, "unknown", None


def _read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as txt_file:
            return txt_file.read()
    except Exception as e:
        print(e)
        return None


_FileManager(attached_file="resume.pdf", username="scanned")
