from typing import Dict, Any
from fastapi import (
    APIRouter, status,
    Request, Depends,
    Body
)
from ...domain.calendar.model.calendar_model import CalendarEventDTO
from ...app.adapter import _calendar_service, ddb_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..res.response import *
import logging

log = logging.getLogger(__name__)

router = APIRouter(
    prefix='/calendar',
    tags=['Calendar'],
    responses={404: {'description': 'Not found'}},
)

@router.post('/events', status_code=status.HTTP_201_CREATED)
async def send_calendar_event(
    payload: CalendarEventDTO = Body(...),
    db: AsyncSession = Depends(ddb_session),
):
    res = await _calendar_service.send_calendar_invite(
        db=db,
        summary=payload.summary,
        description=payload.description,
        start_time_ts=payload.start_time,
        end_time_ts=payload.end_time,
        user_ids=payload.user_ids
    )
    return post_success(data=res)

@router.delete('/events/{event_id}', status_code=status.HTTP_200_OK)
async def delete_calendar_event(
    event_id: str,
):
    res = await _calendar_service.delete_calendar_event(event_id=event_id)
    return res_success(data=res)