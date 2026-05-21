import os
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    # Send an e-mail to the user
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        # URL dynamically points to frontend password reset page
        'reset_password_url': f"{frontend_url}/reset-password?token={reset_password_token.key}"
    }

    # render email text
    email_html_message = f"Hello {context['username']},<br>Please go to the following link to reset your password: <a href='{context['reset_password_url']}'>{context['reset_password_url']}</a>"
    email_plaintext_message = f"Hello {context['username']},\n\nPlease go to the following link to reset your password: {context['reset_password_url']}"

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for Madruguinha",
        # message:
        email_plaintext_message,
        # from:
        "noreply@madruguinha.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
