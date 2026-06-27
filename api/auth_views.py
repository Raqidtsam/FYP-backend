from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    full_name = request.data.get('full_name')
    nationality = request.data.get('nationality')
    contact = request.data.get('contact')

    if not email or not password:
        return Response(
            {'error': 'Email and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create(
        email=email,
        password_hash=password,
        full_name=full_name or '',
        nationality=nationality or '',
        contact=contact or '',
    )

    refresh = RefreshToken()
    refresh['user_id'] = user.id

    return Response({
        'message': 'Registration successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'nationality': user.nationality,
            'contact': user.contact,
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not check_password(password, user.password_hash):
        return Response(
            {'error': 'Invalid email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken()
    refresh['user_id'] = user.id

    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'nationality': user.nationality,
            'contact': user.contact,
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['GET'])
def profile(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return Response({'error': 'No token provided'}, status=401)

    try:
        # Decode JWT token
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        user_id = access_token.get('user_id')

        user = User.objects.get(id=user_id)

        return Response({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'nationality': user.nationality,
            'contact': user.contact,
        })
    except Exception:
        return Response({'error': 'Invalid token'}, status=401)