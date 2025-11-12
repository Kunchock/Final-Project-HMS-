from django.core.cache import cache
from django.utils import timezone
import hashlib


class LoginAttemptTracker:
    """
    Rate-limiting for HMS login attempts using email + IP.
    Compatible with email-only LoginForm.
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 15 * 60  # 15 minutes
    ATTEMPT_WINDOW = 15 * 60    # Track attempts within 15 minutes

    @classmethod
    def _get_cache_key(cls, email, ip_address):
        """Unique key for login attempts"""
        data = f"{email}:{ip_address}"
        return f"login_attempts:{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    @classmethod
    def _get_lockout_key(cls, email, ip_address):
        """Unique key for lockout"""
        data = f"{email}:{ip_address}"
        return f"login_lockout:{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    @classmethod
    def get_client_ip(cls, request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @classmethod
    def is_locked_out(cls, email, ip_address):
        """Check if email+IP is locked"""
        lockout_key = cls._get_lockout_key(email, ip_address)
        lockout_until = cache.get(lockout_key)

        if not lockout_until:
            return False, 0

        now = timezone.now().timestamp()
        if now >= lockout_until:
            cache.delete(lockout_key)
            return False, 0

        remaining = int(lockout_until - now)
        return True, remaining

    @classmethod
    def record_failed_attempt(cls, email, ip_address):
        """Record failed login; return if now locked"""
        cache_key = cls._get_cache_key(email, ip_address)

        attempts_data = cache.get(cache_key, [0, timezone.now().timestamp()])
        attempt_count, first_attempt = attempts_data
        now = timezone.now().timestamp()

        # Reset if outside attempt window
        if now - first_attempt > cls.ATTEMPT_WINDOW:
            attempt_count = 0
            first_attempt = now

        attempt_count += 1
        cache.set(cache_key, [attempt_count, first_attempt], cls.ATTEMPT_WINDOW)

        if attempt_count >= cls.MAX_ATTEMPTS:
            lockout_key = cls._get_lockout_key(email, ip_address)
            lockout_until = now + cls.LOCKOUT_DURATION
            cache.set(lockout_key, lockout_until, cls.LOCKOUT_DURATION)
            cache.delete(cache_key)
            return True, cls.LOCKOUT_DURATION

        return False, 0

    @classmethod
    def clear_attempts(cls, email, ip_address):
        """Clear attempts on successful login"""
        cache.delete(cls._get_cache_key(email, ip_address))
        cache.delete(cls._get_lockout_key(email, ip_address))

    @classmethod
    def get_remaining_attempts(cls, email, ip_address):
        """Return remaining attempts before lockout"""
        attempts_data = cache.get(cls._get_cache_key(email, ip_address), [0, timezone.now().timestamp()])
        attempt_count = attempts_data[0]
        return max(0, cls.MAX_ATTEMPTS - attempt_count)
