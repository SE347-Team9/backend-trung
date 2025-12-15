from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate

from .serializers import (
    UserSerializer, UserCreateSerializer, RegisterSerializer, 
    LoginSerializer, ChangePasswordSerializer
)

User = get_user_model()

# ============================================================
# PERMISSION CLASSES - Phân quyền truy cập
# ============================================================

class IsAdmin(IsAuthenticated):
    """Chỉ Admin mới được phép"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


class IsStaff(IsAuthenticated):
    """Admin hoặc Staff"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in ['admin', 'staff']


class IsAgency(IsAuthenticated):
    """Chỉ Agency"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'agency'


# ============================================================
# AUTH VIEWS - Đăng ký, Đăng nhập, Đăng xuất
# ============================================================

class RegisterView(APIView):
    """
    API Đăng ký tài khoản mới
    - Mặc định role là 'agency' (đại lý)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'message': 'Đăng ký thành công',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API Đăng nhập
    - Trả về token và thông tin user (bao gồm role)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Vui lòng điền username và password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': 'Username hoặc password không đúng'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Tài khoản đã bị vô hiệu hóa'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Đăng nhập thành công',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'role_display': user.get_role_display(),
            }
        })


class LogoutView(APIView):
    """API Đăng xuất"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Đăng xuất thành công'})


class ProfileView(APIView):
    """API Xem và cập nhật profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """API Đổi mật khẩu"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Mật khẩu cũ không đúng'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Đổi mật khẩu thành công'})


# ============================================================
# USER MANAGEMENT VIEWSET - Quản lý tài khoản (Admin only)
# ============================================================

class UserViewSet(viewsets.ModelViewSet):
    """
    API Quản lý tài khoản người dùng
    - Chỉ Admin mới được phép
    """
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Kích hoạt/Vô hiệu hóa tài khoản"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({
            'message': f"Tài khoản {'đã kích hoạt' if user.is_active else 'đã vô hiệu hóa'}",
            'is_active': user.is_active
        })
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset mật khẩu về mặc định (123456)"""
        user = self.get_object()
        user.set_password('123456')
        user.save()
        return Response({'message': 'Đã reset mật khẩu về 123456'})
