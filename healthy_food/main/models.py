from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("female", "Жіноча"),
        ("male", "Чоловіча"),
    ]

    ACTIVITY_CHOICES = [
        ("low", "Мінімальна активність"),
        ("light", "Низька активність"),
        ("moderate", "Помірна активність"),
        ("high", "Висока активність"),
        ("very_high", "Дуже висока активність"),
    ]

    GOAL_CHOICES = [
        ("lose", "Зменшення маси тіла"),
        ("maintain", "Підтримання маси тіла"),
        ("gain", "Збільшення маси тіла"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    age = models.PositiveSmallIntegerField("Вік", null=True, blank=True)
    gender = models.CharField("Стать", max_length=10, choices=GENDER_CHOICES, blank=True)
    height = models.DecimalField("Зріст (см)", max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField("Маса тіла (кг)", max_digits=5, decimal_places=2, null=True, blank=True)
    activity_level = models.CharField("Рівень активності", max_length=20, choices=ACTIVITY_CHOICES, default="low")
    goal = models.CharField("Мета харчування", max_length=10, choices=GOAL_CHOICES, default="maintain")

    daily_calorie_goal = models.PositiveIntegerField("Добова ціль калорій", null=True, blank=True)
    daily_protein_goal = models.DecimalField("Ціль білків (г)", max_digits=7, decimal_places=2, null=True, blank=True)
    daily_fat_goal = models.DecimalField("Ціль жирів (г)", max_digits=7, decimal_places=2, null=True, blank=True)
    daily_carbs_goal = models.DecimalField("Ціль вуглеводів (г)", max_digits=7, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField("Дата створення", auto_now_add=True)
    updated_at = models.DateTimeField("Останнє оновлення", auto_now=True)

    def calculate_bmr(self):
        if not all([self.age, self.gender, self.height, self.weight]):
            return None

        weight = float(self.weight)
        height = float(self.height)

        if weight <= 0 or height <= 0 or self.age <= 0:
            return None

        result = 10 * weight + 6.25 * height - 5 * self.age

        if self.gender == "male":
            result += 5
        elif self.gender == "female":
            result -= 161
        else:
            return None

        return round(result)

    def calculate_daily_calories(self):
        bmr = self.calculate_bmr()

        if bmr is None:
            return None

        activity_factors = {
            "low": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "high": 1.725,
            "very_high": 1.9,
        }

        calories = bmr * activity_factors[self.activity_level]

        goal_factors = {
            "lose": 0.85,
            "maintain": 1.0,
            "gain": 1.1,
        }

        return round(calories * goal_factors[self.goal])

    def __str__(self):
        return f"Профіль: {self.user}"


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("vegetables", "Овочі"),
        ("fruits", "Фрукти"),
        ("dairy", "Молочні продукти"),
        ("meat", "М'ясо"),
        ("fish", "Риба та морепродукти"),
        ("grains", "Крупи та зернові"),
        ("bakery", "Хліб і випічка"),
        ("eggs", "Яйця"),
        ("nuts", "Горіхи та насіння"),
        ("other", "Інше"),
    ]

    name = models.CharField("Назва продукту", max_length=150)
    category = models.CharField("Категорія", max_length=20, choices=CATEGORY_CHOICES, default="other")

    calories = models.DecimalField("Калорійність (ккал/100 г)", max_digits=8, decimal_places=2)
    protein = models.DecimalField("Білки (г/100 г)", max_digits=7, decimal_places=2)
    fat = models.DecimalField("Жири (г/100 г)", max_digits=7, decimal_places=2)
    carbs = models.DecimalField("Вуглеводи (г/100 г)", max_digits=7, decimal_places=2)

    description = models.TextField("Опис", blank=True)
    is_active = models.BooleanField("Доступний у каталозі", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"

    def __str__(self):
        return self.name


class FoodEntry(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Сніданок"),
        ("lunch", "Обід"),
        ("dinner", "Вечеря"),
        ("snack", "Перекус"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="food_entries",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="food_entries",
        verbose_name="Продукт",
    )
    date = models.DateField("Дата", default=timezone.localdate)
    meal_type = models.CharField("Приймання їжі", max_length=10, choices=MEAL_CHOICES)
    grams = models.DecimalField("Маса порції (г)", max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def calories_total(self):
        return self.product.calories * self.grams / Decimal("100")

    @property
    def protein_total(self):
        return self.product.protein * self.grams / Decimal("100")

    @property
    def fat_total(self):
        return self.product.fat * self.grams / Decimal("100")

    @property
    def carbs_total(self):
        return self.product.carbs * self.grams / Decimal("100")

    class Meta:
        ordering = ["date", "created_at"]
        verbose_name = "Запис харчового щоденника"
        verbose_name_plural = "Записи харчового щоденника"

    def __str__(self):
        return f"{self.product.name} — {self.grams} г"
