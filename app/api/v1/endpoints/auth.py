from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from ....core.database import get_db
from ....core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token, validate_password_strength
)
from ....core.dependencies import get_current_user
from ....core.exceptions import (
    UnauthorizedException, ForbiddenException, NotFoundException,
    BusinessRuleException
)
from ....models.user import User, UserSession
from ....models.audit import AuditLog
from ....schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest,
    RefreshTokenResponse, ForgotPasswordRequest,
    VerifyOTPRequest, ResetPasswordRequest,
    ChangePasswordRequest, SessionResponse, UserProfileResponse,
    LoginHistoryResponse
)
from ....schemas.common import ResponseModel
from ....core.logging import create_audit_log
import logging
import secrets
import string

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=ResponseModel)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and generate JWT tokens.
    AUTH-001: Login API
    """
    # Find user by username or email
    # user = db.query(User).filter(
    #     (User.username == credentials.username) |
    #     (User.email == credentials.username)
    # ).first()
    result = await db.execute(
        select(User).where(
            (User.username == credentials.username) |
            (User.email == credentials.username)
        )
    )

    user = result.scalar_one_or_none()
    
    if not user:
        # Create audit log for failed login
        create_audit_log(
            db=db,
            user_id=None,
            action="login_failed",
            resource_type="user",
            resource_data={"username": credentials.username},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            status="error",
            error_message="Invalid credentials"
        )
        raise UnauthorizedException("Invalid username or password")
    
    # Check if user is active
    if not user.is_active or user.is_deleted:
        raise UnauthorizedException("Account is disabled")
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise BusinessRuleException(f"Account is locked. Try again in {remaining} minutes")
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        #db.commit()
        await db.commit()

        create_audit_log(
            db=db,
            user_id=user.id,
            action="login_failed",
            resource_type="user",
            resource_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            status="error",
            error_message="Invalid password"
        )
        raise UnauthorizedException("Invalid username or password")
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    # db.commit()
    await db.commit()
    
    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "role": user.role_name,
        "hospital_id": str(user.hospital_id) if user.hospital_id else None
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Create session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        access_token=access_token,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    # db.add(session)
    # db.commit()
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    # Create audit log for successful login
    create_audit_log(
        db=db,
        user_id=user.id,
        action="login_success",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
    
    return ResponseModel(
        success=True,
        message="Login successful",
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,
            role=user.role_name,
            user_id=str(user.id),
            full_name=user.full_name,
            email=user.email
        ).model_dump()
    )


@router.post("/refresh", response_model=ResponseModel)
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new access token using refresh token.
    AUTH-002: Refresh Token API
    """
    # Validate refresh token
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")
        
        # Check if session exists and is valid
        # session = db.query(UserSession).filter(
        #     UserSession.refresh_token == data.refresh_token,
        #     UserSession.is_valid == True
        # ).first()
        result = await db.execute(
            select(UserSession).where(
                UserSession.refresh_token == data.refresh_token,
                UserSession.is_valid == True
            )
        )

        session = result.scalar_one_or_none()
        
        if not session:
            raise UnauthorizedException("Invalid or expired refresh token")
        
        # Check if session has expired
        if session.expires_at < datetime.utcnow():
            session.is_valid = False
            db.commit()
            raise UnauthorizedException("Refresh token has expired")
        
        # Get user
        #user = db.query(User).filter(User.id == UUID(user_id)).first()
        result = await db.execute(
            select(User).where(
                User.id == UUID(user_id)
            )
        )

        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        
        # Generate new access token
        token_data = {
            "sub": str(user.id),
            "role": user.role_name,
            "hospital_id": str(user.hospital_id) if user.hospital_id else None
        }
        
        new_access_token = create_access_token(token_data)
        
        # Update session with new access token
        session.access_token = new_access_token
        #db.commit()
        await db.commit()
        
        return ResponseModel(
            success=True,
            message="Token refreshed successfully",
            data=RefreshTokenResponse(
                access_token=new_access_token,
                expires_in=1800
            ).model_dump()
        )
        
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        raise UnauthorizedException("Invalid refresh token")


@router.post("/logout", response_model=ResponseModel)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user.
    AUTH-003: Logout API
    """
    # Invalidate all sessions for the user
    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == current_user.id,
            UserSession.is_valid == True
        )
        .values(
            is_valid=False
        )
    )

    await db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="logout",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
    
    return ResponseModel(
        success=True,
        message="Logged out successfully"
    )


@router.post("/forgot-password", response_model=ResponseModel)
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AUTH-004
    Forgot Password
    """
    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    user = result.scalar_one_or_none()
    if not user:
        return ResponseModel(
            success=True,
            message="If your email is registered, you will receive an OTP."
        )

    from app.services.otp_service import OTPService
    # Generate OTP
    otp = await OTPService.generate_otp()

    # Save OTP In Redis
    await OTPService.save_otp(
        email=user.email,
        otp=otp,
    )

    # Send Email / SMS
    # await send_email_otp(user.email, otp)

    logger.info(
        f"OTP for {user.email}: {otp}"
    )

    # Audit Log
    create_audit_log(
        db=db,
        user_id=user.id,
        action="forgot_password",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )

    return ResponseModel(
        success=True,
        message="OTP sent successfully.",
        data={
            "email": user.email,
            "expires_in": OTPService.OTP_EXPIRY,
        }
    )

