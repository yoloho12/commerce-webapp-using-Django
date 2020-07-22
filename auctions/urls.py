from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<str:auction_id>", views.listing, name="listing"),
    path("create", views.create, name="create"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.categories_view, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("announce", views.announce, name="announce")
]
