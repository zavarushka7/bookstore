from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.book_create, name='book_create'),
    path('create_admin/', views.book_create_admin, name='book_create_admin'),
    path('<int:pk>/update/', views.book_update, name='book_update'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('profile/', views.profile, name='profile'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),

]