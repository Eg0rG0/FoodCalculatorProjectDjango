from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("The username field must be set")

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser


class FoodManager(models.Manager):
    def get_user_foods(self, user):
        return self.filter(user=user)


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=100, null=True)
    fats = models.FloatField(null=True)
    carbs = models.FloatField(null=True)
    proteins = models.FloatField(null=True)
    calories = models.FloatField(null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="foods", default=None)

    objects = FoodManager()


class FoodCartManager(models.Manager):
    pass


class FoodCart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="carts")
    foods = models.ManyToManyField(Food)
    name = models.CharField(max_length=100, default="MyCart")

    objects = FoodCartManager()


class MealManager(models.Manager):
    pass


class Meal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True)
    weight = models.FloatField(null=True)
    meal_type = models.CharField(max_length=10, null=True)
    date = models.DateField(null=True)

    objects = MealManager()


