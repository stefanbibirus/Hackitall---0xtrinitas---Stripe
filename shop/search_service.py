#FILE PATH: shop/search_service.py
#================================================================================

"""
Search service module.
This module handles product search functionality.
Replace the mock implementation with your actual search logic.
"""

import random


def search_products_service(query, filters=''):
    """
    Search for products based on query and filters.
    
    Args:
        query (str): The search query from the user
        filters (str): Optional filters (comma-separated)
    
    Returns:
        list: A list of dictionaries containing product information
              Each dict should have: name, description, price, image_url, url
    
    TODO: Replace this mock implementation with your actual search logic
    that returns 6 product links with their details.
    """
    
    # =========================================================================
    # REPLACE THIS SECTION WITH YOUR ACTUAL SEARCH IMPLEMENTATION
    # Your Python script should return 6 links with product information
    # =========================================================================
    
    # Mock data for demonstration
    mock_products = [
        {
            'name': f'{query.title()} - Premium Edition',
            'description': f'High-quality {query} with premium features and excellent build quality.',
            'price': round(random.uniform(29.99, 299.99), 2),
            'image_url': f'https://picsum.photos/seed/{query}1/400/300',
            'url': f'https://example.com/product/{query.replace(" ", "-")}-1',
        },
        {
            'name': f'{query.title()} - Standard Model',
            'description': f'Reliable {query} offering great value for everyday use.',
            'price': round(random.uniform(19.99, 199.99), 2),
            'image_url': f'https://picsum.photos/seed/{query}2/400/300',
            'url': f'https://example.com/product/{query.replace(" ", "-")}-2',
        },
        {
            'name': f'{query.title()} Pro',
            'description': f'Professional-grade {query} for serious enthusiasts.',
            'price': round(random.uniform(99.99, 499.99), 2),
            'image_url': f'https://picsum.photos/seed/{query}3/400/300',
            'url': f'https://example.com/product/{query.replace(" ", "-")}-3',
        },
        {
            'name': f'{query.title()} Lite',
            'description': f'Budget-friendly {query} without compromising on quality.',
            'price': round(random.uniform(9.99, 79.99), 2),
            'image_url': f'https://picsum.photos/seed/{query}4/400/300',
            'url': f'https://example.com/product/{query.replace(" ", "-")}-4',
        },
        {
            'name': f'{query.title()} Deluxe',
            'description': f'Deluxe {query} with all the bells and whistles.',
            'price': round(random.uniform(149.99, 599.99), 2),
            'image_url': f'https://picsum.photos/seed/{query}5/400/300',
            'url': f'https://example.com/product/{query.replace(" ", "-")}-5',
        },
        {
            'name': f'{query.title()} Essential',
            'description': f'Essential {query} covering all basic needs.',
            'price': round(random.uniform(14.99, 99.99), 2),
            'image_url': f'https://picsum.photos/seed/{query}6/400/300',
            'url': f'https://example.com/product/{query.replace(" ", "-")}-6',
        },
    ]
    
    # Apply filters if provided (mock implementation)
    if filters:
        filter_list = [f.strip().lower() for f in filters.split(',')]
        # You can implement actual filter logic here
    
    return mock_products[:6]  # Always return exactly 6 products


# =========================================================================
# EXAMPLE: How to implement with your actual search script
# =========================================================================
#
# def search_products_service(query, filters=''):
#     """
#     Example implementation using an external API or scraper.
#     """
#     import requests
#     
#     # Option 1: Call an API
#     response = requests.get('https://your-api.com/search', params={
#         'q': query,
#         'filters': filters,
#         'limit': 6
#     })
#     data = response.json()
#     
#     products = []
#     for item in data['results']:
#         products.append({
#             'name': item['title'],
#             'description': item['desc'],
#             'price': item['price'],
#             'image_url': item['image'],
#             'url': item['link'],
#         })
#     
#     return products
#
# =========================================================================
# Option 2: Import and call your existing Python script
# =========================================================================
#
# from your_search_module import your_search_function
#
# def search_products_service(query, filters=''):
#     results = your_search_function(query)
#     # Transform results to expected format
#     return results
#