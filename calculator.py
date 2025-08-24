# GST, discount, total calculation logic for the Restaurant Billing Software

def calculate_total(price, quantity, gst_rate=0.05, discount=0):
    """
    Calculate the total amount including GST and discount
    
    Args:
        price (float): Price per item
        quantity (int): Number of items
        gst_rate (float): GST rate as decimal (default 5% = 0.05)
        discount (float): Discount amount
    
    Returns:
        dict: Dictionary containing subtotal, gst, discount, and total
    """
    subtotal = price * quantity
    gst = subtotal * gst_rate
    total = subtotal + gst - discount
    
    return {
        'subtotal': round(subtotal, 2),
        'gst': round(gst, 2),
        'discount': round(discount, 2),
        'total': round(total, 2)
    }

def calculate_discount_percentage(subtotal, discount_percentage):
    """
    Calculate discount amount based on percentage
    
    Args:
        subtotal (float): Subtotal amount
        discount_percentage (float): Discount percentage
    
    Returns:
        float: Discount amount
    """
    return subtotal * (discount_percentage / 100)

def format_currency(amount):
    """
    Format amount as currency string
    
    Args:
        amount (float): Amount to format
    
    Returns:
        str: Formatted currency string
    """
    return f"${amount:.2f}"

def calculate_order_totals(order_items, gst_rate=0.05, discount=0):
    """
    Calculate totals for entire order
    
    Args:
        order_items (list): List of tuples (item_name, quantity, price)
        gst_rate (float): GST rate as decimal
        discount (float): Discount amount
    
    Returns:
        dict: Order totals
    """
    subtotal = sum(price * qty for _, qty, price in order_items)
    gst = subtotal * gst_rate
    total = subtotal + gst - discount
    
    return {
        'subtotal': round(subtotal, 2),
        'gst': round(gst, 2),
        'discount': round(discount, 2),
        'total': round(total, 2)
    }
