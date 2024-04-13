from django.urls import re_path
from .consumers import FoodConsumer

websocket_urlpatterns = [
    re_path(r"ws/my_foods/$", FoodConsumer.as_asgi()),
]
