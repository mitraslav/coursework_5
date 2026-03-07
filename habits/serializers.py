from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = '__all__'

    def validate(self, attrs):
        is_pleasant = attrs.get('is_pleasant', getattr(self.instance, 'is_pleasant', False))
        reward = attrs.get('reward', getattr(self.instance, 'reward', None))
        related_habit = attrs.get('related_habit', getattr(self.instance, 'related_habit', None))
        execution_time = attrs.get('execution_time', getattr(self.instance, 'execution_time', None))
        periodicity = attrs.get('periodicity', getattr(self.instance, 'periodicity', 1))
        user = self.context['request'].user

        if reward and related_habit:
            raise serializers.ValidationError(
                'Нельзя одновременно указывать вознаграждение и связанную привычку.'
            )

        if execution_time and execution_time > 120:
            raise serializers.ValidationError(
                'Время выполнения должно быть не больше 120 секунд.'
            )

        if periodicity > 7:
            raise serializers.ValidationError(
                'Нельзя выполнять привычку реже, чем 1 раз в 7 дней.'
            )

        if related_habit:
            if not related_habit.is_pleasant:
                raise serializers.ValidationError(
                    'Связанной может быть только приятная привычка.'
                )
            if related_habit.user != user:
                raise serializers.ValidationError(
                    'Можно привязать только свою привычку.'
                )

        if is_pleasant and reward:
            raise serializers.ValidationError(
                'У приятной привычки не может быть вознаграждения.'
            )

        if is_pleasant and related_habit:
            raise serializers.ValidationError(
                'У приятной привычки не может быть связанной привычки.'
            )

        return attrs