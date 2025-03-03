from rest_framework.response import Response
from rest_framework import status

class ResponseMixin:
    """
    Mixin to standardize API responses across the application.
    """
    @staticmethod
    def success_response(data=None, message="Operation successful", status_code=status.HTTP_200_OK):
        """
        Standard success response format
        """
        response = {
            "status": "success",
            "message": message
        }
        
        if data is not None:
            response["data"] = data
            
        return Response(response, status=status_code)
    
    @staticmethod
    def error_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Standard error response format
        """
        response = {
            "status": "error",
            "message": message
        }
        
        if errors is not None:
            response["errors"] = errors
            
        return Response(response, status=status_code)