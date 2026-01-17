"""Authentication views for the Control Plane API."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token_view(request):
    """Get CSRF token."""
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint that creates a session."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint that destroys the session."""
    logout(request)
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_view(request):
    """Get current user information."""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    })
