def csp_nonce(request):
    """
    CSP nonce'ni barcha template'larga uzatadi.
    SecurityHeadersMiddleware tomonidan request.csp_nonce yaratiladi.
    """
    return {'csp_nonce': getattr(request, 'csp_nonce', '')}
