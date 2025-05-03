from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import JsonResponse
from .models import Book, User, Cart, CartItem, Order, OrderItem
from .forms import BookForm, RegistrationForm, UserUpdateForm, LoginForm


def check_email(request):
    email = request.GET.get('email', '')
    data = {'is_taken': User.objects.filter(email=email).exists()}
    if data['is_taken']:
        data['error_message'] = 'Этот email уже зарегистрирован.'
    return JsonResponse(data)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('book_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    client_ip = request.META.get('REMOTE_ADDR')
    login_attempts_key = f'login_attempts_{client_ip}'
    login_attempts = cache.get(login_attempts_key, 0)

    if login_attempts >= 5:
        messages.error(request, 'Слишком много попыток входа. Попробуйте снова через 10 минут.')
        return render(request, 'login.html', {'form': LoginForm()})

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                cache.delete(login_attempts_key)
                messages.success(request, 'Вход выполнен успешно!')
                next_page = request.GET.get('next')
                return redirect(next_page) if next_page else redirect('book_list')
            else:
                login_attempts += 1
                cache.set(login_attempts_key, login_attempts, timeout=600)
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            login_attempts += 1
            cache.set(login_attempts_key, login_attempts, timeout=600)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('book_list')


def book_list(request):
    books = Book.objects.all().order_by('id')
    author_filter = request.GET.get('author')
    if author_filter:
        books = books.filter(author__icontains=author_filter)
    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    is_authorized = request.user.is_authenticated
    is_admin = is_authorized and request.user.role == 'admin'
    return render(request, 'book_list.html', {'books': page_obj, 'is_authorized': is_authorized, 'is_admin': is_admin})


@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно добавлена.')
            return redirect('book_list')
        else:
            messages.error(request, 'Ошибка при добавлении книги.')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_create_admin(request):
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен.')
        return redirect('book_list')
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно добавлена.')
            return redirect('book_list')
        else:
            messages.error(request, 'Ошибка при добавлении книги.')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_update(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен.')
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно обновлена.')
            return redirect('book_list')
        else:
            messages.error(request, 'Ошибка при обновлении книги.')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})


@login_required
def book_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен.')
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга успешно удалена.')
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
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{book.title} добавлена в корзину.")
    return redirect('book_list')


def cart_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_id = request.session.session_key
        cart = Cart.objects.filter(session_id=session_id).first() if session_id else None

    cart_items = cart.items.all() if cart else []
    total = sum(item.get_total_price() for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def create_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart')

    total_price = sum(item.get_total_price() for item in cart.items.all())
    order = Order.objects.create(user=request.user, total_price=total_price)

    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            book=cart_item.book,
            quantity=cart_item.quantity,
            price=cart_item.book.price
        )

    cart.items.all().delete()
    messages.success(request, "Заказ успешно оформлен!")
    return redirect('order_history')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})