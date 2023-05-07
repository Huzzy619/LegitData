from django.shortcuts import render
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
# Create your views here.

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter