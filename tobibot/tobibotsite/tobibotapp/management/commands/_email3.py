#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from platform import python_version

SERVER = 'smtp.yandex.ru'
USER = 'support@citadel-trade.ru'
PASSWORD = 'dml46367dml'
SENDER = 'support@citadel-trade.ru'

def send_email(to, subject, text):
    recipients = [to, ]
    html = f'<html><head></head><body><p>{text}</p></body></html>'

    # filepath = "/var/log/maillog"
    # basename = os.path.basename(filepath)
    # filesize = os.path.getsize(filepath)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'Python script <{SENDER}>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = SENDER
    msg['Return-Path'] = SENDER
    msg['X-Mailer'] = f'Python/{python_version()}'

    part_text = MIMEText(text, 'plain')
    part_html = MIMEText(html, 'html')
    # part_file = MIMEBase('application', 'octet-stream; name="{}"'.format(basename))
    # part_file.set_payload(open(filepath,"rb").read() )
    # part_file.add_header('Content-Description', basename)
    # part_file.add_header('Content-Disposition', 'attachment; filename="{}"; size={}'.format(basename, filesize))
    # encoders.encode_base64(part_file)

    msg.attach(part_text)
    msg.attach(part_html)
    # msg.attach(part_file)

    mail = smtplib.SMTP_SSL(SERVER)
    mail.login(USER, PASSWORD)
    mail.sendmail(SENDER, recipients, msg.as_string())
    mail.quit()