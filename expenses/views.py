from rest_framework import viewsets, status,serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from .models import Expense, ExpenseSplit
from .serializers import ExpenseSerializer
import csv
from django.http import HttpResponse
from decimal import Decimal
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication



class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    authentication_classes = [JWTAuthentication]  # Enforce JWT Authentication
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        """
        Handle expense creation with different split types.
        Examples supported:
        1. Equal: Total 3000 split among 4 people = 750 each
        2. Exact: Total 4299 with specific amounts (799, 2000, 1500)
        3. Percentage: Split by percentages (50%, 25%, 25%)
        """
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Extract basic expense data
            split_type = serializer.validated_data['split_type']
            total_amount = serializer.validated_data['amount']
            splits_data = serializer.validated_data['splits']
            
            # Validate splits based on type
            if split_type == 'EQUAL':
                num_people = len(splits_data)
                if num_people == 0:
                    raise serializers.ValidationError("At least one person must be included in the split")
                split_amount = total_amount / Decimal(num_people)
                # Update split amounts
                for split in splits_data:
                    split['amount'] = split_amount
                    split['percentage'] = None

            elif split_type == 'EXACT':
                total_split = sum(Decimal(str(split.get('amount', 0))) for split in splits_data)
                if total_split != total_amount:
                    raise serializers.ValidationError(
                        f"Sum of splits ({total_split}) must equal total amount ({total_amount})"
                    )

            elif split_type == 'PERCENTAGE':
                total_percentage = sum(Decimal(str(split.get('percentage', 0))) for split in splits_data)
                if total_percentage != 100:
                    raise serializers.ValidationError("Percentages must sum to 100%")
                # Calculate amounts based on percentages
                for split in splits_data:
                    percentage = Decimal(str(split['percentage']))
                    split['amount'] = (percentage / 100) * total_amount

            # Create the expense
            expense = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of expenses for a user or all users"""
        user_email = request.query_params.get('user_email')
        
        if user_email:
            # Individual user summary
            paid_expenses = Expense.objects.filter(
                paid_by__email=user_email
            ).aggregate(
                total_paid=Coalesce(Sum('amount'), 0)
            )

            owed_expenses = ExpenseSplit.objects.filter(
                user__email=user_email
            ).aggregate(
                total_owed=Coalesce(Sum('amount'), 0)
            )

            # Get detailed breakdown
            expense_breakdown = ExpenseSplit.objects.filter(
                user__email=user_email
            ).select_related('expense').values(
                'expense__title',
                'expense__amount',
                'expense__split_type',
                'amount',
                'percentage',
                'expense__paid_by__email'
            )

            return Response({
                'user_email': user_email,
                'total_paid': paid_expenses['total_paid'],
                'total_owed': owed_expenses['total_owed'],
                'net_balance': paid_expenses['total_paid'] - owed_expenses['total_owed'],
                'expense_breakdown': expense_breakdown
            })
        else:
            # Overall summary for all users
            users_summary = []
            from users.models import User
            for user in User.objects.all():
                paid = Expense.objects.filter(paid_by=user).aggregate(
                    total=Coalesce(Sum('amount'), 0)
                )['total']
                owed = ExpenseSplit.objects.filter(user=user).aggregate(
                    total=Coalesce(Sum('amount'), 0)
                )['total']
                users_summary.append({
                    'user_email': user.email,
                    'total_paid': paid,
                    'total_owed': owed,
                    'net_balance': paid - owed
                })

            return Response(users_summary)

    @action(detail=False, methods=['get'])
    def download_balance_sheet(self, request):
        """Download detailed balance sheet in CSV format"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'
        writer = csv.writer(response)

        # Write header
        writer.writerow([
            'Date', 'Description', 'Total Amount', 'Paid By', 'Split Type',
            'Participant', 'Share Amount', 'Share Percentage'
        ])

        # Get all expenses with their splits
        expenses = Expense.objects.select_related('paid_by').prefetch_related(
            'splits__user'
        ).order_by('-created_at')

        for expense in expenses:
            for split in expense.splits.all():
                writer.writerow([
                    expense.created_at.strftime('%Y-%m-%d %H:%M'),
                    expense.title,
                    expense.amount,
                    expense.paid_by.email,
                    expense.split_type,
                    split.user.email,
                    split.amount,
                    split.percentage if split.percentage else 'N/A'
                ])

        return response

    @action(detail=False, methods=['get'])
    def get_user_balance_sheet(self, request):
        """Get detailed balance sheet for a specific user"""
        user_email = request.query_params.get('user_email')
        if not user_email:
            return Response(
                {'error': 'user_email parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Get expenses where user is involved
        user_expenses = ExpenseSplit.objects.filter(
            user__email=user_email
        ).select_related(
            'expense',
            'expense__paid_by',
            'user'
        )
        # Get expenses paid by user
        paid_expenses = Expense.objects.filter(
            paid_by__email=user_email
        ).prefetch_related('splits__user')
        balance_sheet = {
            'user_email': user_email,
            'expenses_involved': [{
                'date': exp.expense.created_at.strftime('%Y-%m-%d %H:%M'),
                'description': exp.expense.title,
                'total_amount': exp.expense.amount,
                'paid_by': exp.expense.paid_by.email,
                'split_type': exp.expense.split_type,
                'your_share': exp.amount,
                'your_percentage': exp.percentage
            } for exp in user_expenses],
            'expenses_paid': [{
                'date': exp.created_at.strftime('%Y-%m-%d %H:%M'),
                'description': exp.title,
                'total_amount': exp.amount,
                'split_type': exp.split_type,
                'splits': [{
                    'user': split.user.email,
                    'amount': split.amount,
                    'percentage': split.percentage
                } for split in exp.splits.all()]
            } for exp in paid_expenses]
        }

        return Response(balance_sheet)