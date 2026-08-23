from pydantic import BaseModel
from typing import Optional,Any 
from datetime import datetime

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class ResponseModel(BaseModel):
    status_code: int
    message: str
    data: Optional[Any] = None
    error : Optional[Any] = None
    timestamp :  str
    path: str  

def create_response(request : Request, status_code: int, message: str, data = None, error = None):
    return ResponseModel(
        status_code= status_code,
        message= message,
        data= data,
        error= error,
        timestamp= datetime.now().isoformat(),
        path= request.url.path
    )



def register_exception_handlers(app: FastAPI):

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exception: HTTPException):
        res = create_response(
            request,
            status_code=exception.status_code,
            message="Failed",
            error=exception.detail
        )
        return JSONResponse(
            content=res.model_dump(),
            status_code=res.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exception: RequestValidationError):
        res = create_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation Error",
            error=exception.errors()
        )
        return JSONResponse(
            content=res.model_dump(),
            status_code=res.status_code
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exception: Exception):
        res = create_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed",
            error=str(exception)
        )
        return JSONResponse(
            content=res.model_dump(),
            status_code=res.status_code
        )
