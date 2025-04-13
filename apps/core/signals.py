import logging

from decouple import config
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_user(sender, **kwargs):
    email = config("INITIAL_USER_EMAIL", default=None)
    password = config("INITIAL_USER_PASSWORD", default=None)

    User = get_user_model()
    if User.objects.count() == 0:
        if not email or not password:
            logger.warning("initial user not configured")
            return
    else:
        return

    username = email.split("@")[0]
    logger.info("creating initial user")
    User.objects.create_superuser(username=username, password=password, email=email)
