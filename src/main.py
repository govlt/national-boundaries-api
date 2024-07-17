import os

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_pagination import add_pagination
from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from src import constants, filters, router, schemas, services

if SENTRY_DSN := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = FastAPI(
    title="National Boundaries and Addresses API of Lithuania",
    summary="Access comprehensive data on national boundaries and addresses registered in the Republic of Lithuania",
    description='This API provides detailed information and geometries about counties, municipalities, elderships, '
                'residential areas, streets, addresses, and rooms.<br>ReDoc style documentation can be found <a '
                'href="/redoc">here</a>.<br>'
                '<br><br>'
                'This API is licensed under the '
                '[MIT License](https://github.com/govlt/national-boundaries-api#license).'
                '<br> '
                'Data from this API is licensed under '
                '[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.lt). For more information, '
                'visit [Registrų centras](https://www.registrucentras.lt/p/1187).',
    version="0.0.1",
    terms_of_service="https://www.registrucentras.lt/p/1187",
    docs_url="/",
    contact={
        "name": "Karolis Vyčius",
        "url": "https://vycius.lt/",
        "email": "karolis@vycius.lt",
    },
    license_info={
        "name": "MIT for API and CC BY 4.0 for data",
        "url": "https://github.com/govlt/national-boundaries-api#license",
        "identifier": "CC-BY-4.0",
    },
)

app.include_router(
    router.create_boundaries_router(
        service_class=services.CountiesService,
        response_model=schemas.County,
        response_with_geometry_model=schemas.CountyWithGeometry,
        filter_class=filters.CountiesFilter,
        request_model=schemas.CountiesSearchRequest,
        item_name="county",
        item_name_plural="counties",
        example_code=10,
        search_openapi_examples={
            **constants.openapi_examples_counties_filtering,
            **constants.openapi_examples_geometry_filtering,
        },
    ),
    prefix="/v1/counties",
    tags=["counties"],
)

app.include_router(
    router.create_boundaries_router(
        service_class=services.MunicipalitiesService,
        response_model=schemas.Municipality,
        response_with_geometry_model=schemas.MunicipalityWithGeometry,
        filter_class=filters.MunicipalitiesFilter,
        request_model=schemas.MunicipalitiesSearchRequest,
        item_name="municipality",
        item_name_plural="municipalities",
        example_code=13,
        search_openapi_examples={
            **constants.openapi_examples_municipalities_filtering,
            **constants.openapi_examples_counties_filtering,
            **constants.openapi_examples_geometry_filtering,
        },
    ),
    prefix="/v1/municipalities",
    tags=["municipalities"],
)

app.include_router(
    router.create_boundaries_router(
        service_class=services.EldershipsService,
        response_model=schemas.Eldership,
        response_with_geometry_model=schemas.EldershipWithGeometry,
        filter_class=filters.EldershipsFilter,
        request_model=schemas.EldershipsSearchRequest,
        item_name="eldership",
        item_name_plural="elderships",
        example_code=1306,
        search_openapi_examples={
            **constants.openapi_examples_elderships_filtering,
            **constants.openapi_examples_municipalities_filtering,
            **constants.openapi_examples_counties_filtering,
            **constants.openapi_examples_geometry_filtering,
        },
    ),
    prefix="/v1/elderships",
    tags=["elderships"],
)

app.include_router(
    router.create_boundaries_router(
        service_class=services.ResidentialAreasService,
        response_model=schemas.ResidentialArea,
        response_with_geometry_model=schemas.ResidentialAreaWithGeometry,
        filter_class=filters.ResidentialAreasFilter,
        request_model=schemas.ResidentialAreasSearchRequest,
        item_name="residential area",
        item_name_plural="residential areas",
        example_code=31003,
        search_openapi_examples={
            **constants.openapi_examples_residential_areas_filtering,
            **constants.openapi_examples_municipalities_filtering,
            **constants.openapi_examples_counties_filtering,
            **constants.openapi_examples_geometry_filtering,
        },
    ),
    prefix="/v1/residential-areas",
    tags=["residential-areas"],
)

app.include_router(
    router.create_boundaries_router(
        service_class=services.StreetsService,
        response_model=schemas.Street,
        response_with_geometry_model=schemas.StreetWithGeometry,
        filter_class=filters.StreetsFilter,
        request_model=schemas.StreetsSearchRequest,
        item_name="street",
        item_name_plural="streets",
        example_code=1453778,
        search_openapi_examples={
            **constants.openapi_examples_streets_filtering,
            **constants.openapi_examples_residential_areas_filtering,
            **constants.openapi_examples_municipalities_filtering,
            **constants.openapi_examples_counties_filtering,
            **constants.openapi_examples_geometry_filtering,
        },
    ),
    prefix="/v1/streets",
    tags=["streets"],
)

app.include_router(
    router.addresses_router,
    prefix="/v1/addresses",
    tags=["addresses"],
)

app.include_router(
    router.rooms_router,
    prefix="/v1/rooms",
    tags=["rooms"],
)

app.include_router(router.health_check_router)


@app.exception_handler(filters.InvalidFilterGeometry)
def invalid_request_geometry_exception_handler(request, exc: filters.InvalidFilterGeometry):
    raise RequestValidationError(
        errors=(
            ValidationError.from_exception_data(
                "ValueError",
                [
                    InitErrorDetails(
                        type=PydanticCustomError(
                            "invalid_geometry",
                            "Input should be a valid geometry with SRID (spatial reference identifier)",
                        ),
                        loc=("geometry", exc.field),
                        input=exc.value
                    )
                ],
            )
        ).errors()
    )


add_pagination(app)


def main() -> None:
    uvicorn.run("src.main:app", host="0.0.0.0", server_header=False)


if __name__ == "__main__":
    main()
