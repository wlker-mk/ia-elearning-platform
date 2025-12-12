from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """
    Standardized success response
    """
    response_data = {
        'success': True,
        'message': message,
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code)


def error_response(message='Error occurred', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized error response
    """
    response_data = {
        'success': False,
        'message': message,
    }
    
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status_code)


def paginated_response(queryset, serializer_class, request, message='Success'):
    """
    Standardized paginated response
    """
    from rest_framework.pagination import PageNumberPagination
    
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response({
            'success': True,
            'message': message,
            'data': serializer.data
        })
    
    serializer = serializer_class(queryset, many=True)
    return success_response(data=serializer.data, message=message)