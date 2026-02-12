from django.utils import translation
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = self.get_jwt_user(request)

        if user:
            try:
                settings = getattr(user, 'general_settings', None)
                if settings and settings.language:
                    translation.activate(settings.language)
                    request.LANGUAGE_CODE = settings.language
            except Exception:
                pass

        response = self.get_response(request)
        translation.deactivate()
        return response

    def get_jwt_user(self, request):
        try:
            auth_result = JWTAuthentication().authenticate(request)
            if auth_result:
                return auth_result[0]
        except Exception:
            pass
        
        if request.user.is_authenticated:
            return request.user
            
        return None