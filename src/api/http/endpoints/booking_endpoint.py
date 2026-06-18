from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import UUID7

from api.http.common_exceptions import internal_server_error, not_found
from api.http.response_models import DataManyResponse, DataResponse, ErrorResponse, Meta
from api.http.schemas import (
    BookingCreateSchema,
    BookingGetAllSchema,
    BookingResponseSchema,
)
from dependencies import booking_srv
from domain.dto import BookingCreateInput
from domain.filters import BookingFilter
from errors import NotFoundError, UnprocessableError
from libs.logger.custom_logger import get_logger


if TYPE_CHECKING:
    from services import BookingService

logger = get_logger(__name__)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
)


@router.post(
    "/",
    summary="Create booking",
    response_model=DataResponse[BookingResponseSchema],
    responses={status.HTTP_201_CREATED: {"description": "Success"}},
)
async def create(
    inp: BookingCreateSchema, booking_srv: "BookingService" = Depends(booking_srv)
):
    try:
        dto = BookingCreateInput(**inp.model_dump())
        booking = await booking_srv.create(dto)
        return JSONResponse(
            {
                "data": BookingResponseSchema.model_validate(
                    booking, from_attributes=True
                ).model_dump(mode="json")
            },
            status_code=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.exception("Error during creating booking: %s", str(e))
        raise internal_server_error()


@router.get(
    "/{booking_id}",
    summary="Get booking",
    response_model=DataResponse[BookingResponseSchema],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_one(
    booking_id: UUID7, booking_srv: "BookingService" = Depends(booking_srv)
):
    try:
        booking = await booking_srv.get_one(booking_id)
        return JSONResponse(
            {
                "data": BookingResponseSchema.model_validate(
                    booking, from_attributes=True
                ).model_dump(mode="json")
            }
        )

    except NotFoundError:
        raise not_found("Booking not found or cancelled")
    except Exception as e:
        logger.exception("Error during getting booking: %s", str(e))
        raise internal_server_error()


@router.get(
    "/",
    summary="Get all bookings",
    response_model=DataManyResponse[BookingResponseSchema],
    responses={status.HTTP_200_OK: {"description": "Success"}},
)
async def get_all(
    inp: Annotated[BookingGetAllSchema, Query()],
    booking_srv: "BookingService" = Depends(booking_srv),
):
    try:
        booking_filter = BookingFilter(statuses=inp.statuses)
        bookings, total = await booking_srv.get_all(booking_filter, inp.limit, inp.offset)

        data = [
            BookingResponseSchema.model_validate(b, from_attributes=True).model_dump(
                mode="json"
            )
            for b in bookings
        ]
        meta = Meta(page=inp.page, size=inp.size, total=total)

        return {"data": data, "meta": meta}

    except Exception as e:
        logger.exception("Error during fetching bookings: %s", str(e))
        raise internal_server_error()


# * Заметка: Было бы правильнее использовать POST /booking/{id}/cancel (оставил как в ТЗ)
@router.delete(
    "/{booking_id}",
    summary="Cancel booking",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Success"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Unprocessable operation"},
    },
)
async def cancel(booking_id: UUID7, booking_srv: "BookingService" = Depends(booking_srv)):
    try:
        await booking_srv.cancel(booking_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except UnprocessableError as e:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )

    except Exception as e:
        logger.exception("Error during cancelling booking: %s", str(e))
        raise internal_server_error()
