import re
from commonregex import CommonRegex


parsed_text = CommonRegex("""John, please get that article on www.linkedin.com to me by 5:00PM 
                               on Jan 9th 2012. 4:00 would be ideal, actually. If you have any 
                               questions, You can reach me at (519)-236-2723x341 or get in touch with
                               my associate at harold.smith@gmail.com.44 West 22nd Street, New York, NY 12345. 
                               info@qwikresume.com. 1737 Marshville Road, Alabama. 
                               300 Srimath Anagarika Road, Colombo""")

ttime = parsed_text.street_addresses
tzip = parsed_text.emails
print(ttime)
print(tzip)

# text = "Software Engineer with over 10+ years of experience in the Healthcare domain is seeking a fulltime position
# " \ "in the field of Software Engineering.44 West 22nd Street, New York, NY 12345. info@qwikresume.com. " \
# "linkedin.com/qwikresume "

# 44 West 22nd Street, New York, NY 12345.
# 1737 Marshville Road, Alabama

# regexp = "[0-9]{1,3} .+, .+, [A-Z]{2} [0-9]{5}"
# address = re.findall("([0-9]{1,5} .+, .+, [A-Z]{1,20})", text)
# address = re.findall("([0-9]{1,5} .+, [A-z])", text)
# address = re.compile(r'\d{1,7}( \w+){1,6} (nd|st|street|ave|avenue|ln|lane), (apt|unit|apartment)[\., ]+.*[\. ,'
#                      r']+(NY|AZ|CA|CO|NH)[\. ,]\d{5}')
# address_text = re.findall(address, text)
# print(address_text)
