# Restaurant Billing Software

A complete Python-based restaurant billing system with GUI support for Dine-In and Takeaway modes.

## Features

- **Order Management**: Support for both Dine-In and Takeaway orders
- **Menu Management**: Easy menu item management with categories and pricing
- **Billing System**: Automatic GST calculation (5%) with optional discounts
- **Payment Options**: Cash, Card, and UPI payment methods
- **Reporting**: Daily/weekly/monthly sales reports and analytics
- **Data Storage**: SQLite database for persistent storage
- **Export Options**: CSV and JSON export capabilities

## Project Structure

```
restaurant_billing/
├── app.py                      # Main application entry point
├── db/
│   └── restaurant.db           # SQLite database file
├── data/
│   ├── menu.csv                # Menu items with pricing
│   ├── sample_bills.json       # Sample orders for testing
│   └── sales_report.csv        # Exported reports
├── ui/
│   └── main_ui.py              # Tkinter GUI implementation
├── utils/
│   ├── calculator.py           # GST and discount calculations
│   └── db_utils.py             # Database helper functions
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses built-in Python libraries)

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   # Navigate to your desired directory
   cd /path/to/your/directory
   ```

2. **Run the Application**
   ```bash
   # Navigate to the project directory
   cd restaurant_billing
   
   # Run the main application
   python app.py
   ```

3. **Alternative GUI Launch**
   ```bash
   # Run the GUI directly
   python ui/main_ui.py
   ```

### Usage Guide

#### Initial Setup
1. Launch the application
2. The system will automatically create the database and load sample menu items
3. Start creating orders immediately

#### Creating an Order
1. Select order type (Dine-In or Takeaway)
2. Browse menu items from the list
3. Add items to your order
4. Apply discount if needed
5. Select payment method
6. Generate bill

#### Viewing Reports
1. Click "View Reports" button
2. See daily sales summary
3. Export reports as needed

### Database Schema

#### Menu Table
- `id`: Primary key
- `item_name`: Item name
- `category`: Food category
- `price`: Item price
- `gst`: GST percentage

#### Orders Table
- `id`: Primary key
- `order_type`: Dine-In/Takeaway
- `subtotal`: Subtotal amount
- `gst`: GST amount
- `discount`: Discount amount
- `total`: Final total
- `payment_method`: Cash/Card/UPI
- `order_date`: Order timestamp

#### Order_Items Table
- `id`: Primary key
- `order_id`: Foreign key to orders
- `item_name`: Item name
- `quantity`: Quantity ordered
- `price`: Item price

### Testing

The system includes sample data:
- 10 menu items across different categories
- 5 sample orders with various scenarios
- Test cases for different payment methods and discounts

### Troubleshooting

#### Database Issues
- Ensure write permissions in the `db/` directory
- Database will be created automatically on first run

#### GUI Issues
- Ensure Tkinter is available (comes with standard Python)
- Window size is optimized for 1000x700 resolution

### Development Notes

- All calculations use floating-point arithmetic with rounding to 2 decimal places
- Database transactions ensure data integrity
- Error handling is implemented for all user interactions
- Sample data is loaded automatically for testing purposes

### Future Enhancements

- PDF bill generation
- Email receipts
- Inventory management
- Customer loyalty program
- Multi-language support
- Mobile app version

## License

This project is created as a demonstration of a complete restaurant billing system. Feel free to use and modify as needed.
