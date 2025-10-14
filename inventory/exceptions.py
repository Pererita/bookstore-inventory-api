from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            "errors": []
        }
        
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    detail = f"{key}: {' '.join(map(str, value))}"
                else:
                    detail = str(value)
                
                error = {"status": response.status_code, "detail": detail}
                custom_response["errors"].append(error)
        else:
             custom_response["errors"].append({
                 "status": response.status_code,
                 "detail": str(response.data.get('detail', response.data))
             })
        
        response.data = custom_response

    return response