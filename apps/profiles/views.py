from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserProfileSerializer, ChangePasswordSerializer, UpdateUserProfileSerializer

class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'change_password':
            return ChangePasswordSerializer
        return UserProfileSerializer
        if self.request.method in ['PATCH', 'PUT']:
            return UpdateUserProfileSerializer            
        return UserProfileSerializer
    def get_object(self):
        """Override to always return the logged-in user"""
        return self.request.user
    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def my_profile(self, request):
        user = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = UpdateUserProfileSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()                
                user.refresh_from_db()
                
                read_serializer = UserProfileSerializer(user)
                return Response(read_serializer.data)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Incorrect current password."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            return Response(
                {"message": "Password updated successfully."}, 
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)