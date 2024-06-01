import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, email_config):
    msg = MIMEMultipart()
    msg['From'] = email_config['from_email']
    msg['To'] = ", ".join(email_config['to_emails'])
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['username'], email_config['password'])
        text = msg.as_string()
        server.sendmail(email_config['from_email'], email_config['to_emails'], text)
        server.quit()
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")
