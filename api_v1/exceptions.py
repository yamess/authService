from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials"
)
not_authorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authorized to perform this operation"
)
does_not_exist_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="No record found"
)
