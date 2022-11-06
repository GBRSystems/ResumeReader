import re

text = "Software Engineer with over 10+ years of experience in the Healthcare domain is seeking a fulltime position " \
       "in the field of Software Engineering.44 West 22nd Street, New York, NY 12345. info@qwikresume.com. " \
       "linkedin.com/qwikresume "

# 44 West 22nd Street, New York, NY 12345.
# 1737 Marshville Road, Alabama

# regexp = "[0-9]{1,3} .+, .+, [A-Z]{2} [0-9]{5}"
# address = re.findall("([0-9]{1,5} .+, .+, [A-Z]{1,20})", text)
# address = re.findall("([0-9]{1,5} .+, [A-z])", text)
address = re.compile(r'\d{1,7}( \w+){1,6} (nd|st|street|ave|avenue|ln|lane), (apt|unit|apartment)[\., ]+.*[\. ,]+(NY|AZ|CA|CO|NH)[\. ,]\d{5}')
address_text = re.findall(address, text)
print(address_text)
