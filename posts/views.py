from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages

from .models import Post, Comment, Like, Follow, Profile


# =========================================================
# HOME
# =========================================================

def home(request):

    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")

        action = request.POST.get("action")
        current_user = request.user
        username = current_user.username


        # =====================================================
        # CREATE POST
        # =====================================================

        if action == "post":

            content = request.POST.get(
                "content",
                ""
            ).strip()

            if content:

                Profile.objects.get_or_create(
                    user=current_user
                )

                Post.objects.create(
                    username=username,
                    content=content
                )

            return redirect("home")


        # =====================================================
        # COMMENT
        # =====================================================

        elif action == "comment":

            content = request.POST.get(
                "content",
                ""
            ).strip()

            post_id = request.POST.get(
                "post_id"
            )

            if content and post_id:

                try:

                    post = Post.objects.get(
                        id=post_id
                    )

                    Comment.objects.create(
                        post=post,
                        username=username,
                        content=content
                    )

                except Post.DoesNotExist:
                    pass

            return redirect("home")


        # =====================================================
        # LIKE / UNLIKE
        # =====================================================

        elif action == "like":

            post_id = request.POST.get(
                "post_id"
            )

            if post_id:

                try:

                    post = Post.objects.get(
                        id=post_id
                    )

                    existing_like = Like.objects.filter(
                        post=post,
                        username=username
                    ).first()


                    if existing_like:

                        # UNLIKE
                        existing_like.delete()

                        if post.likes > 0:
                            post.likes -= 1

                        post.save()


                    else:

                        # LIKE
                        Like.objects.create(
                            post=post,
                            username=username
                        )

                        post.likes += 1

                        post.save()


                except Post.DoesNotExist:
                    pass

            return redirect("home")


        # =====================================================
        # FOLLOW / UNFOLLOW
        # =====================================================

        elif action == "follow":

            following_username = request.POST.get(
                "following",
                ""
            ).strip()

            if following_username:

                try:

                    following_user = User.objects.get(
                        username=following_username
                    )

                    if current_user != following_user:

                        Profile.objects.get_or_create(
                            user=following_user
                        )

                        existing_follow = Follow.objects.filter(
                            follower=current_user,
                            following=following_user
                        ).first()


                        if existing_follow:

                            # UNFOLLOW
                            existing_follow.delete()

                        else:

                            # FOLLOW
                            Follow.objects.create(
                                follower=current_user,
                                following=following_user
                            )


                except User.DoesNotExist:
                    pass

            return redirect("home")


    # =====================================================
    # POSTS
    # =====================================================

    posts = Post.objects.all().order_by(
        "-created_at"
    )


    # =====================================================
    # CURRENT USER
    # =====================================================

    if request.user.is_authenticated:

        current_username = request.user.username

    else:

        current_username = ""


    # =====================================================
    # CHECK LIKES
    # =====================================================

    for post in posts:

        if current_username:

            post.is_liked = Like.objects.filter(
                post=post,
                username=current_username
            ).exists()

        else:

            post.is_liked = False


    # =====================================================
    # USERS
    # =====================================================

    users = User.objects.all().order_by(
        "username"
    )


    suggested_users = []


    for user in users:

        # Don't show yourself
        if request.user.is_authenticated:

            if user.id == request.user.id:
                continue


        # Don't show Guest
        if user.username == "Guest":
            continue


        profile_obj, created = Profile.objects.get_or_create(
            user=user
        )


        is_followed = False


        if request.user.is_authenticated:

            is_followed = Follow.objects.filter(
                follower=request.user,
                following=user
            ).exists()


        suggested_users.append({

            "name": user.username,

            "bio":
                profile_obj.bio
                if profile_obj.bio
                else "Welcome to Velora ✨",

            "is_followed": is_followed

        })


    # =====================================================
    # RENDER HOME
    # =====================================================

    return render(
        request,
        "posts/home.html",
        {
            "posts": posts,
            "suggested_users": suggested_users
        }
    )


# =========================================================
# SIGNUP
# =========================================================

def signup(request):

    if request.user.is_authenticated:
        return redirect("home")


    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        password2 = request.POST.get(
            "password2",
            ""
        )


        # =====================================================
        # EMPTY FIELDS
        # =====================================================

        if not username or not password or not password2:

            messages.error(
                request,
                "Please fill all fields."
            )

            return render(
                request,
                "posts/signup.html"
            )


        # =====================================================
        # USERNAME LENGTH
        # =====================================================

        if len(username) < 3:

            messages.error(
                request,
                "Username must be at least 3 characters."
            )

            return render(
                request,
                "posts/signup.html"
            )


        # =====================================================
        # USERNAME EXISTS
        # =====================================================

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists. Please choose another."
            )

            return render(
                request,
                "posts/signup.html"
            )


        # =====================================================
        # PASSWORD MATCH
        # =====================================================

        if password != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "posts/signup.html"
            )


        # =====================================================
        # PASSWORD LENGTH
        # =====================================================

        if len(password) < 6:

            messages.error(
                request,
                "Password must be at least 6 characters."
            )

            return render(
                request,
                "posts/signup.html"
            )


        # =====================================================
        # CREATE USER
        # =====================================================

        user = User.objects.create_user(
            username=username,
            password=password
        )


        # =====================================================
        # CREATE PROFILE
        # =====================================================

        Profile.objects.get_or_create(
            user=user
        )


        # =====================================================
        # LOGIN AUTOMATICALLY
        # =====================================================

        auth_login(
            request,
            user
        )


        messages.success(
            request,
            "Account created successfully! Welcome to Velora ✨"
        )


        return redirect("home")


    return render(
        request,
        "posts/signup.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")


    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )


        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "posts/login.html"
            )


        user = authenticate(
            request,
            username=username,
            password=password
        )


        if user is not None:

            Profile.objects.get_or_create(
                user=user
            )

            auth_login(
                request,
                user
            )

            return redirect("home")


        messages.error(
            request,
            "Invalid username or password."
        )


    return render(
        request,
        "posts/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    auth_logout(
        request
    )

    return redirect("login")


