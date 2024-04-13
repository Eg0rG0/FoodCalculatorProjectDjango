import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
from .models import Food


class FoodConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.receive_json(await self.decode_json(text_data), **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, data, **kwargs):
        sort_by = data.get('sort_by')

        if sort_by in ['fats', 'carbs', 'proteins']:
            user_foods = Food.objects.get_user_foods(self.user).order_by(sort_by)
            sorted_foods = [
                {'food_name': food.food_name, 'fats': food.fats, 'carbs': food.carbs, 'proteins': food.proteins} for
                food in user_foods]

            await self.send_json({'sorted_foods': sorted_foods})


