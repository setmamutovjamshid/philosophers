import secrets

from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Har bir so'rov uchun xavfsizlik headerlarini qo'shuvchi middleware.

    - Content-Security-Policy (CSP): nonce asosida, Tailwind CDN + Google Fonts bilan mos.
    - HSTS: Django SecurityMiddleware orqali settings.py da boshqariladi.
    - Secure cookies: settings.py da SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE orqali.
    """

    def process_request(self, request):
        # Har bir HTTP so'rovi uchun kriptografik nonce yaratish
        request.csp_nonce = secrets.token_urlsafe(16)

    def process_response(self, request, response):
        nonce = getattr(request, 'csp_nonce', secrets.token_urlsafe(16))

        # CSP direktivalari:
        # - script-src: 'unsafe-eval' Tailwind Play CDN uchun zarur (ichida Function() ishlatadi)
        # - style-src: 'unsafe-inline' Tailwind dinamik inline style inject qilgani uchun zarur
        # - img-src: Cloudinary + data: (avatar placeholder), blob: (canvas/preview)
        csp_parts = [
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}' https://cdn.tailwindcss.com 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' data: https://fonts.gstatic.com",
            "img-src 'self' data: blob: https://res.cloudinary.com",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "object-src 'none'",
        ]
        response['Content-Security-Policy'] = "; ".join(csp_parts)

        return response
