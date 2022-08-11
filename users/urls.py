from django.urls import path, include

from .views import login_page

app_name = 'accounts'

urlpatterns = [

    path('login', login_page, name='login'),
    #path('', include(('vacations.urls', 'index'), namespace='vacations'))

    #path('success/', success, name='success'),
]
