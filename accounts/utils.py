from django.core.mail import EmailMessage
from django.conf import settings
def send_email(subject, body, to_email_list):
    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        email = EmailMessage(
            subject,
            body,
            from_email,
            to_email_list
        )
        email.send()
        return True
    except Exception as e:
        print(e)
        return False