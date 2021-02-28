from datetime import timedelta
from json.decoder import JSONDecodeError
from typing import List

from fastapi import APIRouter,Depends,Request,HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from api_v1.exceptions import credentials_exception,not_authorized_exception
from api_v1.models import User
from api_v1.schemas import UserSchema,UserLoginSchema,TokenSchema,UserRegistrationSchema
from authbase.dependencies import get_db,authenticate_user,create_access_token,crud_create_user,get_current_user, \
    crud_get_users,crud_delete_user,crud_update_user,is_verified
from authbase.settings import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# Authentication
@router.post("/token", response_model=TokenSchema, tags=["Authentication"], status_code=status.HTTP_200_OK)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        ip = str(request.client.host)
        data = UserLoginSchema(**body)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided"
        )
    user = authenticate_user(db=db, username=data.username, password=data.password, client_host=ip)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    data = {
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "is_active": user.is_active
    }
    access_token = create_access_token(data=data, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token/verify", tags=["Authentication"], status_code=status.HTTP_200_OK)
async def verify(request: Request):
    body = await request.json()
    access_token = body['token']
    res = is_verified(access_token)
    if res:
        return True
    return False

# Register new user
@router.post("/users/register", response_model=UserSchema, tags=["Users"], status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegistrationSchema, db: Session = Depends(get_db)):
    user = crud_create_user(user=user_in, db=db)
    return user

@router.get("/users/me", response_model=UserSchema, tags=["Users"], status_code=status.HTTP_200_OK)
async def read_me(user: User = Depends(get_current_user)):
    return user

@router.get("/users/list", response_model=List[UserSchema], tags=["Users"], status_code=status.HTTP_200_OK)
async def read_users(
        current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
        skip: int = 0, limit: int = 100
):
    if not current_user:
        raise credentials_exception
    if (not current_user.is_admin) & (not current_user.is_superuser):
        raise not_authorized_exception
    try:
        users = crud_get_users(db=db, skip=skip, limit=limit)
    except JWTError:
        raise credentials_exception
    return users

@router.patch("/users/update/{user_id}", response_model=UserSchema, tags=["Users"], status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_id: int, data: dict, current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    if (user_id != current_user.id) & (not current_user.is_superuser) & (not current_user.is_admin):
        raise not_authorized_exception
    user = crud_update_user(user_id=user_id, db=db, data=data)
    return user

@router.delete("/users/delete/{user_id}", tags=["Users"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if (not current_user.is_admin) & (not current_user.is_superuser):
        raise not_authorized_exception
    crud_delete_user(user_id=user_id, db=db)

