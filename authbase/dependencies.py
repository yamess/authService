import string
import random
import time
from datetime import timedelta, datetime
from typing import Optional,Union,List

from fastapi import HTTPException,status,Depends
from jose import jwt,JWTError,ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api_v1.exceptions import credentials_exception,not_authorized_exception,does_not_exist_exception
from api_v1.models import User,LoginLogs
from api_v1.schemas import LoginsLogsSchema,UserRegistrationSchema
from passlib.context import CryptContext
from authbase.settings import ACCESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY,ALGORITHM,SessionLocal

# Security Section
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Database

def get_db():
    """provide db session to path operation functions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def id_generator(size=8, chars=string.ascii_letters + string.digits):
    x = ''.join(random.choice(chars) for _ in range(size))
    return x.upper()

def verify_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, 'iat': datetime.utcnow()})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str, client_host: str = None):
    user = crud_get_user(db=db, key="username", value=username)
    if (not user) | (not verify_password(plain_pwd=password, hashed_pwd=user.hashed_pwd)):
        log = LoginsLogsSchema(**{"status": "Failed", "client_host": str(client_host)})
        create_login_log(log=log, db=db)
        return False
    log = LoginsLogsSchema(**{"user_id": user.id, "status": "Success", "client_host": str(client_host)})
    create_login_log(log=log, db=db)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        if (not user_id) | (not username):
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise credentials_exception
    user = crud_get_user(db=db, key="id", value=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not exist"
        )
    return user

def crud_get_user(db: Session, key: str, value: Union[str, int]):
    if key == "email":
        return db.query(User).filter(User.email == value).first()
    elif key == "username":
        return db.query(User).filter(User.username == value).first()
    elif key == "id":
        return db.query(User).filter(User.id == value).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Key must be either id, username or email"
        )

def crud_get_users(db: Session, skip: int, limit: int) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def crud_create_user(db: Session, user: UserRegistrationSchema) -> User:
    try:
        existing_user = crud_get_user(db=db, key="email", value=user.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already existing")

        # Genanrate username
        username = id_generator()
        verify_user = db.query(User).filter(User.username == username).first()
        while verify_user:
            username = id_generator()
            verify_user = db.query(User).filter(User.username == username).first()

        # Password resolution
        pwd = get_password(user.password)
        data = {k: v for k, v in user.dict().items() if k != "password"}

        db_user = User(username=username, hashed_pwd=pwd, **data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data type"
        )

def crud_update_user(db: Session, user_id: int, data: dict):
    updates = {k: v for k, v in data.items() if k not in ["id", "username", "created_at", "updated_at", "is_superuser"]}
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise does_not_exist_exception
    db.query(User).filter(User.id == user_id).update(updates)
    db.commit()
    db.refresh(user)
    return user

def crud_delete_user(user_id: int, db: Session):
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise does_not_exist_exception
    db.delete(user_to_delete)
    db.commit()

# def crud_update_user(user_id: int, req: dict, current_user: UserSchema, db: Session):
#     if (user_id != current_user.id) & (not current_user.is_superuser):
#         raise credentials_exception
#     updates = {k: v for k, v in req.items() if ((k != "id") & (k != "email"))}
#     db.query(User).filter(User.id == user_id).update(updates)
#     db.commit()
#     return db.query(User).filter(User.id == user_id).first()
#
# def crud_delete_user(user_id, current_user: UserSchema, db: Session):
#     if current_user.is_superuser is False:
#         raise credentials_exception
#     user_to_delete = db.query(User).filter(User.id == user_id).first()
#     if not user_to_delete:
#         raise credentials_exception
#     db.delete(user_to_delete)
#     db.commit()
#
def create_login_log(log: LoginsLogsSchema, db: Session):
    try:
        loginlog = LoginLogs(
            user_id=log.user_id,
            status=log.status,
            client_host=log.client_host,
        )
        db.add(loginlog)
        db.commit()
    except AttributeError:
        return


# def is_authenticated(token: str = Depends(auth2_schema)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
#     except JWTError:
#         raise credentials_exception
#     if not payload:
#         raise credentials_exception
#     return payload
