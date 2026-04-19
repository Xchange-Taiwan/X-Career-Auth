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
                log.info("初始化 Google Calendar Service...")
                token_env = GOOGLE_CALENDAR_TOKEN
                if not token_env:
                    raise Exception("環境變數缺少 GOOGLE_CALENDAR_TOKEN")
                
                creds = Credentials.from_authorized_user_info(json.loads(token_env), self.scopes)
                self.service = build('calendar', 'v3', credentials=creds)

            # 取得當前憑證
            creds = self.service._http.credentials

            # 檢查是否過期
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    log.info("Token 已過期，正在執行 Refresh")
                    creds.refresh(Request())
                    log.info(f"Refresh 成功！新到期時間: {creds.expiry}")
                else:
                    raise Exception("Token 失效且無法自動續期")

    async def create_event(self, summary: str, description: str, start_time: datetime, end_time: datetime, attendee_emails: list[str]):
        await self._ensure_initialized()

        try:
            attendees_str = ", ".join(attendee_emails)
            log.info(
                f"開始建立日曆行程: 【{summary}】 | "
                f"時間: {start_time.strftime('%Y-%m-%d %H:%M')} | "
                f"邀請對象: [{attendees_str}]"
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

            log.info(f"行程建立成功！google event ID: {created_event.get('id')} | Meet 連結: {created_event.get('hangoutLink')}")
            return created_event

        except HttpError as error:
            log.error(f"Google API 呼叫失敗: {error}")
            raise error

    async def delete_event(self, event_id: str):
        await self._ensure_initialized()

        def _execute_delete():
            try:
                log.info(
                    f"開始刪除日曆行程 google event ID: {event_id}"  
                )
                
                self.service.events().delete(
                    calendarId=self.calendar_id,
                    eventId=event_id,
                    sendUpdates='all'
                ).execute()
                
                log.info(f"行程刪除成功。")
            except HttpError as error:
                if error.resp.status in [404, 410]:
                    log.warning(f"行程已不存在於 Google 日曆，無需重複刪除 [ID: {event_id}]")
                    return
                log.error(f"刪除 Google 行程失敗 [ID: {event_id}]: {error}")
                raise error

        return await asyncio.to_thread(_execute_delete)