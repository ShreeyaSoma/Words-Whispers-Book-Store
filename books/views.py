from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Genre, Book, Order

# Home page
def index(request):
    return render(request, 'index.html')

# Register
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('index')
    return render(request, 'register.html')

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Product Details View
def product_details(request):
    genres = Genre.objects.all()
    books_by_genre = {genre: Book.objects.filter(genre=genre) for genre in genres}
    trending_books = Book.objects.order_by('-likes')[:5]
    liked_books = request.session.get('liked_books', [])
    message_list = messages.get_messages(request)
    return render(request, 'product_details.html', {
        'genres': genres,
        'books_by_genre': books_by_genre,
        'trending_books': trending_books,
        'liked_books': liked_books,
        'messages': message_list,
    })

# Genre-based books
def genre_books(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    books = Book.objects.filter(genre=genre)
    liked_books = request.session.get('liked_books', [])
    return render(request, 'genre_books.html', {
        'genre': genre,
        'books': books,
        'liked_books': liked_books,
    })

# Toggle like/unlike a book
def toggle_like(request, book_id):
    liked_books = request.session.get('liked_books', [])
    if book_id in liked_books:
        liked_books.remove(book_id)
    else:
        liked_books.append(book_id)
        try:
            book = Book.objects.get(id=book_id)
            book.likes += 1
            book.save()
        except Book.DoesNotExist:
            pass
    request.session['liked_books'] = liked_books
    return redirect(request.META.get('HTTP_REFERER', 'product_details'))

# Add book to cart (session-based)
def add_to_cart(request, book_id):
    cart = request.session.get('cart', {})
    cart[str(book_id)] = cart.get(str(book_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Book added to cart.")
    return redirect('view_cart')

# View cart
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for book_id, quantity in cart.items():
        try:
            book = Book.objects.get(id=int(book_id))
            subtotal = book.price * quantity
            cart_items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Book.DoesNotExist:
            continue
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

# Remove book from cart
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

# Checkout
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for book_id, quantity in cart.items():
        try:
            book = Book.objects.get(id=int(book_id))
            subtotal = book.price * quantity
            cart_items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Book.DoesNotExist:
            continue

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        gift_wrap = request.POST.get('giftwrap') == 'yes'
        payment_method = request.POST.get('payment', '')

        if not name or not email or not address or not payment_method:
            messages.error(request, "Please fill in all the required details.")
            return render(request, 'checkout.html', {
                'order_placed': False,
                'cart_items': cart_items,
                'total': total,
                'name': name,
                'email': email,
                'address': address,
                'gift_wrap': gift_wrap,
                'payment_method': payment_method
            })

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            address=address,
            gift_wrap=gift_wrap,
            payment_method=payment_method
        )

        for book_id, quantity in cart.items():
            try:
                book = Book.objects.get(id=int(book_id))
                for _ in range(quantity):
                    order.books.add(book)
            except Book.DoesNotExist:
                continue

        request.session['cart'] = {}

        return render(request, 'checkout.html', {
            'order_placed': True,
            'customer_name': name,
            'total': total
        })

    # If GET, show form and cart
    return render(request, 'checkout.html', {
        'order_placed': False,
        'cart_items': cart_items,
        'total': total
    })
