from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout_view, name='logout'),

    path('products/', views.product_details, name='product_details'),
    path('genre/<int:genre_id>/', views.genre_books, name='genre_books'),

    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('like/<int:book_id>/', views.toggle_like, name='like_book'),
]
