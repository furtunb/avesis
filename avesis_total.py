from avesis import *
from avesis_mail import *


day = today()

docs = academic_control(day)

length = lengthOfStudents()

for thing in range(length):
    all_stuff = message_body(day, docs)
    message_text = all_stuff["text"]
    is_empty = all_stuff["emptiness"]
    message_to = all_stuff["mail"]
    if not is_empty: 
        send_mail(message_to, message_text, mail, password)