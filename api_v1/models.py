from sqlalchemy import Column,Integer,DateTime,String,Boolean,ForeignKey,Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from authbase.settings import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_pwd = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    loginlogs = relationship("LoginLogs", cascade="all, delete", back_populates="user")

    def __repr__(self):
        return f"{self.id} - {self.email}"

class LoginLogs(Base):
    __tablename__ = "loginlogs"

    id = Column(Integer, primary_key=True)
    loggedin_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    client_host = Column(String, nullable=True)
    status = Column(String, nullable=False)

    user = relationship("User", back_populates="loginlogs")

    def __repr__(self):
        return str(self.loggedin_at)
