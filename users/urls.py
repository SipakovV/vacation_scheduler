from django.urls import path, include

from .views import login_page, logout_view

app_name = 'accounts'

urlpatterns = [

    path('login', login_page, name='login'),
    path('logout', logout_view, name='logout'),
    #path('', include(('vacations.urls', 'index'), namespace='vacations'))

    #path('success/', success, name='success'),
]
