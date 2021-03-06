import functools
import json

from django.http.response import HttpResponse
from jsonschema import validate, ValidationError

from .response import HttpResponseIncorrectParameter
from user.models import User


PATTERN_UUID_HEX = r'^[a-z\d]{32}$'

def authenticate(func):
    """
    用户认证

    认证成功request.user为用户对象
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(status=401)
        request.user = user
        return func(request, *args, **kwargs)

    return wrapper


def allow(methods: list):
    """
    api限制请求方式

    @param method: 允许的请求方式列表
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponse(status=404)
            return func(request, *args, **kwargs)
        
        return wrapper

    return decorator


def parameter(schema: object):
    """
    api参数JsonSchema验证

    @param schema: 请求参数JsonSchema

    验证成功request.data为验证后数据
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.META.get('CONTENT_TYPE') == 'application/json':
                try:
                    data = json.loads(request.body)
                except json.decoder.JSONDecodeError as err:
                    return HttpResponseIncorrectParameter(content=err)
            elif request.method == 'POST':
                data = request.POST
            elif request.method == 'GET':
                data = request.GET
            else:
                data = {}
            try:
                validate(data, schema)
            except ValidationError as err:
                return HttpResponseIncorrectParameter(content=err)
            properties = schema.get('properties', {})
            request.data = {
                key: data.get(key) if key in data else properties[key]['default']
                for key in properties
                if key in data or 'default' in properties[key]
            }
            return func(request, *args, **kwargs)
        
        return wrapper

    return decorator


def pagination(default=10, min_size=1, max_size=20):
    """
    分页 限定GET请求, 其余请求不做更改

    @param default: size默认值

    @param min_size: size最小值

    @param min_size: size最大值

    获取参数page, size添加到request.page, request.size
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method != 'GET':
                return func(request, *args, **kwargs)
            page = request.GET.get('page', '1')
            size = request.GET.get('size', str(default))
            try:
                request.page = int(page)
                request.size = min(max(int(size), min_size), max_size)
            except ValueError as err:
                return HttpResponseIncorrectParameter(content=err)
            return func(request, *args, **kwargs)
        
        return wrapper

    return decorator