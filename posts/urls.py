from django.urls import path
from . import views


urlpatterns = [

    # Home
    path(
        "",
        views.home,
        name="home"
    ),

    # Authentication
    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # Profile
    path(
        "profile/<str:username>/",
        views.profile,
        name="profile"
    ),

    # Followers
    path(
        "profile/<str:username>/followers/",
        views.followers,
        name="followers"
    ),

    # Following
    path(
        "profile/<str:username>/following/",
        views.following,
        name="following"
    ),
]