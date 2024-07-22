from django.urls import path
from .views import ObtainJWTView, RefreshJWTView, SignUpView

urlpatterns = [
    path('login/', ObtainJWTView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', RefreshJWTView.as_view(), name='refresh_token_obtain_pair'),
    path('signup/', SignUpView.as_view(), name='signup')
]
