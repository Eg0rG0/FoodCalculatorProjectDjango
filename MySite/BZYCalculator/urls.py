from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),  # http://127.0.0.1:8000
    path("registration/", views.registration, name="registration"),  # http://127.0.0.1:8000/registration
    path("sing_up/", views.sing_up, name="sing_up"),  # http://127.0.0.1:8000/sing_up
    path("personal_account/", views.personal_account, name="personal_account"),
    path("personal_data/", views.personal_data, name="personal_data"),
    path("my_foods/", views.my_foods, name="my_foods"),
    path("my_carts/", views.my_carts, name="my_carts"),
    path("exit/", views.exit_site, name="exit"),
    path("delete_food/<int:food_id>/", views.delete_food, name="delete_food"),
    path("delete_cart/<int:cart_id>/", views.delete_cart, name="delete_cart"),
    path("food_cart_change/<int:cart_id>/", views.food_cart_change, name="food_cart_change"),
    path("delete_food_from_cart/<int:cart_id>/<int:food_id>/", views.delete_food_from_cart, name="delete_food_from_cart"),
    path("calculate/<str:meal_type>/", views.calculate, name="calculate"),
]
