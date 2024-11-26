from django.core.mail import EmailMultiAlternatives


def send_email_verification(user, verification_code):
        text_content = f"""Your verification code is: {verification_code}
        Verification code will expire after 2 minutes"""
        message = EmailMultiAlternatives(
            subject="Verification Code",
            body=text_content,
            to=[user.email],
            from_email="abubakrrahmatullayev1001@gmail.com"   
        )
        message.send()