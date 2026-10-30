
from django.contrib import admin

from .models import UserProfile, Product, FoodEntry


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "age",
        "gender",
        "weight",
        "goal",
        "activity_level",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("gender", "goal", "activity_level")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "calories",
        "protein",
        "fat",
        "carbs",
        "is_active",
    )
    search_fields = ("name",)
    list_filter = ("category", "is_active")
    list_editable = ("is_active",)


@admin.register(FoodEntry)
class FoodEntryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "date",
        "meal_type",
        "grams",
    )
    search_fields = ("user__username", "product__name")
    list_filter = ("date", "meal_type")
    date_hierarchy = "date"
