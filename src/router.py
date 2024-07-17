from typing import Annotated, Dict

from fastapi import HTTPException, APIRouter, Depends, Path, Body
from fastapi.openapi.models import Example
from fastapi.params import Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from fastapi_pagination.cursor import CursorPage

from src import constants, filters, database, schemas, services


def create_boundaries_router(
        service_class: type[services.BaseBoundariesService],
        filter_class: type[filters.BaseFilter],
        request_model: type[schemas.BaseSearchRequest],
        response_model: type[BaseModel],
        response_with_geometry_model: type[BaseModel],
        item_name: str,
        item_name_plural: str,
        example_code: int,
        search_openapi_examples: Dict[str, Example],
):
    router = APIRouter()

    @router.post(
        "/search",
        response_model=CursorPage[response_model],
        summary=f"Search for {item_name_plural} with pagination using various filters",
        description=f"Search for {item_name_plural} with pagination using various filters such as {item_name} codes, "
                    f"feature IDs, name. Additionally, you can filter by GeoJson, EWKT geometry",
        response_description=f"A paginated list of {item_name_plural} matching the search criteria.",
        generate_unique_id_function=lambda route: f"{item_name_plural.replace(' ', '-')}-search"
    )
    def boundaries_search(
            request: Annotated[
                request_model,
                Body(openapi_examples=search_openapi_examples)
            ],
            sort_by: schemas.SearchSortBy = Query(default=schemas.SearchSortBy.code),
            sort_order: schemas.SearchSortOrder = Query(default=schemas.SearchSortOrder.asc),
            db: Session = Depends(database.get_db),
            boundaries_filter: filters.BaseFilter = Depends(filter_class),
            service: services.BaseBoundariesService = Depends(service_class),
    ):
        return service.search(
            db=db,
            sort_by=sort_by,
            sort_order=sort_order,
            request=request,
            boundaries_filter=boundaries_filter,
            srid=None,
            geometry_output_format=None,
        )

    @router.get(
        "/{code}",
        response_model=response_model,
        summary=f"Get {item_name} by code",
        description=f"Retrieve a {item_name} by its unique code.",
        responses={
            404: {"description": f"{item_name} not found".capitalize(), "model": schemas.HTTPExceptionResponse},
        },
        response_description=f"Details of the {item_name} with the specified code.",
        generate_unique_id_function=lambda route: f"{item_name_plural.replace(' ', '-')}-get"
    )
    def get_by_code(
            code: int = Path(
                description=f"The code of the {item_name} to retrieve",
                example=example_code
            ),
            db: Session = Depends(database.get_db),
            service: services.BaseBoundariesService = Depends(service_class),
    ):
        if item := service.get_by_code(db=db, code=code):
            return item
        else:
            raise HTTPException(
                status_code=404,
                detail="Not found",
            )

    @router.get(
        "/{code}/geometry",
        response_model=response_with_geometry_model,
        summary=f"Get {item_name} with geometry by code",
        description=f"Retrieve a {item_name} along with its geometry by its unique code. Optionally specify the SRID "
                    f"for the geometry output.",
        responses={
            404: {"description": f"{item_name} not found".capitalize(), "model": schemas.HTTPExceptionResponse},
        },
        response_description=f"Details of the {item_name} with the specified code, including its geometry.",
        generate_unique_id_function=lambda route: f"{item_name_plural.replace(' ', '-')}-get-with-geometry"
    )
    def get_with_geometry(
            code: int = Path(
                description=f"The code of the {item_name} to retrieve",
                example=example_code
            ),
            db: Session = Depends(database.get_db),
            srid: int = constants.query_srid,
            geometry_output_format: schemas.GeometryOutputFormat = constants.query_geometry_output_type,
            service: services.BaseBoundariesService = Depends(service_class),
    ):
        if row := service.get_by_code(db=db, code=code, srid=srid, geometry_output_format=geometry_output_format):
            return row
        else:
            raise HTTPException(
                status_code=404,
                detail="Not found",
            )

    return router


health_check_router = APIRouter()


