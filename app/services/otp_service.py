import random
import string
from app.core.redis import redis_client

class OTPService:

    OTP_EXPIRY = 5 * 60  # 5 Minutes

    VERIFIED_EXPIRY = 5 * 60

    # Generate OTP
    @staticmethod
    async def generate_otp() -> str:
        return "".join(
            random.choices(
                string.digits,
                k=6,
            )
        )

    # Save OTP
    @staticmethod
    async def save_otp(
        email: str,
        otp: str,
    ):

        await redis_client.set(
            f"otp:{email}",
            otp,
            ex=OTPService.OTP_EXPIRY,
        )

    # Get OTP
    @staticmethod
    async def get_otp(
        email: str,
    ):

        return await redis_client.get(
            f"otp:{email}"
        )

    # Delete OTP
    @staticmethod
    async def delete_otp(
        email: str,
    ):

        await redis_client.delete(
            f"otp:{email}"
        )

    # OTP Exists
    @staticmethod
    async def otp_exists(
        email: str,
    ):

        return await redis_client.exists(
            f"otp:{email}"
        )

    # Remaining Time
    @staticmethod
    async def ttl(
        email: str,
    ):

        return await redis_client.ttl(
            f"otp:{email}"
        )

    # Mark Verified
    @staticmethod
    async def mark_verified(
        email: str,
    ):

        await redis_client.set(
            f"otp_verified:{email}",
            "true",
            ex=OTPService.VERIFIED_EXPIRY,
        )

    # Is Verified
    @staticmethod
    async def is_verified(
        email: str,
    ):

        value = await redis_client.get(
            f"otp_verified:{email}"
        )

        return value == "true"

    # Remove Verification
    @staticmethod
    async def remove_verification(
        email: str,
    ):

        await redis_client.delete(
            f"otp_verified:{email}"
        )

    # Clear All OTP Data
    @staticmethod
    async def clear(
        email: str,
    ):

        await redis_client.delete(
            f"otp:{email}",
            f"otp_verified:{email}",
        )