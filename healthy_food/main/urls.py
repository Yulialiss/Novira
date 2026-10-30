from django.urls import path
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from . import views
@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")
urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/",views.edit_profile_view,name="edit_profile",),
    path("products/search/",views.search_products,name="search_products",),
    path("food/add/",views.add_food_entry,name="add_food_entry",),
    path("food/delete/<int:entry_id>/",views.delete_food_entry,name="delete_food_entry",),
    path("calories/", views.calories_view, name="calories"),
]
