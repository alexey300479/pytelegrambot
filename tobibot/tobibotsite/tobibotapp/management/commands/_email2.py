
import smtplib as smtp
from getpass import getpass
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
email = input('введите почту: \n')
password = getpass('введите пароль: ')
dest_email = input('введите адрес получателя: \n')
subject = input('тема письма: \n')
email_text = input('текст письма: \n' )

message = f'''
From: {email}
To: {dest_email}
Subject: {subject}

{email_text}'
'''

server = smtp.SMTP_SSL('smtp.yandex.ru', 587)
server.set_debuglevel(1)
server.ehlo(email)
server.starttls(context=context)
server.ehlo()
server.login(email, password)
server.auth_plain()
server.sendmail(email, dest_email, message)
server.quit()