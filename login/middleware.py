from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # If the user is not authenticated and trying to access the home page
        if request.path == '/home/' and not request.user.is_authenticated:
            return redirect('login')
