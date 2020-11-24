from django.shortcuts import render
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view,permission_classes
from .serializers import DetailsSerializer, AddressSerializer
from .utils import generate_access_token, generate_refresh_token
from .decorators import check_blacklist_token
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
import jwt, json
from django.conf import settings
from ecommerce_api.settings import blackListedTokens
from django.db.utils import IntegrityError
from .models import Address


@api_view(['GET'])
@check_blacklist_token
def profile(request):
    user = request.user
    try:
        serialized_user = DetailsSerializer(user).data
    except AttributeError:
        return Response({'response': 'authorization credentials missing!', 'status': False})
    print('1 ')
    address = Address.objects.filter(userId=user).first()
    if address:
        serialized_address = AddressSerializer(address).data
        del serialized_address['id']
        del serialized_address['userId']
        serialized_user['address'] = serialized_address
    else:
        serialized_user['address'] = '(unavailable)'
    return Response({'user': serialized_user, 'status': True})


@api_view(['POST'])
@check_blacklist_token
def user_address(request):
    jsn = request.data['address']
    area = None if 'area' not in jsn else jsn['area']
    city = None if 'city' not in jsn else jsn['city']
    country = None if 'country' not in jsn else jsn['country']
    pincode = None if 'pincode' not in jsn else jsn['pincode']
    landmark = None if 'landmark' not in jsn else jsn['landmark']
    adr_type = None if 'adr_type' not in jsn else jsn['adr_type']
    if area or city or country or pincode or landmark or adr_type:
        authorization_header = request.headers.get('Authorization')
        if authorization_header is None:
            return Response({'response': 'Authorization credential missing!', 'status': False})
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'response': 'access token expired!', 'status': False})
        User = get_user_model()
        user = User.objects.filter(id=payload['user_id']).first()
        if user is None:
            return Response({'response': 'User with given credentials not found!', 'status': False})
        address = Address.objects.filter(userId=user).first()
        if address:
            address = Address(id=address.id, area=area, city=city, country=country, pinCode=pincode, landmark=landmark, type=adr_type, userId=user)
            address.save()
            address = Address.objects.filter(userId=user).first()
            address = AddressSerializer(address).data
            return Response({'response': 'address successfully modified!', 'status': True, 'address': address})
        address = Address(area=area, city=city, country=country, pinCode=pincode, landmark=landmark, type=adr_type, userId=user)
        address.save()
        address = Address.objects.filter(userId=user).first()
        address = AddressSerializer(address).data
        return Response({'response': 'address successfully saved!', 'status': True, 'address': address})
    else:
        return Response({'response': 'nothing happened!', 'status': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    context = {}
    jsn: dict
    try:
        jsn = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        jsn = {}
    if jsn:
        for k, v in jsn.items():
            if 'password' != k:
                context[k] = jsn[k]
    if not ('email' in jsn and 'username' in jsn and 'password' in jsn):
        return Response({'response': 'Registration Unsuccessful! (required data: email, username, password)', 'status': False})
    try:
        User = get_user_model()
        user = User(email=jsn['email'], username=jsn['username'])
        user.set_password(jsn['password'])
        user.save()
    except IntegrityError as err:
        dup = str(err).split('user_details_')[1].split('_key')[0]
        return Response({'response': f'{dup} already taken by another user, please user another {dup} and try again!', 'duplicate': dup})
    except IndexError as err:
        # print(err)
        return Response({'response': 'duplication found!', 'status': False})
    if jsn:
        return Response({'response': 'user created!', 'status': True, 'context': context})
    return Response({'response': 'user not created!', 'status': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    response = Response()
    if email is None and password is None:
        return Response({'response': 'email and password are missing and are required for authentication', 'status': False})
    user = User.objects.filter(email=email).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    if not user.check_password(password):
        return Response({'response': 'Wrong Password', 'status': False})

    serialized_user = DetailsSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'access_token': access_token,
        'user': serialized_user,
        'status': True
    }
    return response


@api_view(['POST'])
@ensure_csrf_cookie
def logout(request):
    User = get_user_model()
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    access_token = False
    refresh_token = False
    try:
        access_token = authorization_header.split(' ')[1]
        refresh_token = request.COOKIES.get('refreshtoken')
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if not refresh_token:
            return Response({'response': 'Credential not found in request cookies! (you might have already been logged out!)', 'status': False})
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'response': 'your jwt session time has already been out, you have been logged out already!', 'status': True})
        user = User.objects.filter(id=payload['user.id'])
        if user is None:
            return Response({'response': 'user associated with received credential was not found!', 'status': False})
    finally:
        if access_token in blackListedTokens and refresh_token in blackListedTokens:
            return Response({'response': 'already logged out!', 'status': False})
        elif access_token in blackListedTokens:
            blackListedTokens.add(refresh_token)
            return Response({'response': 'already logged out!', 'status': False})
        elif refresh_token in blackListedTokens:
            blackListedTokens.add(access_token)
            return Response({'response': 'already logged out!', 'status': False})
        if access_token:
            blackListedTokens.add(access_token)
        if refresh_token:
            blackListedTokens.add(refresh_token)
        return Response({'response': 'successfully logged out!', 'status': True})


@api_view(['POST'])
@check_blacklist_token
def refresh_token(request):
    User = get_user_model()
    refresh_token = request.COOKIES.get('refreshtoken')
    if not refresh_token:
        return Response({'response': 'authentication credential missing!', 'status': False})
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'refresh token expired!', 'status': False})
    user = User.objects.filter(id=payload['user.id']).first()
    if user is None:
        return Response({'response': 'user not found!', 'status': False})
    access_token = generate_access_token(user)
    return Response({'access_token': access_token, 'status': True})


@api_view(['POST'])
@check_blacklist_token
@ensure_csrf_cookie
def delete_user(request):
    User = get_user_model()
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'Authorization credential missing/expired!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    user = User.objects.filter(id=payload['user_id']).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    user.delete()
    return Response({'response': 'User successfully deleted!', 'status': True})