# Healthcheck code is adapted from https://gist.github.com/Jarmos-san/0b655a3f75b698833188922b714562e5
@health_check_router.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=schemas.HealthCheck,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": schemas.HTTPExceptionResponse}}
)
def get_health(db: Session = Depends(database.get_db)) -> schemas.HealthCheck:
    """
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    try:
        result = db.execute(text("SELECT spatialite_version()"))
        spatialite_version = result.scalar()
        if spatialite_version:
            return schemas.HealthCheck(healthy=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Not healthy"
            )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Not healthy"
        )


addresses_router = APIRouter()


@addresses_router.post(
    "/search",
    response_model=CursorPage[schemas.Address],
    summary="Search for address with pagination using various filters",
    description="Search for addresses with pagination using various filters such as address codes, "
                "feature IDs, name. Additionally, you can filter by GeoJson, EWKT geometry",
    response_description="A paginated list of addresses matching the search criteria.",
    generate_unique_id_function=lambda _: "addresses-search",
)
def addresses_search(
        request: Annotated[
            schemas.AddressesSearchRequest,
            Body(openapi_examples={
                **constants.openapi_examples_addresses_filtering,
                **constants.openapi_examples_streets_filtering,
                **constants.openapi_examples_residential_areas_filtering,
                **constants.openapi_examples_municipalities_filtering,
                **constants.openapi_examples_counties_filtering,
                **constants.openapi_examples_geometry_filtering,
            })
        ],
        sort_by: schemas.SearchSortBy = Query(default=schemas.SearchSortBy.code),
        sort_order: schemas.SearchSortOrder = Query(default=schemas.SearchSortOrder.asc),
        geometry_output_format: schemas.GeometryOutputFormat = constants.query_geometry_output_type,
        srid: int = constants.query_srid,
        db: Session = Depends(database.get_db),
        addresses_filter: filters.AddressesFilter = Depends(filters.AddressesFilter),
        service: services.AddressesService = Depends(services.AddressesService),
):
    return service.search(
        db,
        sort_by=sort_by,
        sort_order=sort_order,
        request=request,
        srid=srid,
        boundaries_filter=addresses_filter,
        geometry_output_format=geometry_output_format
    )


@addresses_router.get(
    "/{code}",
    response_model=schemas.Address,
    summary="Get address by code",
    description="Retrieve a address by its unique code.",
    responses={
        404: {"description": "Address not found", "model": schemas.HTTPExceptionResponse},
    },
    response_description="Details of the address with the specified code.",
    generate_unique_id_function=lambda route: "addresses-get"
)
def get(
        code: int = Path(
            description="The code of the address to retrieve",
            openapi_examples={
                "example_address_code": {
                    "summary": "Example address code",
                    "value": 155218235
                },
            },
        ),
        srid: int = constants.query_srid,
        geometry_output_format: schemas.GeometryOutputFormat = constants.query_geometry_output_type,
        db: Session = Depends(database.get_db),
        service: services.AddressesService = Depends(services.AddressesService),
):
    if item := service.get_by_code(db=db, code=code, srid=srid, geometry_output_format=geometry_output_format):
        return item
    else:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )


rooms_router = APIRouter()


@rooms_router.post(
    "/search",
    response_model=CursorPage[schemas.Rooms],
    summary="Search for rooms with pagination using various filters",
    description="Search for rooms with pagination using various filters such as address codes, "
                "feature IDs, name. Additionally, you can filter by GeoJson, EWKT geometry",
    response_description="A paginated list of rooms matching the search criteria.",
    generate_unique_id_function=lambda _: "rooms-search"
)
def rooms_search(
        request: Annotated[
            schemas.RoomsSearchRequest,
            Body(openapi_examples={
                **constants.openapi_examples_rooms_filtering,
                **constants.openapi_examples_addresses_filtering,
                **constants.openapi_examples_streets_filtering,
                **constants.openapi_examples_residential_areas_filtering,
                **constants.openapi_examples_municipalities_filtering,
                **constants.openapi_examples_counties_filtering,
                **constants.openapi_examples_geometry_filtering,
            })
        ],
        sort_by: schemas.SearchSortBy = Query(default=schemas.SearchSortBy.code),
        sort_order: schemas.SearchSortOrder = Query(default=schemas.SearchSortOrder.asc),
        srid: int = constants.query_srid,
        geometry_output_format: schemas.GeometryOutputFormat = Query(default=schemas.GeometryOutputFormat.ewkt),
        db: Session = Depends(database.get_db),
        rooms_filter: filters.RoomsFilter = Depends(filters.RoomsFilter),
        service: services.RoomsService = Depends(services.RoomsService),
):
    return service.search(
        db,
        sort_by=sort_by,
        sort_order=sort_order,
        request=request,
        srid=srid,
        boundaries_filter=rooms_filter,
        geometry_output_format=geometry_output_format
    )


@rooms_router.get(
    "/{code}",
    response_model=schemas.Rooms,
    summary="Get room by code",
    description="Retrieve a room by its unique code.",
    responses={
        404: {"description": "Room not found", "model": schemas.HTTPExceptionResponse},
    },
    response_description="Details of the room with the specified code.",
    generate_unique_id_function=lambda route: "rooms-get"
)
def get(
        code: int = Path(
            description="The code of the room to retrieve",
            openapi_examples={
                "example_room_code": {
                    "summary": "Example room code",
                    "value": 194858325
                },
            },
        ),
        srid: int = constants.query_srid,
        geometry_output_format: schemas.GeometryOutputFormat = constants.query_geometry_output_type,
        db: Session = Depends(database.get_db),
        service: services.RoomsService = Depends(services.RoomsService),
):
    if item := service.get_by_code(db=db, code=code, srid=srid, geometry_output_format=geometry_output_format):
        return item
    else:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )
