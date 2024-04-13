from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import BZYCalculator.routing

application = ProtocolTypeRouter({
    "http": URLRouter(
        BZYCalculator.routing.websocket_urlpatterns
    )
})