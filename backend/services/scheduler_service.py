"""
Scheduling service for automated Canvas data syncing and notifications.
Uses APScheduler for background tasks and proactive notifications.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.services.sync_service import CanvasSyncService
from backend.services.ai_service import CanvasAIService
from backend.models import Assignment, User, NotificationLog

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CanvasSchedulerService:
    """Background scheduler for automated Canvas tasks."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Canvas Scheduler Service started")
    
    def schedule_daily_sync(self):
        """Schedule daily full sync at 6 AM."""
        self.scheduler.add_job(
            func=self._daily_sync_job,
            trigger=CronTrigger(hour=6, minute=0),
            id='daily_sync',
            name='Daily Canvas Sync',
            replace_existing=True
        )
        logger.info("Scheduled daily sync at 6:00 AM")
    
    def schedule_deadline_notifications(self):
        """Schedule deadline notifications to run every hour."""
        self.scheduler.add_job(
            func=self._deadline_notification_job,
            trigger=IntervalTrigger(hours=1),
            id='deadline_notifications',
            name='Deadline Notifications',
            replace_existing=True
        )
        logger.info("Scheduled hourly deadline notifications")
    
    def schedule_assignment_sync(self):
        """Schedule assignment sync every 4 hours."""
        self.scheduler.add_job(
            func=self._assignment_sync_job,
            trigger=IntervalTrigger(hours=4),
            id='assignment_sync',
            name='Assignment Sync',
            replace_existing=True
        )
        logger.info("Scheduled assignment sync every 4 hours")
    
    def _daily_sync_job(self):
        """Execute daily full sync."""
        logger.info("Starting daily sync job")
        db = SessionLocal()
        try:
            sync_service = CanvasSyncService(db)
            sync_run = sync_service.full_sync(user_id=1)
            logger.info(f"Daily sync completed: {sync_run.status}, processed {sync_run.items_processed} items")
        except Exception as e:
            logger.error(f"Daily sync failed: {str(e)}")
        finally:
            db.close()
    
    def _assignment_sync_job(self):
        """Execute assignment sync."""
        logger.info("Starting assignment sync job")
        db = SessionLocal()
        try:
            sync_service = CanvasSyncService(db)
            sync_run = sync_service.sync_assignments(user_id=1)
            logger.info(f"Assignment sync completed: {sync_run.status}, processed {sync_run.items_processed} items")
        except Exception as e:
            logger.error(f"Assignment sync failed: {str(e)}")
        finally:
            db.close()
    
    def _deadline_notification_job(self):
        """Check for upcoming deadlines and send notifications."""
        logger.info("Starting deadline notification job")
        db = SessionLocal()
        try:
            ai_service = CanvasAIService(db)
            
            # Get assignments due in next 24 hours
            upcoming_24h = ai_service.get_upcoming_deadlines(user_id=1, days_ahead=1)
            
            # Get assignments due in next 3 days (but not already notified for 24h)
            upcoming_3d = ai_service.get_upcoming_deadlines(user_id=1, days_ahead=3)
            
            notifications_sent = 0
            
            # Send 24-hour notifications
            for deadline in upcoming_24h:
                if deadline["urgency"] == "high":
                    # Check if we already sent notification today
                    existing_notification = db.query(NotificationLog).filter(
                        NotificationLog.user_id == 1,
                        NotificationLog.notification_type == "24h_deadline",
                        NotificationLog.extra_data.contains(str(deadline["assignment_id"])),
                        NotificationLog.sent_at >= datetime.now(timezone.utc) - timedelta(hours=12)
                    ).first()
                    
                    if not existing_notification:
                        notification = ai_service.create_deadline_notification(
                            user_id=1,
                            assignment_id=deadline["assignment_id"],
                            notification_type="24h_deadline"
                        )
                        notifications_sent += 1
                        logger.info(f"Sent 24h deadline notification for: {deadline['name']}")
            
            # Send 3-day notifications (less urgent)
            for deadline in upcoming_3d:
                if deadline["urgency"] == "medium" and deadline["days_until_due"] == 3:
                    existing_notification = db.query(NotificationLog).filter(
                        NotificationLog.user_id == 1,
                        NotificationLog.notification_type == "3d_deadline",
                        NotificationLog.extra_data.contains(str(deadline["assignment_id"])),
                        NotificationLog.sent_at >= datetime.now(timezone.utc) - timedelta(days=2)
                    ).first()
                    
                    if not existing_notification:
                        notification = ai_service.create_deadline_notification(
                            user_id=1,
                            assignment_id=deadline["assignment_id"],
                            notification_type="3d_deadline"
                        )
                        notifications_sent += 1
                        logger.info(f"Sent 3d deadline notification for: {deadline['name']}")
            
            logger.info(f"Deadline notification job completed: {notifications_sent} notifications sent")
            
        except Exception as e:
            logger.error(f"Deadline notification job failed: {str(e)}")
        finally:
            db.close()
    
    def get_job_status(self) -> List[Dict[str, Any]]:
        """Get status of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    def trigger_sync_now(self) -> Dict[str, str]:
        """Manually trigger a sync job."""
        try:
            self.scheduler.add_job(
                func=self._daily_sync_job,
                trigger='date',
                run_date=datetime.now() + timedelta(seconds=2),
                id='manual_sync',
                name='Manual Sync'
            )
            return {"status": "success", "message": "Manual sync triggered"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Canvas Scheduler Service stopped")


# Global scheduler instance
scheduler_service = None


def get_scheduler_service() -> CanvasSchedulerService:
    """Get or create scheduler service instance."""
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = CanvasSchedulerService()
        # Schedule all jobs
        scheduler_service.schedule_daily_sync()
        scheduler_service.schedule_deadline_notifications()
        scheduler_service.schedule_assignment_sync()
    return scheduler_service


def initialize_scheduler():
    """Initialize the scheduler service."""
    return get_scheduler_service()
