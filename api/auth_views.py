from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from .models import User, PasswordResetToken
from .validators import validate_password_strength


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    full_name = request.data.get('full_name')
    nationality = request.data.get('nationality')
    contact = request.data.get('contact')

    is_valid, errors = validate_password_strength(password)
    if not is_valid:
        return Response({
            'error': 'Weak password',
            'details': errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
    refresh['user_id'] = user.pk

    return Response({
        'message': 'Registration successful',
        'user': {
            'id': user.pk,
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
    refresh['user_id'] = user.pk

    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.pk,
            'email': user.email,
            'full_name': user.full_name,
            'nationality': user.nationality,
            'contact': user.contact,
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def profile(request):
    auth_header = (
        request.headers.get('Authorization', '') or
        request.META.get('HTTP_AUTHORIZATION', '')
    )

    if not auth_header.startswith('Bearer '):
        return Response({'error': 'No token provided'}, status=401)

    token = auth_header.replace('Bearer ', '')

    try:
        access_token = AccessToken(token)
        user_id = access_token.get('user_id')

        if not user_id:
            return Response({'error': 'Invalid token'}, status=401)

        user = User.objects.get(pk=user_id)

        profile_pic_url = None
        if user.profile_picture:
            profile_pic_url = request.build_absolute_uri(user.profile_picture.url)

        return Response({
            'id': user.pk,
            'email': user.email,
            'full_name': user.full_name,
            'nationality': user.nationality,
            'contact': user.contact,
            'profile_picture': profile_pic_url,
        })
    except TokenError:
        return Response({'error': 'Invalid or expired token'}, status=401)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_profile(request):
    auth_header = (
        request.headers.get('Authorization', '') or
        request.META.get('HTTP_AUTHORIZATION', '')
    )

    if not auth_header.startswith('Bearer '):
        return Response({'error': 'No token provided'}, status=401)

    token = auth_header.replace('Bearer ', '')

    try:
        access_token = AccessToken(token)
        user_id = access_token.get('user_id')

        if not user_id:
            return Response({'error': 'Invalid token'}, status=401)

        user = User.objects.get(pk=user_id)

        if 'full_name' in request.data:
            user.full_name = request.data['full_name']
        if 'email' in request.data:
            user.email = request.data['email']
        if 'nationality' in request.data:
            user.nationality = request.data['nationality']
        if 'contact' in request.data:
            user.contact = request.data['contact']
        if 'password' in request.data and request.data['password']:
            user.password_hash = make_password(request.data['password'])
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        if 'remove_picture' in request.data and request.data['remove_picture'] == 'true':
            if user.profile_picture:
                user.profile_picture.delete(save=False)
            user.profile_picture = None

        user.save()

        profile_pic_url = None
        if user.profile_picture:
            profile_pic_url = request.build_absolute_uri(user.profile_picture.url)

        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.pk,
                'email': user.email,
                'full_name': user.full_name,
                'nationality': user.nationality,
                'contact': user.contact,
                'profile_picture': profile_pic_url,
            }
        })
    except TokenError:
        return Response({'error': 'Invalid or expired token'}, status=401)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send OTP to user's email"""
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'message': 'If the email exists, an OTP has been sent'})

    # Generate OTP
    token = PasswordResetToken.generate_otp(user)

    # Send OTP via email
    subject = 'Smart Geo Investment - Password Reset Code'
    message = f'''
Hello {user.full_name},

You requested a password reset for your Smart Geo Investment account.

Your verification code is: {token.otp_code}

This code will expire in 10 minutes.

If you did not request this, please ignore this email.

Regards,
Smart Geo Investment Team
Zanzibar, Tanzania
'''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"Password reset email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    return Response({
        'message': 'If the email exists, an OTP has been sent',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP code"""
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'error': 'Email and OTP required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or OTP'}, status=status.HTTP_400_BAD_REQUEST)

    token = PasswordResetToken.objects.filter(
        user=user,
        otp_code=otp,
        is_used=False
    ).order_by('-created_at').first()

    if not token or not token.is_valid():
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'message': 'OTP verified successfully',
        'verified': True,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using OTP"""
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')

    if not email or not otp or not new_password:
        return Response(
            {'error': 'Email, OTP and new password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 6:
        return Response(
            {'error': 'Password must be at least 6 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

    token = PasswordResetToken.objects.filter(
        user=user,
        otp_code=otp,
        is_used=False
    ).order_by('-created_at').first()

    if not token or not token.is_valid():
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

    # Reset password
    user.password_hash = make_password(new_password)
    user.save()

    # Mark OTP as used
    token.is_used = True
    token.save()

    return Response({'message': 'Password reset successfully'})