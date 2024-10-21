from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'
    
    authentication_classes = [JWTAuthentication]  # Enforce JWT Authentication
    permission_classes = [IsAuthenticated] 

    @action(detail=True, methods=['get'])
    def expenses(self, request, email=None):
        user = self.get_object()
        if request.user.email != user.email:
            raise PermissionDenied("You do not have permission to access this user's expenses.")
        expenses = user.expense_splits.all()
        data = {
            'paid_expenses': user.paid_expenses.all().values(),
            'involved_expenses': expenses.values(),
        }
        return Response(data)