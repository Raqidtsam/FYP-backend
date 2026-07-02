from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User


class AdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check admin routes
        if request.path.startswith('/api/admin/'):
            auth_header = request.headers.get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')

            if not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authentication required'}, status=401)

            token = auth_header.replace('Bearer ', '')

            try:
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')

                if not user_id:
                    return JsonResponse({'error': 'Invalid token'}, status=401)

                user = User.objects.get(pk=user_id)

                if not user.is_admin:
                    return JsonResponse({'error': 'Admin access required'}, status=403)

                request.admin_user = user
            except (TokenError, User.DoesNotExist):
                return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response