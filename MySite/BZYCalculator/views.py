import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import CustomUserRegistrationForm, CustomUserSingUpForm, FoodCreationForm, \
    CustomUserChangeForm, FoodCartCreationForm, FoodCartChangeForm, AddMealForm
from .models import Food, CustomUser, FoodCart, Meal


def index(request):
    if request.user.is_authenticated:
        breakfast_info = get_meal_info(request.user, "Breakfast")
        lunch_info = get_meal_info(request.user, "Lunch")
        dinner_info = get_meal_info(request.user, "Dinner")
        snack_info = get_meal_info(request.user, "Snack")
        all_day_info = get_meal_info(request.user)
        context = {
            "breakfast_info": breakfast_info,
            "lunch_info": lunch_info,
            "dinner_info": dinner_info,
            "snack_info": snack_info,
            "all_day_info": all_day_info
        }
    else:
        context = {
            "breakfast_info": 0,
            "lunch_info": 0,
            "dinner_info": 0,
            "snack_info": 0,
        }

    return render(request, "BZYCalculator/index.html", context)


def get_meal_info(user, meal_type=None) -> {str: float}:
    if meal_type:
        meals = Meal.objects.filter(user=user, meal_type=meal_type, date=timezone.now().date())
    else:
        meals = Meal.objects.filter(user=user,date=timezone.now().date())
    total_proteins = sum(meal.food.proteins * meal.weight for meal in meals) / 100
    total_fats = sum(meal.food.fats * meal.weight for meal in meals) / 100
    total_carbs = sum(meal.food.carbs * meal.weight for meal in meals) / 100
    total_calories = sum(meal.food.calories * meal.weight for meal in meals) / 100

    return {
        "total_proteins": round(total_proteins, 2),
        "total_fats": round(total_fats, 2),
        "total_carbs": round(total_carbs, 2),
        "total_calories": round(total_calories, 2),
    }


def registration(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = CustomUserRegistrationForm()
    return render(request, "BZYCalculator/registration.html", {"form": form})


def sing_up(request):
    if request.method == "POST":
        form = CustomUserSingUpForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserSingUpForm()

    return render(request, "BZYCalculator/sing_up.html", {"form": form})


def personal_account(request):
    menu = [
        {"title": "Мои данные", "url_name": "sing_up"},
        {"title": "Мои блюда", "url_name": "my_foods"},
        {"title": "Мои подборки", "url_name": "my_carts"},
        {"title": "выход", "url_name:": "exit"},
    ]

    return render(request, "BZYCalculator/personal_account.html", {"form": menu})


def personal_data(request):
    user = request.user
    form = CustomUserChangeForm(instance=user)
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("personal_data")
    return render(request, "BZYCalculator/personal_data.html", {"form": form})


def my_carts(request):
    if request.method == "POST":
        form = FoodCartCreationForm(request.POST)
        if form.is_valid():
            food_cart = form.save(commit=False)
            food_cart.user = request.user
            food_cart.save()
            food_cart.foods.add(*request.POST.getlist("foods"))
            return redirect("my_carts")
        else:
            print(form.errors)
    else:
        form = FoodCartCreationForm(request.POST or None)

    carts = FoodCart.objects.filter(user=request.user)
    available_foods = Food.objects.filter(user=request.user)

    return render(request, "BZYCalculator/my_carts.html", {
        "form": form,
        "available_foods": available_foods,
        "carts": carts
    })


def my_foods(request):
    if request.method == "POST":
        form = FoodCreationForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.user = request.user
            food.calories = (form.cleaned_data["proteins"] * 4.1 + form.cleaned_data["fats"] * 9 +
                             form.cleaned_data["carbs"] * 4.1)
            food.save()
            redirect("my_foods")
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = FoodCreationForm()

    sort_by = request.GET.get("sort_by")
    if sort_by:
        user_foods = request.user.foods.all().order_by(sort_by)
        if request.GET.get("sort_direction") == "desc":
            user_foods = user_foods.reverse()
    else:
        user_foods = request.user.foods.all()

    return render(request, "BZYCalculator/my_foods.html", {"form": form, "user_foods": user_foods})


def delete_food(request, food_id):
    food = get_object_or_404(Food, pk=food_id)
    food.delete()
    return redirect("my_foods")


def delete_cart(request, cart_id):
    cart = get_object_or_404(FoodCart, pk=cart_id)
    if request.method == "POST":
        cart.delete()
        return redirect("my_carts")
    return render(request, "BZYCalculator/delete_cart.html", {"cart": cart})


def food_cart_change(request, cart_id):
    cart = get_object_or_404(FoodCart, pk=cart_id)
    user_products = Food.objects.filter(user=request.user)
    available_foods = user_products.exclude(pk__in=cart.foods.all())

    if request.method == "POST":
        form = FoodCartChangeForm(request.POST)
        if form.is_valid():
            food_ids = form.cleaned_data["foods"]
            foods_to_add = Food.objects.filter(pk__in=food_ids)
            cart.foods.add(*foods_to_add)
            return redirect("food_cart_change", cart_id=cart_id)
    else:
        form = FoodCartChangeForm()
    return render(request, "BZYCalculator/food_cart_change.html", {"cart": cart,
                                                                   "available_foods": available_foods,
                                                                   "form": form})


def delete_food_from_cart(request, cart_id, food_id):
    cart = get_object_or_404(FoodCart, pk=cart_id)
    food = get_object_or_404(Food, pk=food_id)
    cart.foods.remove(food)
    return redirect("food_cart_change", cart_id=cart_id)


def calculate(request, meal_type):
    if not request.user.is_authenticated:
        return redirect("sign_up")

    meals = Meal.objects.filter(user=request.user, meal_type=meal_type, date=timezone.now().date())

    if request.method == "POST":
        form = AddMealForm(request.POST, user=request.user, meal_type=meal_type, date=timezone.now().date())
        if form.is_valid():
            form.save()
            return redirect("calculate", meal_type=meal_type)
    else:
        form = AddMealForm(user=request.user, meal_type=meal_type)

    context = {
        "meal_type": meal_type,
        "meals": meals,
        "form": form,
    }

    return render(request, "BZYCalculator/calculate.html", context)


def exit_site(request):
    logout(request)
    return redirect("home")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Bro, не могу найти такую страницу<h1>")


