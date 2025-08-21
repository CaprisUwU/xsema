from fastapi import Request
from fastapi.responses import JSONResponse

async def standard_error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        if 400 <= response.status_code < 600:
            return JSONResponse(
                content={"error": "Request failed", "code": response.status_code},
                status_code=response.status_code
            )
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "type": type(e).__name__}
        )
