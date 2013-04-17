from flask.ext.mail import Message
from app import mail
from flask import flash

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body

    try:
        mail.send(msg)
    except:
        flash('Es gab ein Problem beim Versand einer E-Mail.', 'error')
        pass
