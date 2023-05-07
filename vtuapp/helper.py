from .models import WebsiteConfiguration

def get_config():

    config, _ = WebsiteConfiguration.objects.get_or_create(id=1)

    return config
