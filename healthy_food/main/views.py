
from decimal import Decimal, InvalidOperation
from . import views
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import UserProfileForm, RegistrationForm
from .models import UserProfile, Product, FoodEntry


def home(request):
    return render(request, "main/home.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request,  "Вітаємо в NOVIRA! Ваш обліковий запис створено."  )
            return redirect("profile")
    else:
        form = RegistrationForm()

    return render(
        request,"main/register.html", {"form": form} )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(request, "Ви успішно увійшли!")

            next_url = request.POST.get("next", "")

            if (
                next_url
                and next_url.startswith("/")
                and not next_url.startswith("//")
            ):
                return redirect(next_url)

            return redirect("profile")
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "main/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        }
    )


@login_required
def edit_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Особисті дані успішно збережено!"
            )
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(
        request,
        "main/edit_profile.html",
        {
            "form": form,
            "profile": profile,
        }
    )


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    today = timezone.localdate()

    entries = FoodEntry.objects.filter(
        user=request.user,
        date=today
    ).select_related("product")

    meals = [
        {"key": "breakfast", "name": "Сніданок"},
        {"key": "snack", "name": "Перекус"},
        {"key": "lunch", "name": "Обід"},
        {"key": "dinner", "name": "Вечеря"},
    ]

    for meal in meals:
        meal_entries = entries.filter(
            meal_type=meal["key"]
        )

        meal["entries"] = meal_entries
        meal["calories"] = sum(
            (entry.calories_total for entry in meal_entries),
            Decimal("0")
        )

    totals = {
        "calories": sum(
            (entry.calories_total for entry in entries),
            Decimal("0")
        ),
        "protein": sum(
            (entry.protein_total for entry in entries),
            Decimal("0")
        ),
        "fat": sum(
            (entry.fat_total for entry in entries),
            Decimal("0")
        ),
        "carbs": sum(
            (entry.carbs_total for entry in entries),
            Decimal("0")
        ),
    }

    daily_goal = (
        profile.daily_calorie_goal
        or profile.calculate_daily_calories()
        or 2000
    )

    query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            name__icontains=query
        )

    products = products.order_by("name")[:30]

    context = {
        "profile": profile,
        "meals": meals,
        "totals": totals,
        "daily_goal": daily_goal,
        "today": today,
        "search_query": query,
        "products": products if query else [],
    }

    return render(
        request,
        "main/profile.html",
        context
    )


@login_required
def calories_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    bmr = profile.calculate_bmr()
    daily_calories = profile.calculate_daily_calories()

    context = {
        "profile": profile,
        "bmr": bmr,
        "daily_calories": daily_calories,
    }

    return render(
        request,
        "main/calories.html",
        context
    )


@login_required
@require_POST
def add_food_entry(request):
    product_id = request.POST.get("product_id")
    meal_type = request.POST.get("meal_type")
    grams_raw = request.POST.get("grams", "")

    allowed_meals = {"breakfast", "snack", "lunch", "dinner"}

    if meal_type not in allowed_meals:
        return JsonResponse({
            "success": False,
            "message": "Вибери правильний прийом їжі."
        }, status=400)

    try:
        grams = Decimal(grams_raw)
    except (InvalidOperation, ValueError):
        return JsonResponse({
            "success": False,
            "message": "Введи правильну кількість грамів."
        }, status=400)

    if not grams.is_finite() or grams <= 0 or grams > 10000:
        return JsonResponse({
            "success": False,
            "message": "Кількість має бути від 1 до 10000 грамів."
        }, status=400)

    try:
        product = Product.objects.get(
            pk=product_id,
            is_active=True
        )
    except (Product.DoesNotExist, ValueError, TypeError):
        return JsonResponse({
            "success": False,
            "message": "Продукт не знайдено."
        }, status=404)

    entry = FoodEntry.objects.create(
        user=request.user,
        product=product,
        date=timezone.localdate(),
        meal_type=meal_type,
        grams=grams,
    )

    return JsonResponse({
        "success": True,
        "message": "Продукт успішно додано!",
        "id": entry.id,
        "name": entry.product.name,
        "grams": float(entry.grams),
        "calories": float(entry.calories_total),
        "protein": float(entry.protein_total),
        "fat": float(entry.fat_total),
        "carbs": float(entry.carbs_total),
    })


@login_required
@require_POST
def delete_food_entry(request, entry_id):
    entry = get_object_or_404(
        FoodEntry,
        pk=entry_id,
        user=request.user,
        date=timezone.localdate()
    )

    entry.delete()

    messages.success(
        request,
        "Продукт видалено."
    )

    return redirect("profile")

@login_required
@require_GET
def search_products(request):
    query = request.GET.get("q", "").strip().casefold()

    products = Product.objects.filter(is_active=True).order_by("name")

    # Пошук українських назв незалежно від регістру
    if query:
        products = [
            product
            for product in products
            if query in product.name.casefold()
        ][:30]
    else:
        products = list(products[:30])

    return JsonResponse({
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "calories": float(product.calories),
                "protein": float(product.protein),
                "fat": float(product.fat),
                "carbs": float(product.carbs),
            }
            for product in products
        ]
    })
