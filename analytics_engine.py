"""
Analytics Engine for Hotel Nico
Tracks occupancy, revenue, expenses, and generates insights
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd

from config import Config
from models import DailyReport
from booking_tracker import BookingTracker
from utils import (
    calculate_occupancy_percentage,
    get_occupancy_status,
    format_currency,
    get_today,
    get_week_dates,
    get_month_dates,
    average
)

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Analyzes hotel performance and generates insights"""
    
    def __init__(self, booking_tracker: BookingTracker):
        """Initialize analytics engine with booking tracker"""
        self.tracker = booking_tracker
    
    def generate_daily_report(self, target_date: Optional[date] = None) -> DailyReport:
        """Generate comprehensive daily report"""
        if target_date is None:
            target_date = get_today()
        
        try:
            # Get active bookings
            active_bookings = self.tracker.get_active_bookings(target_date)
            occupied_rooms = len(active_bookings)
            available_rooms = Config.TOTAL_ROOMS - occupied_rooms
            
            # Calculate occupancy
            occupancy_pct = calculate_occupancy_percentage(occupied_rooms, Config.TOTAL_ROOMS)
            
            # Get check-ins and check-outs
            checkins = self.tracker.get_todays_checkins() if target_date == get_today() else []
            checkouts = self.tracker.get_todays_checkouts() if target_date == get_today() else []
            
            # Calculate revenue
            total_revenue = sum(float(b.get('Total', 0)) for b in active_bookings)
            advance_collected = sum(float(b.get('Advance', 0)) for b in active_bookings)
            balance_pending = sum(float(b.get('Balance', 0)) for b in active_bookings)
            
            # Calculate average room rate
            if active_bookings:
                avg_rate = average([float(b.get('Rate', 0)) for b in active_bookings])
            else:
                avg_rate = 0.0
            
            # Get expenses
            expenses = self.tracker.get_expenses_by_date(target_date)
            total_expenses = sum(float(e.get('Amount', 0)) for e in expenses)
            
            # Calculate net profit
            net_profit = total_revenue - total_expenses
            
            # Get feedback
            feedback = self.tracker.get_recent_feedback(limit=100)
            today_feedback = [f for f in feedback if datetime.fromisoformat(f['Date']).date() == target_date]
            
            if today_feedback:
                avg_rating = average([float(f.get('Rating', 0)) for f in today_feedback])
            else:
                avg_rating = 0.0
            
            # Create report
            report = DailyReport(
                report_date=target_date,
                total_rooms=Config.TOTAL_ROOMS,
                occupied_rooms=occupied_rooms,
                available_rooms=available_rooms,
                occupancy_percentage=occupancy_pct,
                check_ins=len(checkins),
                check_outs=len(checkouts),
                total_revenue=total_revenue,
                total_expenses=total_expenses,
                net_profit=net_profit,
                advance_collected=advance_collected,
                balance_pending=balance_pending,
                new_bookings=0,  # Would need to track this separately
                cancellations=0,  # Would need to track this separately
                average_room_rate=avg_rate,
                guest_feedback_count=len(today_feedback),
                average_rating=avg_rating
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            raise
    
    def get_occupancy_trend(self, days: int = 7) -> List[Tuple[date, float]]:
        """Get occupancy trend for past N days"""
        try:
            trend = []
            today = get_today()
            
            for i in range(days):
                target_date = today - timedelta(days=i)
                active_bookings = self.tracker.get_active_bookings(target_date)
                occupancy = calculate_occupancy_percentage(len(active_bookings), Config.TOTAL_ROOMS)
                trend.append((target_date, occupancy))
            
            return list(reversed(trend))
            
        except Exception as e:
            logger.error(f"Error getting occupancy trend: {e}")
            return []
    
    def get_revenue_trend(self, days: int = 7) -> List[Tuple[date, float]]:
        """Get revenue trend for past N days"""
        try:
            trend = []
            today = get_today()
            
            for i in range(days):
                target_date = today - timedelta(days=i)
                active_bookings = self.tracker.get_active_bookings(target_date)
                revenue = sum(float(b.get('Total', 0)) for b in active_bookings)
                trend.append((target_date, revenue))
            
            return list(reversed(trend))
            
        except Exception as e:
            logger.error(f"Error getting revenue trend: {e}")
            return []
    
    def analyze_guest_categories(self) -> Dict[str, int]:
        """Analyze distribution of guest categories"""
        try:
            active_bookings = self.tracker.get_active_bookings()
            
            categories = {}
            for booking in active_bookings:
                category = booking.get('Category', 'UNKNOWN')
                categories[category] = categories.get(category, 0) + 1
            
            return categories
            
        except Exception as e:
            logger.error(f"Error analyzing guest categories: {e}")
            return {}
    
    def analyze_booking_sources(self) -> Dict[str, int]:
        """Analyze distribution of booking sources"""
        try:
            active_bookings = self.tracker.get_active_bookings()
            
            sources = {}
            for booking in active_bookings:
                source = booking.get('Source', 'UNKNOWN')
                sources[source] = sources.get(source, 0) + 1
            
            return sources
            
        except Exception as e:
            logger.error(f"Error analyzing booking sources: {e}")
            return {}
    
    def get_low_occupancy_alert(self) -> Optional[Dict]:
        """Check if occupancy is below threshold and generate alert"""
        try:
            report = self.generate_daily_report()
            
            if report.occupancy_percentage < Config.LOW_OCCUPANCY_THRESHOLD:
                return {
                    "alert": True,
                    "occupancy": report.occupancy_percentage,
                    "threshold": Config.LOW_OCCUPANCY_THRESHOLD,
                    "available_rooms": report.available_rooms,
                    "message": f"⚠️ Low Occupancy Alert: {report.occupancy_percentage:.1f}% (Target: {Config.TARGET_OCCUPANCY}%)"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking occupancy alert: {e}")
            return None
    
    def get_payment_pending_summary(self) -> Dict:
        """Get summary of pending payments"""
        try:
            active_bookings = self.tracker.get_active_bookings()
            
            pending_bookings = []
            total_pending = 0.0
            
            for booking in active_bookings:
                balance = float(booking.get('Balance', 0))
                if balance > 0:
                    pending_bookings.append({
                        "booking_id": booking.get('Booking ID'),
                        "guest_name": booking.get('Guest Name'),
                        "balance": balance
                    })
                    total_pending += balance
            
            return {
                "count": len(pending_bookings),
                "total_amount": total_pending,
                "bookings": pending_bookings
            }
            
        except Exception as e:
            logger.error(f"Error getting payment summary: {e}")
            return {"count": 0, "total_amount": 0.0, "bookings": []}
    
    def get_weekly_summary(self) -> Dict:
        """Generate weekly performance summary"""
        try:
            start_date, end_date = get_week_dates()
            
            total_revenue = 0.0
            total_expenses = 0.0
            occupancy_rates = []
            
            current_date = start_date
            while current_date <= end_date:
                # Get daily data
                active_bookings = self.tracker.get_active_bookings(current_date)
                daily_revenue = sum(float(b.get('Total', 0)) for b in active_bookings)
                total_revenue += daily_revenue
                
                expenses = self.tracker.get_expenses_by_date(current_date)
                daily_expenses = sum(float(e.get('Amount', 0)) for e in expenses)
                total_expenses += daily_expenses
                
                occupancy = calculate_occupancy_percentage(len(active_bookings), Config.TOTAL_ROOMS)
                occupancy_rates.append(occupancy)
                
                current_date += timedelta(days=1)
            
            avg_occupancy = average(occupancy_rates) if occupancy_rates else 0.0
            net_profit = total_revenue - total_expenses
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_profit": net_profit,
                "average_occupancy": avg_occupancy,
                "days": (end_date - start_date).days + 1
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {e}")
            return {}
    
    def get_monthly_summary(self) -> Dict:
        """Generate monthly performance summary"""
        try:
            start_date, end_date = get_month_dates()
            
            total_revenue = 0.0
            total_expenses = 0.0
            occupancy_rates = []
            
            current_date = start_date
            while current_date <= end_date:
                # Get daily data
                active_bookings = self.tracker.get_active_bookings(current_date)
                daily_revenue = sum(float(b.get('Total', 0)) for b in active_bookings)
                total_revenue += daily_revenue
                
                expenses = self.tracker.get_expenses_by_date(current_date)
                daily_expenses = sum(float(e.get('Amount', 0)) for e in expenses)
                total_expenses += daily_expenses
                
                occupancy = calculate_occupancy_percentage(len(active_bookings), Config.TOTAL_ROOMS)
                occupancy_rates.append(occupancy)
                
                current_date += timedelta(days=1)
            
            avg_occupancy = average(occupancy_rates) if occupancy_rates else 0.0
            net_profit = total_revenue - total_expenses
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_profit": net_profit,
                "average_occupancy": avg_occupancy,
                "days": (end_date - start_date).days + 1
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly summary: {e}")
            return {}
    
    def suggest_pricing_strategy(self) -> Dict:
        """Suggest pricing strategy based on occupancy"""
        try:
            report = self.generate_daily_report()
            occupancy = report.occupancy_percentage
            
            suggestions = []
            
            if occupancy < 50:
                suggestions.append({
                    "strategy": "Aggressive Discount",
                    "action": f"Offer ₹{Config.LOCAL_RATE - 100} for locals, ₹{Config.STANDARD_RATE - 300} for tourists",
                    "reason": "Very low occupancy - need to fill rooms quickly"
                })
            elif occupancy < 70:
                suggestions.append({
                    "strategy": "Moderate Discount",
                    "action": f"Maintain ₹{Config.LOCAL_RATE} for locals, offer ₹{Config.STANDARD_RATE - 200} for tourists",
                    "reason": "Below target occupancy - attract more guests"
                })
            elif occupancy < 90:
                suggestions.append({
                    "strategy": "Standard Pricing",
                    "action": f"Maintain current rates: ₹{Config.LOCAL_RATE} locals, ₹{Config.STANDARD_RATE} tourists",
                    "reason": "Good occupancy - maintain current strategy"
                })
            else:
                suggestions.append({
                    "strategy": "Premium Pricing",
                    "action": f"Consider increasing rates by 10-15% for new bookings",
                    "reason": "High demand - maximize revenue"
                })
            
            return {
                "current_occupancy": occupancy,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error suggesting pricing strategy: {e}")
            return {}
    
    def get_performance_insights(self) -> List[str]:
        """Generate actionable insights based on performance data"""
        try:
            insights = []
            
            # Occupancy insight
            report = self.generate_daily_report()
            status, emoji = get_occupancy_status(report.occupancy_percentage)
            insights.append(f"{emoji} Occupancy is {status} at {report.occupancy_percentage:.1f}%")
            
            # Revenue insight
            if report.net_profit > 0:
                insights.append(f"💰 Profitable day with net profit of {format_currency(report.net_profit)}")
            else:
                insights.append(f"⚠️ Loss of {format_currency(abs(report.net_profit))} - review expenses")
            
            # Payment insight
            payment_summary = self.get_payment_pending_summary()
            if payment_summary['count'] > 0:
                insights.append(f"💳 {payment_summary['count']} bookings have pending payments totaling {format_currency(payment_summary['total_amount'])}")
            
            # Guest category insight
            categories = self.analyze_guest_categories()
            if categories:
                top_category = max(categories, key=categories.get)
                insights.append(f"👥 Most guests are {top_category} ({categories[top_category]} bookings)")
            
            # Feedback insight
            if report.guest_feedback_count > 0:
                insights.append(f"⭐ Average rating: {report.average_rating:.1f}/5 from {report.guest_feedback_count} reviews")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
