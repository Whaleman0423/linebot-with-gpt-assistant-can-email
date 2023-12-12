# reference: https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

email_account = os.getenv('EMAIL_ACCOUNT')
email_pwd = os.getenv('EMAIL_PWD')


def send_email(subject, message, to_email):
    # Gmail 認證信息
    gmail_user = email_account
    gmail_password = email_pwd

    # 創建郵件物件
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # 郵件正文
    msg.attach(MIMEText(message, 'plain'))

    # 連接到 Gmail 服務器
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # 啟用安全傳輸
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
        print("郵件已成功發送！")
    except Exception as e:
        print(f"發送郵件時出錯: {e}")
