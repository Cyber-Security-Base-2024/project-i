from django.http import HttpResponse

def home(request):
    html = "<html><body>MORO</body></html>"
    return HttpResponse(html)
