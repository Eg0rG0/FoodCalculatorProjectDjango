from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from BZYCalculator.forms import CustomUserRegistrationForm, CustomUserSingUpForm, FoodCreationForm, \
    CustomUserChangeForm, FoodCartCreationForm, FoodCartChangeForm
from BZYCalculator.models import Food, CustomUser, FoodCart


def index(request):
    menu = [{"title": "Вход", "url_name": "sing_up"},
            {"title": "Регистрация", "url_name": "registration"}]
    return render(request, "BZYCalculator/index.html", context={'menu': menu})


def registration(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = CustomUserRegistrationForm()
    return render(request, "BZYCalculator/registration.html", {'form': form})


def sing_up(request):
    if request.method == 'POST':
        form = CustomUserSingUpForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
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
    if request.method == 'POST':
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
            food_cart.foods.add(*request.POST.getlist('foods'))
            return redirect('my_carts')
        else:
            print(form.errors)
    else:
        form = FoodCartCreationForm(request.POST or None)

    carts = FoodCart.objects.filter(user=request.user)
    available_foods = Food.objects.filter(user=request.user)

    return render(request, 'BZYCalculator/my_carts.html', {
        'form': form,
        'available_foods': available_foods,
        'carts': carts
    })


def my_foods(request):
    if request.method == "POST":
        form = FoodCreationForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.user = request.user
            food.save()
            redirect('my_foods')
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = FoodCreationForm()

    sort_by = request.GET.get('sort_by')
    if sort_by:
        user_foods = request.user.foods.all().order_by(sort_by)
        if request.GET.get('sort_direction') == 'desc':
            user_foods = user_foods.reverse()
    else:
        user_foods = request.user.foods.all()

    return render(request, "BZYCalculator/my_foods.html", {"form": form, "user_foods": user_foods})


def delete_food(request, food_id):
    food = get_object_or_404(Food, pk=food_id)
    food.delete()
    return redirect('my_foods')


def delete_cart(request, cart_id):
    cart = get_object_or_404(FoodCart, pk=cart_id)
    if request.method == 'POST':
        cart.delete()
        return redirect('my_carts')
    return render(request, 'BZYCalculator/delete_cart.html', {'cart': cart})


def food_cart_change(request, cart_id):
    cart = get_object_or_404(FoodCart, pk=cart_id)
    user_products = Food.objects.filter(user=request.user)
    available_foods = user_products.exclude(pk__in=cart.foods.all())

    if request.method == 'POST':
        form = FoodCartChangeForm(request.POST)
        if form.is_valid():
            food_ids = form.cleaned_data['foods']
            foods_to_add = Food.objects.filter(pk__in=food_ids)
            cart.foods.add(*foods_to_add)
            return redirect('food_cart_change', cart_id=cart_id)
    else:
        form = FoodCartChangeForm()
    return render(request, "BZYCalculator/food_cart_change.html", {'cart': cart,
                                                                   'available_foods': available_foods,
                                                                   'form': form})


def delete_food_from_cart(request, cart_id, food_id):
    cart = get_object_or_404(FoodCart, pk=cart_id)
    food = get_object_or_404(Food, pk=food_id)
    cart.foods.remove(food)
    return redirect("food_cart_change", cart_id=cart_id)


def exit_site(request):
    logout(request)
    return redirect('home')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Bro, не могу найти такую страницу<h1>")


