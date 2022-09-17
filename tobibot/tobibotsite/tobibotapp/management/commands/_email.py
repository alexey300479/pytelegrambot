# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def send_email(to, text):
    msg = MIMEText(text)
    msg['Subject'] = 'ГУ ТО "Тульский областной бизнес-инкубатор". Подтверждение email'
    msg['From'] = 'biznes-inkubatorto@tularegion.org'
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()