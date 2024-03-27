from mimi.accounts.mails.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, current_site_domain):
    subject = "Activate your account"
    message = render_to_string(
        "accounts/activation_email.html",
        {
            "user": user,
            "domain": current_site_domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )

    email = EmailMessage(subject, message, to=[user.email])
    email.send()
