"""
Data models for Hotel Nico BlackBox AI Manager
Defines structures for bookings, guests, rooms, expenses, and feedback
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum


class GuestCategory(Enum):
    """Guest category enumeration"""
    LOCAL = "LOCAL"
    TOURIST = "TOURIST"
    WALK_IN = "WALK_IN"
    REPEAT = "REPEAT"
    CORPORATE = "CORPORATE"


class RoomStatus(Enum):
    """Room status enumeration"""
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    CLEANING = "CLEANING"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


@dataclass
class Guest:
    """Guest information model"""
    name: str
    phone: str
    id_type: str  # Aadhar, Passport, Driving License, etc.
    id_number: str
    address: str
    category: GuestCategory
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    is_repeat_guest: bool = False
    previous_stays: int = 0
    
    def to_dict(self) -> Dict:
        """Convert guest to dictionary"""
        return {
            "name": self.name,
            "phone": self.phone,
            "id_type": self.id_type,
            "id_number": self.id_number,
            "address": self.address,
            "category": self.category.value,
            "email": self.email or "",
            "emergency_contact": self.emergency_contact or "",
            "is_repeat_guest": self.is_repeat_guest,
            "previous_stays": self.previous_stays
        }


@dataclass
class Room:
    """Room information model"""
    room_number: str
    status: RoomStatus
    floor: int
    room_type: str = "Standard"  # Standard, Deluxe, Suite
    max_occupancy: int = 2
    amenities: List[str] = field(default_factory=list)
    last_cleaned: Optional[datetime] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert room to dictionary"""
        return {
            "room_number": self.room_number,
            "status": self.status.value,
            "floor": self.floor,
            "room_type": self.room_type,
            "max_occupancy": self.max_occupancy,
            "amenities": ",".join(self.amenities),
            "last_cleaned": self.last_cleaned.isoformat() if self.last_cleaned else "",
            "notes": self.notes
        }


@dataclass
class Booking:
    """Booking information model"""
    booking_id: str
    guest: Guest
    room_number: str
    check_in_date: date
    check_out_date: date
    number_of_guests: int
    room_rate: float
    total_amount: float
    advance_paid: float
    balance_amount: float
    payment_status: PaymentStatus
    booking_source: str = "Direct"  # Direct, WhatsApp, Instagram, Walk-in, OTA
    special_requests: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    checked_in: bool = False
    checked_out: bool = False
    
    def calculate_nights(self) -> int:
        """Calculate number of nights"""
        return (self.check_out_date - self.check_in_date).days
    
    def calculate_total(self) -> float:
        """Calculate total amount based on nights and rate"""
        return self.room_rate * self.calculate_nights()
    
    def update_balance(self):
        """Update balance amount"""
        self.balance_amount = self.total_amount - self.advance_paid
        
        # Update payment status
        if self.balance_amount <= 0:
            self.payment_status = PaymentStatus.PAID
        elif self.advance_paid > 0:
            self.payment_status = PaymentStatus.PARTIAL
        else:
            self.payment_status = PaymentStatus.PENDING
    
    def to_dict(self) -> Dict:
        """Convert booking to dictionary"""
        return {
            "booking_id": self.booking_id,
            "guest_name": self.guest.name,
            "guest_phone": self.guest.phone,
            "guest_id": self.guest.id_number,
            "guest_category": self.guest.category.value,
            "room_number": self.room_number,
            "check_in_date": self.check_in_date.isoformat(),
            "check_out_date": self.check_out_date.isoformat(),
            "nights": self.calculate_nights(),
            "number_of_guests": self.number_of_guests,
            "room_rate": self.room_rate,
            "total_amount": self.total_amount,
            "advance_paid": self.advance_paid,
            "balance_amount": self.balance_amount,
            "payment_status": self.payment_status.value,
            "booking_source": self.booking_source,
            "special_requests": self.special_requests,
            "created_at": self.created_at.isoformat(),
            "checked_in": self.checked_in,
            "checked_out": self.checked_out
        }


