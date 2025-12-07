#FILE PATH: shop/context_processors.py
#================================================================================

"""
Context processors for the shop app.
These add variables to every template context.
"""

from .models import CartItem


def cart_count(request):
    """Add cart item count to template context."""
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_count': count}