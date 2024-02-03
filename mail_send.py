# ライブラリ設定
import smtplib
from email.mime.text import MIMEText
import os
 
def send_mail(message: str):
    #  メール情報の設定
    from_email = os.environ["GMAIL_SEND_ADDRESS"]
    to_email = os.environ["GMAIL_SEND_ADDRESS"]
    cc_mail = ''
    mail_title = 'pachi_batchの実行結果'

    
    #  MIMEオブジェクトでメールを作成
    msg = MIMEText(message, 'plain')
    msg['Subject'] = mail_title
    msg['To'] = to_email
    msg['From'] = from_email
    msg['cc'] = cc_mail
    
    #  サーバを指定してメールを送信する
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_password = os.environ["GMAIL_APP_PASSWORD"]
    
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(from_email, smtp_password)
    server.send_message(msg)
    server.quit()
