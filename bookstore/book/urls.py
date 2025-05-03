from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.book_list, name='book_list'),
    path('book/create/', views.book_create, name='book_create'),
    path('book/create/admin/', views.book_create_admin, name='book_create_admin'),
    path('book/<int:pk>/update/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('profile/', views.profile, name='profile'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/history/', views.order_history, name='order_history'),
    path('check-email/', views.check_email, name='check_email'),
]