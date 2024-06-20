from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Customer, Orders, OrderItem, Cart, CartItem
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer, CartItemSerializer, OrderItemSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework import generics
import logging
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required




# Configure logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
def hello_user(request):
    return Response("Hello Developer")

@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register_customer(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_customer(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    print(user)
    if user is not None:
        # Update last login time
        Customer.objects.filter(username=username).update(last_login=timezone.now())

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomerDetail(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Customer.objects.get(username=self.request.user.username)

@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"

        # Send email
        subject = "Password Reset Request"
        message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        plain_message = f"Dear {user.username},\n\nYou requested a password reset. Click the link below to reset your password:\n{reset_url}\n\nIf you did not request this password reset, please ignore this email."
        
        try:
            send_mail(subject, plain_message, 'avvsteja1100@gmail.com', [email], html_message=message)
        except BadHeaderError:
            return Response({"detail": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return Response({"detail": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Password reset email sent"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"detail": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('password')
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password has been reset"}, status=status.HTTP_200_OK)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_cart(request, product_id=None):
    user = request.user

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_data = []
            total_price = 0

            for cart_item in cart_items:
                product = cart_item.product
                product_data = {
                    'product_id':product.id,
                    'product_name': product.name,
                    'price': product.price,
                    'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
                    'quantity': cart_item.quantity,
                    'total_price': product.price * cart_item.quantity
                }
                cart_data.append(product_data)
                total_price += product.price * cart_item.quantity

            return Response({'cart_items': cart_data, 'total_price': total_price})
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if new_quantity is None or int(new_quantity) < 1:
            return Response({"detail": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = int(new_quantity)
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"detail": "Cart item deleted"}, status=status.HTTP_204_NO_CONTENT)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({"detail": "Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return Response({"detail": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    order = Orders.objects.create(user=user, total_amount=total_amount)

    order_items = []
    order_items_data = []
    for cart_item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
        )
        order_items.append(order_item)
        order_items_data.append({
            'product_name': cart_item.product.name,
            'price': cart_item.product.price,
            'image_url': request.build_absolute_uri(cart_item.product.image.url) if cart_item.product.image else None,  # Build absolute URL for the image
            'quantity': cart_item.quantity,
            'total_price': cart_item.product.price * cart_item.quantity
        })

    # Clear the cart after placing order
    cart_items.delete()

    # Send receipt email
    subject = "Order Confirmation"
    message = render_to_string('order_confirmation_email.html', {
        'user': user,
        'order': order,
        'order_items': order_items_data,
    })
    plain_message = f"Dear {user.username},\n\nThank you for your purchase! Your order has been placed successfully.\n\nOrder ID: {order.id}\nTotal Amount: {order.total_amount}\n\nThank you for shopping with us!"
    
    try:
        send_mail(subject, plain_message, 'avvsteja1100@gmail.com', [user.email], html_message=message)
    except BadHeaderError:
        return Response({"detail": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return Response({"detail": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"detail": "Order placed successfully"}, status=status.HTTP_201_CREATED)

class UserOrderList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Orders.objects.filter(user=self.request.user)


class OrderDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            order = Orders.objects.get(pk=pk)
            if order.user != self.request.user:
                raise Http404
            return order
        except Orders.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)


    def delete(self, request, pk, format=None):
        order = self.get_object(pk)
        order.delete()
        return Response({"detail": f"Order with ID {pk} has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)