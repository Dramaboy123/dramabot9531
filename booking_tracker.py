"""
Booking Tracker with Google Sheets Integration
Manages guest bookings, room assignments, and payment tracking
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Optional, Dict
from datetime import date, datetime
import logging

from config import Config
from models import Booking, Guest, Room, Expense, Feedback, GuestCategory, RoomStatus, PaymentStatus
from utils import generate_booking_id, format_date

logger = logging.getLogger(__name__)


class BookingTracker:
    """Manages bookings and integrates with Google Sheets"""
    
    def __init__(self):
        """Initialize Google Sheets connection"""
        self.client = None
        self.spreadsheet = None
        self.bookings_sheet = None
        self.rooms_sheet = None
        self.expenses_sheet = None
        self.feedback_sheet = None
        
    def connect(self):
        """Connect to Google Sheets"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate using service account
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            
            # Open the spreadsheet
            self.spreadsheet = self.client.open_by_key(Config.GOOGLE_SHEETS_SPREADSHEET_ID)
            
            # Get or create worksheets
            self._initialize_sheets()
            
            logger.info("Successfully connected to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            return False
    
    def _initialize_sheets(self):
        """Initialize or create necessary worksheets"""
        try:
            # Bookings sheet
            try:
                self.bookings_sheet = self.spreadsheet.worksheet("Bookings")
            except gspread.WorksheetNotFound:
                self.bookings_sheet = self.spreadsheet.add_worksheet(
                    title="Bookings",
                    rows=1000,
                    cols=20
                )
                self._setup_bookings_headers()
            
            # Rooms sheet
            try:
                self.rooms_sheet = self.spreadsheet.worksheet("Rooms")
            except gspread.WorksheetNotFound:
                self.rooms_sheet = self.spreadsheet.add_worksheet(
                    title="Rooms",
                    rows=100,
                    cols=10
                )
                self._setup_rooms_headers()
            
            # Expenses sheet
            try:
                self.expenses_sheet = self.spreadsheet.worksheet("Expenses")
            except gspread.WorksheetNotFound:
                self.expenses_sheet = self.spreadsheet.add_worksheet(
                    title="Expenses",
                    rows=1000,
                    cols=10
                )
                self._setup_expenses_headers()
            
            # Feedback sheet
            try:
                self.feedback_sheet = self.spreadsheet.worksheet("Feedback")
            except gspread.WorksheetNotFound:
                self.feedback_sheet = self.spreadsheet.add_worksheet(
                    title="Feedback",
                    rows=1000,
                    cols=10
                )
                self._setup_feedback_headers()
                
        except Exception as e:
            logger.error(f"Error initializing sheets: {e}")
            raise
    
    def _setup_bookings_headers(self):
        """Setup headers for bookings sheet"""
        headers = [
            "Booking ID", "Guest Name", "Phone", "ID Number", "Category",
            "Room Number", "Check-in", "Check-out", "Nights", "Guests",
            "Rate", "Total", "Advance", "Balance", "Payment Status",
            "Source", "Special Requests", "Checked In", "Checked Out", "Created At"
        ]
        self.bookings_sheet.update('A1:T1', [headers])
    
    def _setup_rooms_headers(self):
        """Setup headers for rooms sheet"""
        headers = [
            "Room Number", "Status", "Floor", "Type", "Max Occupancy",
            "Amenities", "Last Cleaned", "Notes"
        ]
        self.rooms_sheet.update('A1:H1', [headers])
    
    def _setup_expenses_headers(self):
        """Setup headers for expenses sheet"""
        headers = [
            "Expense ID", "Date", "Category", "Description", "Amount",
            "Paid To", "Payment Method", "Receipt Number", "Notes", "Created At"
        ]
        self.expenses_sheet.update('A1:J1', [headers])
    
    def _setup_feedback_headers(self):
        """Setup headers for feedback sheet"""
        headers = [
            "Feedback ID", "Booking ID", "Guest Name", "Rating", "Review",
            "Source", "Date", "Responded", "Response", "Public"
        ]
        self.feedback_sheet.update('A1:J1', [headers])
    
    def add_booking(self, booking: Booking) -> bool:
        """Add a new booking to the sheet"""
        try:
            row = [
                booking.booking_id,
                booking.guest.name,
                booking.guest.phone,
                booking.guest.id_number,
                booking.guest.category.value,
                booking.room_number,
                booking.check_in_date.isoformat(),
                booking.check_out_date.isoformat(),
                booking.calculate_nights(),
                booking.number_of_guests,
                booking.room_rate,
                booking.total_amount,
                booking.advance_paid,
                booking.balance_amount,
                booking.payment_status.value,
                booking.booking_source,
                booking.special_requests,
                booking.checked_in,
                booking.checked_out,
                booking.created_at.isoformat()
            ]
            
            self.bookings_sheet.append_row(row)
            logger.info(f"Added booking: {booking.booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding booking: {e}")
            return False
    
    def update_booking(self, booking_id: str, updates: Dict) -> bool:
        """Update an existing booking"""
        try:
            # Find the booking row
            cell = self.bookings_sheet.find(booking_id)
            if not cell:
                logger.error(f"Booking not found: {booking_id}")
                return False
            
            row_num = cell.row
            
            # Map column names to indices
            headers = self.bookings_sheet.row_values(1)
            
            for key, value in updates.items():
                if key in headers:
                    col_num = headers.index(key) + 1
                    self.bookings_sheet.update_cell(row_num, col_num, value)
            
            logger.info(f"Updated booking: {booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating booking: {e}")
            return False
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get booking details by ID"""
        try:
            cell = self.bookings_sheet.find(booking_id)
            if not cell:
                return None
            
            row_values = self.bookings_sheet.row_values(cell.row)
            headers = self.bookings_sheet.row_values(1)
            
            return dict(zip(headers, row_values))
            
        except Exception as e:
            logger.error(f"Error getting booking: {e}")
            return None
    
    def get_active_bookings(self, target_date: Optional[date] = None) -> List[Dict]:
        """Get all active bookings for a specific date"""
        try:
            if target_date is None:
                target_date = date.today()
            
            all_records = self.bookings_sheet.get_all_records()
            active_bookings = []
            
            for record in all_records:
                check_in = datetime.fromisoformat(record['Check-in']).date()
                check_out = datetime.fromisoformat(record['Check-out']).date()
                
                # Check if booking is active on target date
                if check_in <= target_date < check_out and not record.get('Checked Out', False):
                    active_bookings.append(record)
            
            return active_bookings
            
        except Exception as e:
            logger.error(f"Error getting active bookings: {e}")
            return []
    
    def get_todays_checkins(self) -> List[Dict]:
        """Get all check-ins scheduled for today"""
        try:
            today = date.today()
            all_records = self.bookings_sheet.get_all_records()
            
            checkins = []
            for record in all_records:
                check_in = datetime.fromisoformat(record['Check-in']).date()
                if check_in == today and not record.get('Checked In', False):
                    checkins.append(record)
            
            return checkins
            
        except Exception as e:
            logger.error(f"Error getting today's check-ins: {e}")
            return []
    
    def get_todays_checkouts(self) -> List[Dict]:
        """Get all check-outs scheduled for today"""
        try:
            today = date.today()
            all_records = self.bookings_sheet.get_all_records()
            
            checkouts = []
            for record in all_records:
                check_out = datetime.fromisoformat(record['Check-out']).date()
                if check_out == today and not record.get('Checked Out', False):
                    checkouts.append(record)
            
            return checkouts
            
        except Exception as e:
            logger.error(f"Error getting today's check-outs: {e}")
            return []
    
    def update_room_status(self, room_number: str, status: str) -> bool:
        """Update room status"""
        try:
            cell = self.rooms_sheet.find(room_number)
            if not cell:
                logger.error(f"Room not found: {room_number}")
                return False
            
            row_num = cell.row
            # Status is in column B (2)
            self.rooms_sheet.update_cell(row_num, 2, status)
            
            logger.info(f"Updated room {room_number} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating room status: {e}")
            return False
    
    def get_available_rooms(self, target_date: Optional[date] = None) -> List[str]:
        """Get list of available room numbers"""
        try:
            if target_date is None:
                target_date = date.today()
            
            # Get all rooms
            all_rooms = self.rooms_sheet.get_all_records()
            
            # Get active bookings
            active_bookings = self.get_active_bookings(target_date)
            occupied_rooms = [b['Room Number'] for b in active_bookings]
            
            # Filter available rooms
            available = []
            for room in all_rooms:
                if (room['Room Number'] not in occupied_rooms and 
                    room['Status'] in ['AVAILABLE', 'Available']):
                    available.append(room['Room Number'])
            
            return available
            
        except Exception as e:
            logger.error(f"Error getting available rooms: {e}")
            return []
    
    def add_expense(self, expense: Expense) -> bool:
        """Add expense record"""
        try:
            row = [
                expense.expense_id,
                expense.date.isoformat(),
                expense.category,
                expense.description,
                expense.amount,
                expense.paid_to,
                expense.payment_method,
                expense.receipt_number or "",
                expense.notes,
                expense.created_at.isoformat()
            ]
            
            self.expenses_sheet.append_row(row)
            logger.info(f"Added expense: {expense.expense_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return False
    
    def get_expenses_by_date(self, target_date: date) -> List[Dict]:
        """Get all expenses for a specific date"""
        try:
            all_records = self.expenses_sheet.get_all_records()
            
            expenses = []
            for record in all_records:
                expense_date = datetime.fromisoformat(record['Date']).date()
                if expense_date == target_date:
                    expenses.append(record)
            
            return expenses
            
        except Exception as e:
            logger.error(f"Error getting expenses: {e}")
            return []
    
    def add_feedback(self, feedback: Feedback) -> bool:
        """Add guest feedback"""
        try:
            row = [
                feedback.feedback_id,
                feedback.booking_id,
                feedback.guest_name,
                feedback.rating,
                feedback.review_text,
                feedback.source,
                feedback.date.isoformat(),
                feedback.responded,
                feedback.response_text or "",
                feedback.public
            ]
            
            self.feedback_sheet.append_row(row)
            logger.info(f"Added feedback: {feedback.feedback_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return False
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent feedback entries"""
        try:
            all_records = self.feedback_sheet.get_all_records()
            # Sort by date (most recent first)
            sorted_records = sorted(
                all_records,
                key=lambda x: datetime.fromisoformat(x['Date']),
                reverse=True
            )
            return sorted_records[:limit]
            
        except Exception as e:
            logger.error(f"Error getting feedback: {e}")
            return []
