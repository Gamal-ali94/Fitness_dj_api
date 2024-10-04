from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    adding password as write_only field so it doesn't show when outputting data and only allowed to be writable
    during update or create overriding the create method to hash the password we first use pop to take the password
    out to handle separately creating the user with the rest of the validated_data using **validated_data,
    hashing the password and saving and returning user
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'bio', 'profile_picture']

    # overriding create to hash passwords
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """
    adding required=False to password so its not required to update it everytime they update they profile
    adding email as a read_only_field so its not allowed to be updated
    overriding the update method to check if password is being updated or no
    first we try to pop the password or its set to None
    if Password we set the password to the new one
    """
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'bio', 'profile_picture']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

