import smtplib
from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys


def send_mail(message_to, message_body):

    message = MIMEMultipart()

    message["From"] = "lighthouse.avesis@gmail.com"

    message["To"] = message_to

    message["Subject"] = "Bugün Hocaların Tarafından Paylaşılan AVESİS Dosyaları"



    message_body= MIMEText(message_body)

    message.attach(message_body)



    address = "lighthouse.avesis@gmail.com"
    password = "avesis_ytu"
    try:
        
        mail = smtplib.SMTP("smtp.gmail.com",587)
        
        mail.ehlo()
        
        mail.starttls()
        
        mail.login(address,password)
        
        mail.sendmail(message["From"],message["To"],message.as_string())
        
        print("mail sent successfully....")

        mail.close()

    except:
        sys.stderr.write("There is an error!")
        sys.stderr.flush()

