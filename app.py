#!/usr/bin/env python3
"""
Restaurant Billing Software - Main Application Entry Point
"""

import sys
import os
import tkinter as tk
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure imports work regardless of where the script is run
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from ui.main_ui import RestaurantBillingApp

def main():
    """Main entry point for the Restaurant Billing Software"""
    logging.info("=" * 60)
    logging.info("RESTAURANT BILLING SOFTWARE")
    logging.info("=" * 60)
    logging.info("Starting application...")

    # Windows DPI fix
    if sys.platform.startswith("win"):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            logging.warning(f"DPI awareness could not be set: {e}")

    # Initialize the GUI application
    root = tk.Tk()
    root.title("Restaurant Billing Software")
    app = RestaurantBillingApp(root)

    logging.info("Application started successfully!")
    logging.info("=" * 60)
    logging.info("Features available:")
    logging.info("- Dine-In and Takeaway order support")
    logging.info("- Menu management with categories")
    logging.info("- Automatic GST calculation (5%)")
    logging.info("- Discount and payment method support")
    logging.info("- Bill generation and export")
    logging.info("- Sales reporting and analytics")
    logging.info("=" * 60)

    root.mainloop()

if __name__ == "__main__":
    main()
