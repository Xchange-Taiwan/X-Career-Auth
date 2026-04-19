from datetime import datetime, timezone
from typing import Dict, Any, List
from ....infra.client.calendar import CalendarClient
from ...auth.dao.i_auth_repository import IAuthRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ....config.exception import *

import logging

log = logging.getLogger(__name__)

class CalendarService:
    def __init__(self, calendar_client: CalendarClient, auth_repo: IAuthRepository):
        self.calendar_client = calendar_client
        self.auth_repo = auth_repo

    async def send_calendar_invite(
        self, db: AsyncSession, summary: str, description: str, 
        start_time_ts: int, end_time_ts: int, user_ids: List[int]
    ) -> Dict[str, Any]:
        
        attendee_emails = []
        
        for uid in user_ids:
            account = await self.auth_repo.find_account_by_user_id(db, uid)
            
            if not account:
                log.warning(f"[Calendar] 找不到 User ID: {uid} 的帳號資訊")
                continue
                
            if not account.email:
                log.warning(f"[Calendar] User ID: {uid} 帳號存在但未設定 Email")
                continue
            
            attendee_emails.append(account.email)

        if not attendee_emails:
            error_detail = f"無法為參與者建立日曆邀請：清單中的 User IDs {user_ids} 均無有效 Email"
            log.error(error_detail)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=error_detail
            )

        try:
            start_dt = datetime.fromtimestamp(start_time_ts, tz=timezone.utc)
            end_dt = datetime.fromtimestamp(end_time_ts, tz=timezone.utc)

            event = await self.calendar_client.create_event(
                summary=summary,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                attendee_emails=attendee_emails
            )
            
            return {
                'event_id': event.get('id'),
                'html_link': event.get('htmlLink'),
                'status': 'success',
                'sent_to': attendee_emails
            }
        except Exception as e:
            log.error(f"建立 Google 日曆活動失敗: {e}")
            raise e

    async def delete_calendar_event(self, event_id: str) -> Dict[str, Any]:
        try:
            await self.calendar_client.delete_event(event_id=event_id)
            return {
                'event_id': event_id,
                'status': 'deleted'
            }
        except Exception as e:
            log.error(f"Failed to delete calendar event {event_id}: {e}")
            raise e