@dataclass
class Expense:
    """Daily expense tracking model"""
    expense_id: str
    date: date
    category: str  # Utilities, Supplies, Maintenance, Staff, Food, Other
    description: str
    amount: float
    paid_to: str
    payment_method: str = "Cash"  # Cash, UPI, Bank Transfer
    receipt_number: Optional[str] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert expense to dictionary"""
        return {
            "expense_id": self.expense_id,
            "date": self.date.isoformat(),
            "category": self.category,
            "description": self.description,
            "amount": self.amount,
            "paid_to": self.paid_to,
            "payment_method": self.payment_method,
            "receipt_number": self.receipt_number or "",
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Feedback:
    """Guest feedback model"""
    feedback_id: str
    booking_id: str
    guest_name: str
    rating: int  # 1-5 stars
    review_text: str
    source: str = "Direct"  # Direct, Google, Instagram, WhatsApp
    date: date = field(default_factory=date.today)
    responded: bool = False
    response_text: Optional[str] = None
    public: bool = True
    
    def to_dict(self) -> Dict:
        """Convert feedback to dictionary"""
        return {
            "feedback_id": self.feedback_id,
            "booking_id": self.booking_id,
            "guest_name": self.guest_name,
            "rating": self.rating,
            "review_text": self.review_text,
            "source": self.source,
            "date": self.date.isoformat(),
            "responded": self.responded,
            "response_text": self.response_text or "",
            "public": self.public
        }


@dataclass
class DailyReport:
    """Daily operations report model"""
    report_date: date
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    occupancy_percentage: float
    check_ins: int
    check_outs: int
    total_revenue: float
    total_expenses: float
    net_profit: float
    advance_collected: float
    balance_pending: float
    new_bookings: int
    cancellations: int
    average_room_rate: float
    guest_feedback_count: int
    average_rating: float
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary"""
        return {
            "report_date": self.report_date.isoformat(),
            "total_rooms": self.total_rooms,
            "occupied_rooms": self.occupied_rooms,
            "available_rooms": self.available_rooms,
            "occupancy_percentage": round(self.occupancy_percentage, 2),
            "check_ins": self.check_ins,
            "check_outs": self.check_outs,
            "total_revenue": self.total_revenue,
            "total_expenses": self.total_expenses,
            "net_profit": self.net_profit,
            "advance_collected": self.advance_collected,
            "balance_pending": self.balance_pending,
            "new_bookings": self.new_bookings,
            "cancellations": self.cancellations,
            "average_room_rate": round(self.average_room_rate, 2),
            "guest_feedback_count": self.guest_feedback_count,
            "average_rating": round(self.average_rating, 2),
            "notes": self.notes
        }


@dataclass
class MarketingCampaign:
    """Marketing campaign tracking model"""
    campaign_id: str
    name: str
    platform: str  # WhatsApp, Instagram, Facebook, Direct
    start_date: date
    end_date: date
    target_audience: str  # Locals, Tourists, Corporate
    offer_details: str
    message_template: str
    reach: int = 0
    engagement: int = 0
    conversions: int = 0
    revenue_generated: float = 0.0
    cost: float = 0.0
    roi: float = 0.0
    active: bool = True
    
    def calculate_roi(self):
        """Calculate return on investment"""
        if self.cost > 0:
            self.roi = ((self.revenue_generated - self.cost) / self.cost) * 100
        else:
            self.roi = 0.0
    
    def to_dict(self) -> Dict:
        """Convert campaign to dictionary"""
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "platform": self.platform,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "target_audience": self.target_audience,
            "offer_details": self.offer_details,
            "message_template": self.message_template,
            "reach": self.reach,
            "engagement": self.engagement,
            "conversions": self.conversions,
            "revenue_generated": self.revenue_generated,
            "cost": self.cost,
            "roi": round(self.roi, 2),
            "active": self.active
        }
