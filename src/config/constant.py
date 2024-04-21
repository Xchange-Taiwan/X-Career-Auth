from enum import Enum
from .conf import LOCAL_REGION


class InterestCategory(Enum):
    INTERESTED_POSITION = 'interested_position'
    SKILL = 'skill'
    TOPIC = 'topic'


class ProfessionCategory(Enum):
    EXPERTISE = 'expertise'
    INDUSTRY = 'industry'


class ExperienceCategory(Enum):
    WORK = 'work'
    EDUCATION = 'education'
    LINK = 'link'


class ScheduleType(Enum):
    ALLOW = 'allow'
    FORBIDDEN = 'forbidden'


class RoleType(Enum):
    MENTOR = 'mentor'
    MENTEE = 'mentee'


class BookingStatus(Enum):
    PENDING = 'pending'
    ACCEPT = 'accept'
    REJECT = 'reject'


class ReservationListState(Enum):
    UPCOMING = 'upcoming'
    PENDING = 'pending'
    HISTORY = 'history'

class SortingBy(Enum):
    UPDATED_TIME = 'updated_time'
    # VIEW = 'view'

class Sorting(Enum):
    ASC = 1
    DESC = -1


REGION_MAPPING = {
    'us-east-1': 'us-e1',
    'us-east-2': 'us-e2',
    'us-west-1': 'us-w1',
    'us-west-2': 'us-w2',
    'ca-central-1': 'ca-c1',
    'eu-north-1': 'eu',
    'eu-west-2': 'uk',
    'eu-west-3': 'fr',
    'eu-south-1': 'it',
    'eu-central-1': 'de',
    'ap-northeast-1': 'jp',
    'ap-northeast-2': 'kr',
    'ap-southeast-1': 'sg',
    'ap-southeast-2': 'au',
    'ap-south-1': 'in',
    'sa-east-1': 'br'
}

HERE_WE_ARE = REGION_MAPPING[LOCAL_REGION]

class AccountType(str, Enum):
    XC = 'xc'
    LINKEDIN = 'linkedin'
    GOOGLE = 'google'
