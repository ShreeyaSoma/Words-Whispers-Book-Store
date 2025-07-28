from django.contrib import admin
from .models import Genre, Book, CartItem, Order

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'price', 'stock')
    list_filter = ('genre',)
    search_fields = ('title', 'author')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'payment_method', 'created_at')
