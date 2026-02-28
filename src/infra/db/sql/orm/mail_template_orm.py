from sqlalchemy import (
    Column,
    Text, 
    DateTime,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MailTemplate(Base):
    __tablename__ = "mail_template"

    id = Column(String, primary_key=True)
    content = Column(Text)
    name = Column(Text)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
