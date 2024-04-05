from django.contrib import messages

class LoginRequiredMessageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path == request.build_absolute_uri('/login/').replace(request.scheme + '://', '').replace(request.get_host(), '', 1) and 'next' in request.GET:
            messages.error(request, "Please login first to access the requested page.")
        return None
