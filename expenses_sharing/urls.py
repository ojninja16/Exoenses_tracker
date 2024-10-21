from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views import UserViewSet
from expenses.views import ExpenseViewSet

# Set up the router for your viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'expenses', ExpenseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Endpoint to obtain the JWT token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Endpoint to refresh the JWT token
]
