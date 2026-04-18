import os
import asyncio
import logging
import json
from datetime import datetime
from typing import List

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...config.conf import GOOGLE_CALENDAR_TOKEN, GOOGLE_CALENDAR_ID

log = logging.getLogger(__name__)

class CalendarClient:
    def __init__(self):
        self.calendar_id = GOOGLE_CALENDAR_ID
        self.scopes = ['https://www.googleapis.com/auth/calendar.events']
        self.service = None
        self._lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """
        確保 Google API 已授權。
        """
        async with self._lock:
            if not self.service:
                log.info("Initializing Google Calendar Service...")
                token_env = GOOGLE_CALENDAR_TOKEN
                if not token_env:
                    raise Exception("Missing environment variable: GOOGLE_CALENDAR_TOKEN")
                
                creds = Credentials.from_authorized_user_info(json.loads(token_env), self.scopes)
                self.service = build('calendar', 'v3', credentials=creds)

            # 取得當前憑證
            creds = self.service._http.credentials

            # 檢查是否過期
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    log.info("Token expired, refreshing...")
                    creds.refresh(Request())
                    log.info(f"Token refreshed successfully! New expiry: {creds.expiry}")
                else:
                    raise Exception("Token invalid and cannot be refreshed automatically")

    async def create_event(self, summary: str, description: str, start_time: datetime, end_time: datetime, attendee_emails: list[str]):
        await self._ensure_initialized()

        try:
            attendees_str = ", ".join(attendee_emails)
            log.info(
                f"Creating calendar event: [{summary}] | "
                f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} | "
                f"Attendees: [{attendees_str}]"
            )

            request_id = f"x-career-{int(datetime.now().timestamp())}"
            attendees = [{'email': email} for email in attendee_emails]
            
            event_body = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                },
                'attendees': attendees,
                'conferenceData': {
                    'createRequest': {
                        'requestId': request_id,
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }

            created_event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event_body, 
                sendUpdates='all',
                conferenceDataVersion=1
            ).execute()

            log.info(f"Event created successfully! Google event ID: {created_event.get('id')} | Meet link: {created_event.get('hangoutLink')}")
            return created_event

        except HttpError as error:
            log.error(f"Google API call failed: {error}")
            raise error

    async def delete_event(self, event_id: str):
        await self._ensure_initialized()

        def _execute_delete():
            try:
                log.info(
                    f"Deleting calendar event, Google event ID: {event_id}"  
                )
                
                self.service.events().delete(
                    calendarId=self.calendar_id,
                    eventId=event_id,
                    sendUpdates='all'
                ).execute()
                
                log.info(f"Event deleted successfully.")
            except HttpError as error:
                if error.resp.status in [404, 410]:
                    log.warning(f"Event no longer exists in Google Calendar, skipping deletion [ID: {event_id}]")
                    return
                log.error(f"Failed to delete Google Calendar event [ID: {event_id}]: {error}")
                raise error

        return await asyncio.to_thread(_execute_delete)