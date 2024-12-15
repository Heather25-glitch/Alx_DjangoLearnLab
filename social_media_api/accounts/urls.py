from django.urls import path, include
from .views import RegisterView, LoginView
from .views import UserFollowViewSet
from rest_framework.routers import DefaultRouter
from . import views
from .views import RegisterView
from .views import LoginView

router = DefaultRouter()
router.register(r'follow', UserFollowViewSet, basename='follow')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    path('api/users/login/', LoginView.as_view(), name='login'),
    path('follow/<int:user_id>/', views.followuser, name='followuser'),
    path('unfollow/<int:user_id>/', views.unfollowuser, name='unfollowuser'),
    path('api/users/register/', RegisterView.as_view(), name='register'),
]