# =========================================================
# PROFILE
# =========================================================

def profile(request, username):

    user = User.objects.filter(
        username=username
    ).first()


    # =====================================================
    # USER NOT FOUND
    # =====================================================

    if not user:

        return render(
            request,
            "posts/profile.html",
            {
                "user_not_found": True,
                "username": username
            }
        )


    # =====================================================
    # HANDLE FOLLOW / UNFOLLOW FROM PROFILE
    # =====================================================

    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")


        action = request.POST.get(
            "action"
        )


        if action == "follow":

            if request.user != user:

                existing_follow = Follow.objects.filter(
                    follower=request.user,
                    following=user
                ).first()


                if existing_follow:

                    existing_follow.delete()

                else:

                    Follow.objects.get_or_create(
                        follower=request.user,
                        following=user
                    )


            return redirect(
                "profile",
                username=username
            )


    # =====================================================
    # PROFILE
    # =====================================================

    profile_obj, created = Profile.objects.get_or_create(
        user=user
    )


    # =====================================================
    # POSTS
    # =====================================================

    posts = Post.objects.filter(
        username=username
    ).order_by(
        "-created_at"
    )


    # =====================================================
    # FOLLOWERS COUNT
    # =====================================================

    followers_count = Follow.objects.filter(
        following=user
    ).count()


    # =====================================================
    # FOLLOWING COUNT
    # =====================================================

    following_count = Follow.objects.filter(
        follower=user
    ).count()


    # =====================================================
    # FOLLOW STATUS
    # =====================================================

    is_followed = False


    if request.user.is_authenticated:

        if request.user != user:

            is_followed = Follow.objects.filter(
                follower=request.user,
                following=user
            ).exists()


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "posts/profile.html",
        {
            "profile_user": user,
            "profile": profile_obj,
            "posts": posts,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_followed": is_followed
        }
    )


# =========================================================
# FOLLOWERS LIST
# =========================================================

def followers(request, username):

    user = User.objects.filter(
        username=username
    ).first()


    if not user:

        return render(
            request,
            "posts/user_list.html",
            {
                "title": "Followers",
                "username": username,
                "users": []
            }
        )


    # =====================================================
    # FOLLOW / UNFOLLOW FROM LIST
    # =====================================================

    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")


        action = request.POST.get(
            "action"
        )

        target_username = request.POST.get(
            "following",
            ""
        ).strip()


        if action == "follow" and target_username:

            target_user = User.objects.filter(
                username=target_username
            ).first()


            if target_user and target_user != request.user:

                existing_follow = Follow.objects.filter(
                    follower=request.user,
                    following=target_user
                ).first()


                if existing_follow:

                    existing_follow.delete()

                else:

                    Follow.objects.create(
                        follower=request.user,
                        following=target_user
                    )


        return redirect(
            "followers",
            username=username
        )


    # =====================================================
    # GET FOLLOWERS
    # =====================================================

    follow_records = Follow.objects.filter(
        following=user
    ).select_related(
        "follower"
    )


    user_data = []


    for item in follow_records:

        person = item.follower

        is_followed = False


        if request.user.is_authenticated:

            is_followed = Follow.objects.filter(
                follower=request.user,
                following=person
            ).exists()


        user_data.append({

            "user": person,

            "is_followed": is_followed

        })


    return render(
        request,
        "posts/user_list.html",
        {
            "title": "Followers",
            "username": username,
            "users": user_data
        }
    )


# =========================================================
# FOLLOWING LIST
# =========================================================

def following(request, username):

    user = User.objects.filter(
        username=username
    ).first()


    if not user:

        return render(
            request,
            "posts/user_list.html",
            {
                "title": "Following",
                "username": username,
                "users": []
            }
        )


    # =====================================================
    # FOLLOW / UNFOLLOW FROM LIST
    # =====================================================

    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")


        action = request.POST.get(
            "action"
        )

        target_username = request.POST.get(
            "following",
            ""
        ).strip()


        if action == "follow" and target_username:

            target_user = User.objects.filter(
                username=target_username
            ).first()


            if target_user and target_user != request.user:

                existing_follow = Follow.objects.filter(
                    follower=request.user,
                    following=target_user
                ).first()


                if existing_follow:

                    # UNFOLLOW
                    existing_follow.delete()

                else:

                    # FOLLOW
                    Follow.objects.create(
                        follower=request.user,
                        following=target_user
                    )


        return redirect(
            "following",
            username=username
        )


    # =====================================================
    # GET FOLLOWING
    # =====================================================

    follow_records = Follow.objects.filter(
        follower=user
    ).select_related(
        "following"
    )


    user_data = []


    for item in follow_records:

        person = item.following

        is_followed = False


        if request.user.is_authenticated:

            is_followed = Follow.objects.filter(
                follower=request.user,
                following=person
            ).exists()


        user_data.append({

            "user": person,

            "is_followed": is_followed

        })


    return render(
        request,
        "posts/user_list.html",
        {
            "title": "Following",
            "username": username,
            "users": user_data
        }
    )