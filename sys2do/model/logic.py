# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-9-2
#  @author: cl.lam
#  Description:
###########################################
'''
from sqlalchemy import ForeignKey, Column, Float, Boolean
from sqlalchemy.types import Unicode, Integer, DateTime
from sys2do.model import DeclarativeBase
from auth import SysMixin

class Attachment(DeclarativeBase, SysMixin):
    __tablename__ = 'attachment'

    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(Unicode(500))
    original_name = Column(Unicode(500))
    path = Column(Unicode(1000))
    url = Column(Unicode(1000))

