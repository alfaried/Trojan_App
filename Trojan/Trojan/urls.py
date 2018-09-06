from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('AWS_Utilities.urls','AWS_Utilities'), namespace="AWS")),
]
