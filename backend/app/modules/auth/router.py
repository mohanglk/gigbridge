from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth import service
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.rate_limit import (
    AuthRateLimiter,
    enforce_auth_rate_limit,
    get_auth_rate_limiter,
)
from app.modules.auth.schemas import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
    RegistrationRequest,
    RegistrationResponse,
)

router = APIRouter()
REFRESH_COOKIE_NAME = "gigbridge_refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def register(
    payload: RegistrationRequest,
    request: Request,
    db: Session = Depends(get_db),
    rate_limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
) -> RegistrationResponse:
    enforce_auth_rate_limit(rate_limiter, "register", request, payload.email)
    try:
        service.register_user(
            db,
            email=payload.email,
            password=payload.password.get_secret_value(),
        )
    except service.DuplicateEmailError:
        # Duplicate and new addresses intentionally receive identical responses.
        return RegistrationResponse()

    return RegistrationResponse()


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    rate_limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
) -> LoginResponse:
    enforce_auth_rate_limit(rate_limiter, "login", request, payload.email)
    try:
        result = service.login_user(
            db,
            email=payload.email,
            password=payload.password.get_secret_value(),
        )
    except service.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=result.refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path=REFRESH_COOKIE_PATH,
        secure=settings.secure_auth_cookies,
        httponly=True,
        samesite=settings.auth_cookie_samesite,
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return LoginResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        user=AuthUserResponse.model_validate(result.user),
    )


@router.get("/me", response_model=AuthUserResponse)
def current_user(user: User = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse.model_validate(user)
