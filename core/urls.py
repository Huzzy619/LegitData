from django.urls import path, include
from .views import FacebookLogin

urlpatterns = [
    path("rest-auth/facebook/", FacebookLogin.as_view(), name="fb_login"),
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/registration/', include('dj_rest_auth.registration.urls'))
]
