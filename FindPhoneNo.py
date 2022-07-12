import re

# a = "Senior Software Engineer ROBERT SMITH Phone 123 456 78 99 Email info@qwikresume.com Website www.qwikresume.com LinkedIn linkedin.com qwikresume Address 1737 Marshville Road Alabama. Objective Software Engineer with over 10 years of experience in the Healthcare domain is seeking a full time position in the field of Software Engineering. Skills Java Groovy Web Services JavaScript JQuery CSS HTML XML C .NET VB 6.0 VB.NET C C VC RDBMS Oracle SQL MS Access Sybase Domain Knowledge Windows 7 MS Windows Work Experience Senior Software Engineer Intermountain Healthcare November 2007 Present Implementing an innovative rendering tool for the companys new product in order to help out team members with auto generated flow diagrams for simple to complex projects. Storing these diagrams in project folder per the architecture standards for user access. Storing the flows in the database for updating querying the flows at any given time. Generating a web services JAR that contains classes to access it from a given WSDL for complex financial healthcare structures HIPPA 276 277 countrywide standard. Incorporated this JAR into EGATE to call the web service by sending in the input parameters via Services approx and getting responses for various situations which had to be developed to handle simple to complex subscriber dependent test cases through data structures algorithms. Using the JUnit to test various situations working closely with users business analysts QA to provide input test cases for select health customers functional technical guides. Creating training document for the department to train members on the web service implementations. Software Engineer ABC Corp 2006 2007 Wrote code to power a globalized network of radar sensors. Wrote well designed testable and efficient code that met the technical requirements. Participated in a highly collaborative team environment contributed to all phases of the development lifecycle using Agile SCRUM methodologies. Assisted in the troubleshooting of code defects and deployment of timely fixes. Delivered the projects on time and with attention to quality. Developed sql statements to pull data from the database using sql server. Fixed over a hundred bugs in javascript css oracle pl sql c asp razor template code. Education Masters in Computational Science Minor in Business And Management April 2005 to May 2006 University Of Utah Masters in Computer Applications December 2003 IGNOU This Free Resume Template is the copyright of Qwikresume.com. Usage Guidelines"


class phone_number:

    def __init__(self, a):
        self.a = a

    def validate_phone_no(self):
        test = self.a
        # reg = re.compile(r".*?(\(?\d{3})? ?[\.-]? ?\d{3} ?[\.-]? ?\d{4}).*?", re.test)
        # reg = re.compile(r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})")
        reg = re.compile(r"[\+\d]?(\d{2,3}[-\.\s]??\d{2,3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})")
        phone_no = re.findall(reg, test)
        # print(phone_no)
        return phone_no
        # "(?:^|\s)(((?:\+|0{2})(?:49|43|33)[-\. ]?|0)([1-9]\d{1,2}[-\. ]?|\([1-9]\d{1,2}\)[-\. ]?)(\d{6,9}|\d{2,3}[-\. ]\d{4,6}))"


test = "SMITH Phone (123) 456 7899 Email info@qwikresume.com Website"
obj = phone_number(test)
number = obj.validate_phone_no()
print(number)
