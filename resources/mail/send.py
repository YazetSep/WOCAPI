from flask_mail import Mail, Message

def send_reset_email():
    mail = Mail()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=['luisliz2038@gmail.com'])
    msg.body = f'''To reset your password, visit the following link:
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

send_reset_email()
