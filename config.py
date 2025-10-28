"""
Configuration module for Hotel Nico BlackBox AI Manager
Manages all environment variables and system constants
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for Hotel Nico AI Manager"""
    
    # Hotel Information
    HOTEL_NAME = "Hotel Nico"
    HOTEL_LOCATION = "Phoenix Bay, Port Blair"
    TOTAL_ROOMS = 10  # Adjust based on actual room count
    TARGET_OCCUPANCY = 80  # Target occupancy percentage
    
    # Pricing
    LOCAL_RATE = 799  # ₹799 for local guests (Port Blair, Neil Islanders)
    STANDARD_RATE = 1500  # Standard rate for tourists
    WALK_IN_RATE = 1200  # Walk-in guest rate
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # For automated reports
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    GOOGLE_SHEETS_NAME = os.getenv("GOOGLE_SHEETS_NAME", "Hotel Nico Register")
    
    # WhatsApp Business Configuration (Optional)
    WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
    WHATSAPP_PHONE_NUMBER = os.getenv("WHATSAPP_PHONE_NUMBER")
    
    # Instagram Configuration (Optional)
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    
    # Scheduled Report Times
    MORNING_REPORT_TIME = "08:00"  # 8 AM
    AFTERNOON_CHECK_TIME = "14:00"  # 2 PM
    EVENING_REPORT_TIME = "21:00"  # 9 PM
    
    # Alert Thresholds
    LOW_OCCUPANCY_THRESHOLD = 60  # Alert if occupancy falls below 60%
    HIGH_EXPENSE_THRESHOLD = 5000  # Alert if daily expenses exceed ₹5000
    
    # File Paths
    GUEST_FORMS_DIR = os.getenv("GUEST_FORMS_DIR", "./guest_forms")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")
    MARKETING_ASSETS_DIR = os.getenv("MARKETING_ASSETS_DIR", "./marketing_assets")
    
    # Marketing Templates
    WHATSAPP_TEMPLATE_LOCAL = """
🏨 *Hotel Nico - Special Local Offer!*

📍 Phoenix Bay, Port Blair

💰 *₹799 Only* for Port Blair & Neil Island Residents!

✨ What you get:
• Clean & Comfortable Rooms
• 24/7 Hot Water
• Free WiFi
• Prime Location

📞 Book Now: {phone}
📱 WhatsApp: {whatsapp}

*Limited Time Offer!*
    """
    
    INSTAGRAM_CAPTION_TEMPLATE = """
🌴 Escape to comfort at Hotel Nico! 🏨

Located in the heart of Phoenix Bay, Port Blair 📍

Special rates for locals: ₹799 only! 💰

#HotelNico #PortBlair #AndamanIslands #TravelAndaman #LocalStay #AffordableStay #PhoenixBay #IslandLife #AndamanTourism #StayLocal

Book now! DM for details 📩
    """
    
    # Guest Categories
    GUEST_CATEGORIES = {
        "LOCAL": "Port Blair/Neil Islander",
        "TOURIST": "Tourist/Visitor",
        "WALK_IN": "Walk-in Guest",
        "REPEAT": "Repeat Guest",
        "CORPORATE": "Corporate Guest"
    }
    
    # Room Status
    ROOM_STATUS = {
        "AVAILABLE": "Available",
        "OCCUPIED": "Occupied",
        "CLEANING": "Under Cleaning",
        "MAINTENANCE": "Under Maintenance",
        "RESERVED": "Reserved"
    }
    
    # Payment Status
    PAYMENT_STATUS = {
        "PENDING": "Pending",
        "PARTIAL": "Partial Payment",
        "PAID": "Fully Paid",
        "REFUNDED": "Refunded"
    }
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        
        if not cls.GOOGLE_SHEETS_SPREADSHEET_ID:
            errors.append("GOOGLE_SHEETS_SPREADSHEET_ID is not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def get_room_rate(cls, guest_category):
        """Get room rate based on guest category"""
        rates = {
            "LOCAL": cls.LOCAL_RATE,
            "TOURIST": cls.STANDARD_RATE,
            "WALK_IN": cls.WALK_IN_RATE,
            "REPEAT": cls.LOCAL_RATE,  # Give repeat guests local rate
            "CORPORATE": cls.STANDARD_RATE
        }
        return rates.get(guest_category, cls.STANDARD_RATE)


# Create necessary directories
os.makedirs(Config.GUEST_FORMS_DIR, exist_ok=True)
os.makedirs(Config.REPORTS_DIR, exist_ok=True)
os.makedirs(Config.MARKETING_ASSETS_DIR, exist_ok=True)
