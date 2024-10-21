from rest_framework import serializers
from .models import Expense, ExpenseSplit
from users.serializers import UserSerializer
from users.models import User


class ExpenseSplitSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = ExpenseSplit
        fields = ['id', 'user_email', 'user_details', 'amount', 'percentage']
        read_only_fields = ['user_details']

    def validate(self, data):
        if 'amount' in data and 'percentage' in data:
            if data['amount'] and data['percentage']:
                raise serializers.ValidationError(
                    "Cannot specify both amount and percentage"
                )
        return data

class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True)
    paid_by_email = serializers.EmailField(write_only=True)
    paid_by_details = UserSerializer(source='paid_by', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'split_type', 'paid_by_email', 
                 'paid_by_details', 'splits', 'created_at']
        read_only_fields = ['paid_by_details']

    def validate_splits(self, splits):
        split_type = self.initial_data.get('split_type')
        total_amount = float(self.initial_data.get('amount', 0))

        if split_type == 'PERCENTAGE':
            total_percentage = sum(
                float(split['percentage'] or 0) for split in splits
            )
            if total_percentage != 100:
                raise serializers.ValidationError(
                    "Percentage splits must sum to 100%"
                )
        elif split_type == 'EXACT':
            total_split = sum(
                float(split['amount'] or 0) for split in splits
            )
            if total_split != total_amount:
                raise serializers.ValidationError(
                    "Sum of exact splits must equal total amount"
                )
        
        return splits

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        paid_by_email = validated_data.pop('paid_by_email')
        
        try:
            paid_by_user = User.objects.get(email=paid_by_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"User with email {paid_by_email} does not exist"
            )

        expense = Expense.objects.create(
            paid_by=paid_by_user,
            **validated_data
        )

        # Handle splits based on split_type
        if expense.split_type == 'EQUAL':
            split_amount = expense.amount / len(splits_data)
            for split_data in splits_data:
                user = User.objects.get(email=split_data['user_email'])
                ExpenseSplit.objects.create(
                    expense=expense,
                    user=user,
                    amount=split_amount
                )
        else:
            for split_data in splits_data:
                user = User.objects.get(email=split_data['user_email'])
                ExpenseSplit.objects.create(
                    expense=expense,
                    user=user,
                    amount=split_data.get('amount'),
                    percentage=split_data.get('percentage')
                )

        return expense