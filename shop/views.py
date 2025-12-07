#FILE PATH: shop/views.py
#================================================================================

import json
import stripe
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User, Product, CartItem, Order, OrderItem
from .search_service import search_products_service
from django.shortcuts import render
from .search_service import search_products_service


stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    """Home page with search functionality."""
    return render(request, 'shop/index.html')


def search_products(request):
    """Search products using the search service and return JSON results."""
    query = request.GET.get('q', '').strip()
    filters = request.GET.get('filters', '')
    
    if not query:
        return JsonResponse({'products': [], 'error': 'Please enter a search term'})
    
    try:
        # Get products from search service
        products_data = search_products_service(query, filters)
        
        # Save products to database and return them
        products = []
        for item in products_data[:6]:  # Limit to 6 results
            product, created = Product.objects.get_or_create(
                source_url=item.get('url', ''),
                defaults={
                    'name': item.get('name', 'Unknown Product'),
                    'description': item.get('description', ''),
                    'price': Decimal(str(item.get('price', 0))),
                    'image_url': item.get('image_url', ''),
                    'source_data': item,
                }
            )
            if not created:
                # Update existing product
                product.name = item.get('name', product.name)
                product.price = Decimal(str(item.get('price', product.price)))
                product.image_url = item.get('image_url', product.image_url)
                product.save()
            
            products.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'image_url': product.image_url,
                'source_url': product.source_url,
            })
        
        return JsonResponse({'products': products})
    
    except Exception as e:
        return JsonResponse({'products': [], 'error': str(e)})


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back!')
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'shop/login.html')


def signup_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')
    
    return render(request, 'shop/signup.html')


def logout_view(request):
    """Log out the user."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def cart_view(request):
    """Display the shopping cart."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.total_price for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    cart_count = CartItem.objects.filter(user=request.user).count()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart',
        'cart_count': cart_count,
    })


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.total_price for item in cart_items)
    cart_count = cart_items.count()
    
    return JsonResponse({
        'success': True,
        'total': str(total),
        'cart_count': cart_count,
    })


@login_required
@require_POST
def update_cart_quantity(request, item_id):
    """Update cart item quantity."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    
    data = json.loads(request.body)
    quantity = int(data.get('quantity', 1))
    
    if quantity < 1:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.total_price for item in cart_items)
    
    return JsonResponse({
        'success': True,
        'item_total': str(cart_item.total_price) if quantity >= 1 else '0',
        'cart_total': str(total),
    })


@login_required
def checkout(request):
    """Checkout page."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')
    
    total = sum(item.total_price for item in cart_items)
    
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@login_required
@require_POST
def create_checkout_session(request):
    """Create a Stripe checkout session."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    if not cart_items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)
    
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                    'description': item.product.description[:500] if item.product.description else 'Product',
                },
                'unit_amount': int(item.product.price * 100),  # Stripe uses cents
            },
            'quantity': item.quantity,
        })
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
            metadata={
                'user_id': request.user.id,
            }
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def payment_success(request):
    """Payment success page."""
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Create order
            cart_items = CartItem.objects.filter(user=request.user).select_related('product')
            total = sum(item.total_price for item in cart_items)
            
            order = Order.objects.create(
                user=request.user,
                total=total,
                stripe_payment_id=session.payment_intent,
                status='paid'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, 'Payment successful! Your order has been placed.')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
    
    return render(request, 'shop/payment_success.html')


def payment_cancel(request):
    """Payment cancelled page."""
    messages.warning(request, 'Payment was cancelled.')
    return render(request, 'shop/payment_cancel.html')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # You should set up a webhook secret in production
    # endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Payment was successful, order is already created in payment_success
    
    return HttpResponse(status=200)


@login_required
def order_history(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'shop/orders.html', {'orders': orders})