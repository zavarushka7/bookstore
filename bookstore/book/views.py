from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Book, User, Cart, CartItem
from .forms import BookForm, RegistrationForm, UserUpdateForm, LoginForm  # <---- ВАЖНО: импортируйте LoginForm
from django.core.paginator import Paginator
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('book_list')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Создаем экземпляр формы
        if form.is_valid():  # Проверяем, валидна ли форма
            username = form.cleaned_data['username']  # Получаем очищенные данные
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_page = request.GET.get('next')
                return redirect(next_page) if next_page else redirect('book_list')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            # Форма невалидна, добавляем сообщения об ошибках
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LoginForm()  # Создаем пустую форму для GET-запроса
    return render(request, 'login.html', {'form': form})  # Передаем форму в шаблон

@login_required
def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_list.html', {'page_obj': page_obj})


def logout_view(request):
    logout(request)
    return redirect('book_list')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_create_admin(request):
    if request.user.role != 'admin':
        return redirect('book_list')
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_update(request, pk):
    if request.user.role != 'admin':
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('book_list')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{book.title} добавлена в корзину.")
    return redirect('book_list')


def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    is_authorized = request.user.is_authenticated
    is_admin = is_authorized and request.user.role == 'admin'
    return render(request, 'book_list.html', {'books': page_obj, 'is_authorized': is_authorized, 'is_admin': is_admin})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('book_list')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Создаем экземпляр формы
        if form.is_valid():  # Проверяем, валидна ли форма
            username = form.cleaned_data['username']  # Получаем очищенные данные
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_page = request.GET.get('next')
                return redirect(next_page) if next_page else redirect('book_list')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            # Форма невалидна, добавляем сообщения об ошибках
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LoginForm()  # Создаем пустую форму для GET-запроса
    return render(request, 'login.html', {'form': form})  # Передаем форму в шаблон

def logout_view(request):
    logout(request)
    return redirect('book_list')


@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_create_admin(request):
    if request.user.role != 'admin':
        return redirect('book_list')
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_update(request, pk):
    if request.user.role != 'admin':
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{book.title} добавлена в корзину.")
    return redirect('book_list')

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first() # или get() если уверены, что корзина всегда есть
    if cart:
        cart_items = CartItem.objects.filter(cart=cart)
    else:
        cart_items = []  # Пустая корзина

    total = sum(item.book.price * item.quantity for item in cart_items)  # Рассчитываем общую сумму

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