@router.post("/verify-otp", response_model=ResponseModel)
async def verify_otp(
    request: Request,
    data: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AUTH-005
    Verify Forgot Password OTP
    """

    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException(
            "User",
            f"email {data.email}"
        )

    from app.services.otp_service import OTPService
    # Get OTP From Redis
    stored_otp = await OTPService.get_otp(
        user.email
    )

    if stored_otp is None:
        raise BusinessRuleException(
            "OTP expired or not found. Please request a new OTP."
        )

    # Verify OTP
    if str(stored_otp).strip() != str(data.otp).strip():
        raise BusinessRuleException(
            "Invalid OTP"
        )

    # Mark OTP Verified
    await OTPService.mark_verified(
        user.email
    )

    # Delete OTP immediately after verification
    await OTPService.delete_otp(
        user.email
    )

    # Audit Log
    create_audit_log(
        db=db,
        user_id=user.id,
        action="otp_verified",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )

    return ResponseModel(
        success=True,
        message="OTP verified successfully."
    )

@router.post("/reset-password", response_model=ResponseModel)
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    AUTH-006
    Reset Password
    """

    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException(
            "User",
            f"email {data.email}"
        )

    from app.services.otp_service import OTPService

    # Check OTP Verification
    verified = await OTPService.is_verified(
        user.email
    )

    if not verified:
        raise BusinessRuleException(
            "OTP not verified. Please verify OTP first."
        )

    # Password Validation
    is_valid, message = validate_password_strength(
        data.new_password
    )

    if not is_valid:
        raise BusinessRuleException(message)

    # Password History
    password_history = user.password_history or []

    for old_password in password_history:

        if verify_password(
            data.new_password,
            old_password,
        ):
            raise BusinessRuleException(
                "Password has been used recently."
            )

    # Update Password
    hashed_password = get_password_hash(
        data.new_password
    )

    user.hashed_password = hashed_password
    user.password_changed_at = datetime.utcnow()

    # Update Password History

    if len(password_history) >= 5:
        password_history.pop(0)

    password_history.append(
        hashed_password
    )
    user.password_history = password_history

    # Invalidate All Sessions
    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user.id
        )
        .values(
            is_valid=False
        )
    )
    await db.commit()

    # Remove OTP From Redis
    await OTPService.clear(
        user.email
    )

    # Audit Log
    create_audit_log(
        db=db,
        user_id=user.id,
        action="reset_password",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )

    return ResponseModel(
        success=True,
        message="Password reset successfully."
    )

@router.post("/change-password", response_model=ResponseModel)
async def change_password(
    request: Request,
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for authenticated user.
    AUTH-007: Change Password API
    """
    # Verify current password
    if not verify_password(data.current_password, current_user.hashed_password):
        raise UnauthorizedException("Current password is incorrect")
    
    # Validate new password strength
    is_valid, message = validate_password_strength(data.new_password)
    if not is_valid:
        raise BusinessRuleException(message)
    
    # Check password history
    password_history = current_user.password_history or []
    for old_password_hash in password_history:
        if verify_password(data.new_password, old_password_hash):
            raise BusinessRuleException("Password already used recently")
    
    # Update password
    new_password_hash = get_password_hash(data.new_password)
    current_user.hashed_password = new_password_hash
    current_user.password_changed_at = datetime.utcnow()
    
    # Update password history
    if len(password_history) >= 5:
        password_history.pop(0)
    password_history.append(new_password_hash)
    current_user.password_history = password_history
    
    await db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="change_password",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
    
    return ResponseModel(
        success=True,
        message="Password changed successfully"
    )


@router.get("/session", response_model=ResponseModel)
async def validate_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate current user session.
    AUTH-008: Validate Session API
    """
    # Check if user has any valid session
    result = await db.execute(
        select(UserSession).where(
            UserSession.user_id == current_user.id,
            UserSession.is_valid == True
        )
    )

    session = result.scalar_one_or_none()
    
    if not session:
        raise UnauthorizedException("No active session found")
    
    return ResponseModel(
        success=True,
        message="Session is valid",
        data=SessionResponse(
            user_id=str(current_user.id),
            full_name=current_user.full_name,
            email=current_user.email,
            role=current_user.role_name,
            is_active=True
        ).model_dump()
    )


@router.get("/me", response_model=ResponseModel)
async def get_logged_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current logged-in user profile.
    AUTH-009: Get Logged User API
    """
    return ResponseModel(
        success=True,
        message="User profile retrieved successfully",
        data=UserProfileResponse(
            id=str(current_user.id),
            full_name=current_user.full_name,
            email=current_user.email,
            username=current_user.username,
            phone=current_user.phone,
            role=current_user.role_name,
            hospital_id=str(current_user.hospital_id) if current_user.hospital_id else None,
            is_active=current_user.is_active,
            last_login=current_user.last_login,
            created_at=current_user.created_at
        ).model_dump()
    )


@router.get("/login-history", response_model=ResponseModel)
async def get_login_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get login history for the current user.
    AUTH-010: Login History API
    """
    # Get audit logs for login actions
    result = await db.execute(
        select(AuditLog)
        .where(
            AuditLog.user_id == current_user.id,
            AuditLog.action.in_(["login_success", "login_failed"])
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(50)
    )

    login_logs = result.scalars().all()
    
    history = []
    for log in login_logs:
        history.append({
            "timestamp": log.created_at,
            "action": log.action,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "status": log.status
        })
    
    return ResponseModel(
        success=True,
        message="Login history retrieved successfully",
        data=LoginHistoryResponse(
            history=history
        ).model_dump()
    )