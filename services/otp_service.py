import requests
from flask import current_app
from models.otp import OTP
import re

class OTPService:
    """Service for handling OTP operations with Fast2SMS"""

    @staticmethod
    def normalize_phone_number(phone):
        """Normalize phone number to 10 digits without country code"""
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', phone)

        # Remove country code if present
        if phone.startswith('91') and len(phone) == 12:
            phone = phone[2:]
        elif phone.startswith('+91') and len(phone) == 13:
            phone = phone[3:]

        return phone

    @staticmethod
    def validate_phone_number(phone):
        """Validate Indian phone number"""
        normalized = OTPService.normalize_phone_number(phone)
        return len(normalized) == 10 and normalized.isdigit()

    @staticmethod
    def send_otp(phone_number):
        """Send OTP to the given phone number"""
        try:
            # Validate phone number
            if not OTPService.validate_phone_number(phone_number):
                return False, "Invalid phone number format"

            # Normalize phone number
            normalized_phone = OTPService.normalize_phone_number(phone_number)

            # Check if it's the test number to save SMS credits
            if normalized_phone == "9123187562":
                # Create test OTP with fixed code
                otp_record = OTP.create_new_otp(
                    normalized_phone,
                    current_app.config.get('OTP_LENGTH', 6),
                    current_app.config.get('OTP_EXPIRY_MINUTES', 10)
                )
                # Override with fixed test OTP
                otp_record.otp_code = "123456"
                from database import db
                db.session.commit()

                current_app.logger.info(f"Test OTP created for {normalized_phone}: 123456")
                return True, f"OTP sent successfully to {normalized_phone}"

            # Create new OTP for real numbers
            otp_record = OTP.create_new_otp(
                normalized_phone,
                current_app.config.get('OTP_LENGTH', 6),
                current_app.config.get('OTP_EXPIRY_MINUTES', 10)
            )

            # Send OTP via Fast2SMS
            success, message = OTPService._send_via_fast2sms(normalized_phone, otp_record.otp_code)

            if success:
                return True, f"OTP sent successfully to {normalized_phone}"
            else:
                return False, f"Failed to send OTP: {message}"

        except Exception as e:
            current_app.logger.error(f"Error sending OTP: {str(e)}")
            return False, f"Error sending OTP: {str(e)}"

    @staticmethod
    def _send_via_fast2sms(phone_number, otp_code):
        """Send OTP via Fast2SMS API using Quick SMS route"""
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"

            api_key = current_app.config.get('FAST2SMS_API_KEY')
            if not api_key:
                return False, "Fast2SMS API key not configured"

            # Create OTP message
            message = f"Your Om Engineers OTP is: {otp_code}. Valid for 2 minutes. Do not share with anyone."

            payload = {
                "authorization": api_key,
                "route": "q",
                "message": message,
                "numbers": phone_number,
                "flash": "0"
            }

            headers = {
                'cache-control': "no-cache"
            }

            response = requests.get(url, headers=headers, params=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('return', False):
                    return True, "OTP sent successfully"
                else:
                    error_msg = result.get('message', ['Unknown error'])[0]
                    return False, error_msg
            else:
                return False, f"API request failed with status {response.status_code}"

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Fast2SMS API error: {str(e)}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            current_app.logger.error(f"Unexpected error in Fast2SMS: {str(e)}")
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def verify_otp(phone_number, otp_code):
        """Verify OTP for the given phone number"""
        try:
            # Normalize phone number
            normalized_phone = OTPService.normalize_phone_number(phone_number)

            # Verify OTP using the model
            success, message = OTP.verify_otp(normalized_phone, otp_code)
            return success, message

        except Exception as e:
            current_app.logger.error(f"Error verifying OTP: {str(e)}")
            return False, f"Error verifying OTP: {str(e)}"

    @staticmethod
    def resend_otp(phone_number):
        """Resend OTP to the given phone number"""
        return OTPService.send_otp(phone_number)

    @staticmethod
    def cleanup_expired_otps():
        """Clean up expired OTPs from database"""
        try:
            count = OTP.cleanup_expired_otps()
            return True, f"Cleaned up {count} expired OTPs"
        except Exception as e:
            current_app.logger.error(f"Error cleaning up OTPs: {str(e)}")
            return False, f"Error cleaning up OTPs: {str(e)}"

    @staticmethod
    def get_otp_status(phone_number):
        """Get OTP status for debugging purposes"""
        try:
            normalized_phone = OTPService.normalize_phone_number(phone_number)
            otp_record = OTP.query.filter_by(
                phone_number=normalized_phone,
                is_verified=False
            ).first()

            if otp_record:
                return True, otp_record.to_dict()
            else:
                return False, "No active OTP found"
        except Exception as e:
            return False, f"Error getting OTP status: {str(e)}"