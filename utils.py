"""
Utility functions for Hotel Nico BlackBox AI Manager
Helper functions for date handling, formatting, ID generation, etc.
"""

import re
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
import random
import string


def generate_booking_id(prefix: str = "BK") -> str:
    """
    Generate a unique booking ID
    Format: BK-YYYYMMDD-XXXX (e.g., BK-20251028-A1B2)
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_str}-{random_str}"


def generate_expense_id(prefix: str = "EX") -> str:
    """
    Generate a unique expense ID
    Format: EX-YYYYMMDD-XXXX
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_str}-{random_str}"


def generate_feedback_id(prefix: str = "FB") -> str:
    """
    Generate a unique feedback ID
    Format: FB-YYYYMMDD-XXXX
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_str}-{random_str}"


def generate_campaign_id(prefix: str = "CM") -> str:
    """
    Generate a unique campaign ID
    Format: CM-YYYYMMDD-XXXX
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_str}-{random_str}"


def format_currency(amount: float, currency: str = "₹") -> str:
    """
    Format amount as currency
    Example: 1500.50 -> ₹1,500.50
    """
    return f"{currency}{amount:,.2f}"


def format_date(date_obj: date, format_str: str = "%d %b %Y") -> str:
    """
    Format date object to string
    Default format: 28 Oct 2025
    """
    return date_obj.strftime(format_str)


def format_datetime(datetime_obj: datetime, format_str: str = "%d %b %Y %I:%M %p") -> str:
    """
    Format datetime object to string
    Default format: 28 Oct 2025 02:30 PM
    """
    return datetime_obj.strftime(format_str)


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string to date object
    Supports formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
    """
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def calculate_nights(check_in: date, check_out: date) -> int:
    """Calculate number of nights between check-in and check-out"""
    return (check_out - check_in).days


def get_date_range(start_date: date, end_date: date) -> List[date]:
    """Get list of dates between start and end date (inclusive)"""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def is_valid_phone(phone: str) -> bool:
    """
    Validate Indian phone number
    Accepts: 10 digits, +91 prefix, spaces, hyphens
    """
    # Remove spaces and hyphens
    phone = re.sub(r'[\s\-]', '', phone)
    
    # Check for +91 prefix
    if phone.startswith('+91'):
        phone = phone[3:]
    elif phone.startswith('91') and len(phone) == 12:
        phone = phone[2:]
    
    # Check if 10 digits
    return bool(re.match(r'^[6-9]\d{9}$', phone))


def is_valid_email(email: str) -> bool:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_phone(phone: str) -> str:
    """
    Format phone number to standard format
    Example: 9876543210 -> +91 98765 43210
    """
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Remove +91 or 91 prefix if present
    if phone.startswith('91') and len(phone) > 10:
        phone = phone[-10:]
    
    # Format as +91 XXXXX XXXXX
    if len(phone) == 10:
        return f"+91 {phone[:5]} {phone[5:]}"
    
    return phone


def calculate_occupancy_percentage(occupied_rooms: int, total_rooms: int) -> float:
    """Calculate occupancy percentage"""
    if total_rooms == 0:
        return 0.0
    return (occupied_rooms / total_rooms) * 100


def get_occupancy_status(occupancy_percentage: float) -> Tuple[str, str]:
    """
    Get occupancy status and emoji
    Returns: (status, emoji)
    """
    if occupancy_percentage >= 90:
        return ("Excellent", "🟢")
    elif occupancy_percentage >= 80:
        return ("Good", "🟢")
    elif occupancy_percentage >= 60:
        return ("Moderate", "🟡")
    elif occupancy_percentage >= 40:
        return ("Low", "🟠")
    else:
        return ("Critical", "🔴")


def get_payment_status_emoji(status: str) -> str:
    """Get emoji for payment status"""
    emojis = {
        "PAID": "✅",
        "PARTIAL": "⚠️",
        "PENDING": "❌",
        "REFUNDED": "↩️"
    }
    return emojis.get(status, "❓")


def get_room_status_emoji(status: str) -> str:
    """Get emoji for room status"""
    emojis = {
        "AVAILABLE": "✅",
        "OCCUPIED": "🔴",
        "CLEANING": "🧹",
        "MAINTENANCE": "🔧",
        "RESERVED": "📅"
    }
    return emojis.get(status, "❓")


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_greeting() -> str:
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"


def get_today() -> date:
    """Get today's date"""
    return date.today()


def get_tomorrow() -> date:
    """Get tomorrow's date"""
    return date.today() + timedelta(days=1)


def get_yesterday() -> date:
    """Get yesterday's date"""
    return date.today() - timedelta(days=1)


def days_until(target_date: date) -> int:
    """Calculate days until target date"""
    return (target_date - date.today()).days


def is_weekend(check_date: date) -> bool:
    """Check if date is weekend (Saturday or Sunday)"""
    return check_date.weekday() in [5, 6]


def get_week_dates() -> Tuple[date, date]:
    """Get start and end date of current week (Monday to Sunday)"""
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_dates() -> Tuple[date, date]:
    """Get start and end date of current month"""
    today = date.today()
    start = date(today.year, today.month, 1)
    
    # Get last day of month
    if today.month == 12:
        end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    return start, end


def format_list_items(items: List[str], bullet: str = "•") -> str:
    """Format list items with bullets"""
    return "\n".join([f"{bullet} {item}" for item in items])


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def average(values: List[float]) -> float:
    """Calculate average of list of values"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename
