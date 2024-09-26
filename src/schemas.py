import abc
import datetime
import enum
from typing import Optional, List

from pydantic import BaseModel, Field


class SearchSortBy(enum.StrEnum):
    code = 'code'
    name = 'name'
    feature_id = 'feature_id'
    created_at = 'created_at'


class AddressSearchSortBy(enum.StrEnum):
    code = 'code'
    plot_or_building_number = 'plot_or_building_number'
    building_block_number = 'building_block_number'
    postal_code = 'postal_code'
    feature_id = 'feature_id'
    created_at = 'created_at'


class RoomsSearchSortBy(enum.StrEnum):
    code = 'code'
    room_number = 'room_number'
    created_at = 'created_at'


class ParcelsSearchSortBy(enum.StrEnum):
    unique_number = 'unique_number'
    cadastral_number = 'cadastral_number'
    updated_at = 'updated_at'
    area_ha = 'area_ha'


class SearchSortOrder(str, enum.Enum):
    asc = 'asc'
    desc = 'desc'


class GeometryOutputFormat(str, enum.Enum):
    ewkt = 'ewkt'
    ewkb = 'ewkb'


class Geometry(BaseModel):
    srid: int = Field(description="Spatial Reference Identifier (SRID) for the geometry")
    data: str = Field(description="Geometry data in WKB (Well-Known Binary) format, represented as a hex string")


class ShortCounty(BaseModel):
    code: int = Field(description="Unique code of the county")
    feature_id: int = Field(description="Feature ID of the county")
    name: str = Field(description="Name of the county")

    class Config:
        from_attributes = True


class County(ShortCounty):
    area_ha: float = Field(description="Area of the county in hectares")
    created_at: datetime.date = Field(description="Date of creation of the county")

    class Config:
        from_attributes = True


class CountyWithGeometry(County):
    geometry: Geometry = Field(description="Geometry information of the county")


class ShortMunicipality(BaseModel):
    code: int = Field(description="Unique code of the municipality")
    feature_id: int = Field(description="Feature ID of the municipality")
    name: str = Field(description="Name of the municipality")
    county: ShortCounty = Field(description="County information the municipality belongs to")

    class Config:
        from_attributes = True


class Municipality(ShortMunicipality):
    area_ha: float = Field(description="Area of the municipality in hectares")
    created_at: datetime.date = Field(description="Date of creation of the municipality")

    class Config:
        from_attributes = True


class MunicipalityWithGeometry(Municipality):
    geometry: Geometry = Field(description="Geometry information of the municipality")


class Eldership(BaseModel):
    code: int = Field(description="Unique code of the eldership")
    name: str = Field(description="Name of the eldership")
    feature_id: int = Field(description="Feature ID of the eldership")
    area_ha: float = Field(description="Area of the eldership in hectares")
    municipality: ShortMunicipality = Field(description="Municipality information the eldership belongs to")
    created_at: datetime.date = Field(description="Date of creation of the eldership")

    class Config:
        from_attributes = True


class EldershipWithGeometry(Eldership):
    geometry: Geometry = Field(description="Geometry information of the eldership")


class FlatResidentialArea(BaseModel):
    code: int = Field(description="Unique code of the residential area")
    feature_id: int = Field(description="Feature ID of the residential area")
    name: str = Field(description="Name of the residential area")

    class Config:
        from_attributes = True


class ShortResidentialArea(FlatResidentialArea):
    municipality: ShortMunicipality = Field(description="Municipality information the residential area belongs to")


class ResidentialArea(ShortResidentialArea):
    area_ha: float = Field(description="Area of the residential area in hectares")
    created_at: datetime.date = Field(description="Date of creation of the residential area")


class ResidentialAreaWithGeometry(ResidentialArea):
    geometry: Geometry = Field(description="Geometry information of the residential area")


class FlatStreet(BaseModel):
    code: int = Field(description="Unique code of the street")
    feature_id: int = Field(description="Feature ID of the street")
    name: str = Field(description="Name of the street")
    full_name: str = Field(description="The full name of the street, including its type")

    class Config:
        from_attributes = True


class Street(FlatStreet):
    length_m: float = Field(description="The total length of the street in meters")
    created_at: datetime.date = Field(description="Date of creation of the street")
    residential_area: ShortResidentialArea = Field(description="Residential area information the street belongs to")

    class Config:
        from_attributes = True


class StreetWithGeometry(Street):
    geometry: Geometry = Field(description="Line geometry information of the street")


class ShortAddress(BaseModel):
    code: int = Field(description="Unique code of the address")
    feature_id: int = Field(description="Feature ID of the address")
    plot_or_building_number: str = Field(description="Plot or building number of the address")
    building_block_number: Optional[str] = Field(description="Plot or building number of the address", min_length=1)
    postal_code: str = Field(description="Postal code of the address")

    street: Optional[FlatStreet] = Field(description="Street information the address belongs to")
    residential_area: Optional[FlatResidentialArea] = Field(
        description="Residential area information the address belongs to",
    )
    municipality: ShortMunicipality = Field(description="Municipality information the address belongs to")


class Address(ShortAddress):
    geometry: Geometry = Field(description="Point geometry of the address")


class Room(BaseModel):
    code: int = Field(description="Unique code of the room")
    room_number: str = Field(description="Room number in the building or building section")
    created_at: datetime.date = Field(description="Date of creation of the room address")
    geometry: Geometry = Field(description="Point geometry of the address")
    address: ShortAddress = Field(description="Address of the room")


class ShortParcel(BaseModel):
    unique_number: int = Field(description="Unique number of the parcel")
    cadastral_number: str = Field(description="Cadastral number of the parcel")
    updated_at: datetime.date = Field(description="Date of update of the parcel")
    area_ha: float = Field(description="Area of the parcel in hectares")

    municipality: ShortMunicipality = Field(description="Municipality information the parcel belongs to")

class Parcel(ShortParcel):
    geometry: Geometry = Field(description="Polygon geometry of the parcel")


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    healthy: bool = Field(description="Health status of the service")


class HTTPExceptionResponse(BaseModel):
    detail: str = Field(description="Detailed error message")

    class Config:
        json_schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }


class StringFilter(BaseModel):
    contains: Optional[str] = Field(
        default=None,
        description="Filter by containing a string (case insensitive)",
        examples=[
            ""
        ],
    )

    exact: Optional[str] = Field(
        default=None,
        description="Filter by exact string (case insensitive)",
        examples=[
            ""
        ],
    )

    starts: Optional[str] = Field(
        default=None,
        description="Filter by starting with a string (case insensitive)",
        examples=[
            ""
        ],
    )


class GeometryFilterMethod(enum.StrEnum):
    intersects = 'intersects'
    contains = 'contains'


class GeometryFilter(BaseModel):
    method: GeometryFilterMethod = Field(
        default=GeometryFilterMethod.intersects,
        description="Defines method used for filtering geometries:\n"
                    "- **`intersects`**: filter geometries that intersects any portion of space with the specified "
                    "geometry.\n"
                    "- **`contains`**: filter geometries that are completely within the specified geometry."
    )
    ewkb: Optional[str] = Field(
        default=None,
        description="Extended Well-Known Binary (EWKB) represented as a hex string for geometry filtering",
        examples=[
            r"0103000020E6100000010000000500000045F6419605473940B1DD3D40F7574B4045F641960547394061E124CD1F57"
            r"4B40719010E50B4A394061E124CD1F574B40719010E50B4A3940B1DD3D40F7574B4045F6419605473940B1DD3D40F7574B40"
        ],
    )

    ewkt: Optional[str] = Field(
        default=None,
        description="Extended Well-Known Text (EWKT) for geometry filtering",
        examples=[
            "SRID=4326;POLYGON((25.277429 54.687233, 25.277429 54.680658, 25.289244 54.680658, 25.289244 54.687233, "
            "25.277429 54.687233))"
        ],
    )

    geojson: Optional[str] = Field(
        default=None,
        description="GeoJson for geometry filtering",
        examples=[
            r'{"crs":{"type":"name","properties":{"name":"EPSG:4326"}},"type":"Polygon","coordinates":[[[25.277429,'
            r'54.687233],[25.277429,54.680658],[25.289244,54.680658],[25.289244,54.687233],[25.277429,54.687233]]]}'
        ],
    )


class GeneralBoundariesFilter(BaseModel):
    codes: Optional[List[int]] = Field(
        default=None,
        description="Filter by codes",
        examples=[
            []
        ],
    )

    feature_ids: Optional[List[int]] = Field(
        default=None,
        description="Filter by feature IDs",
        examples=[
            []
        ],
    )

    name: Optional[StringFilter] = Field(
        default=None,
        description="Filter by name"
    )


class AddressesFilter(BaseModel):
    codes: Optional[List[int]] = Field(
        default=None,
        description="Filter by codes",
        examples=[
            []
        ],
    )

    feature_ids: Optional[List[int]] = Field(
        default=None,
        description="Filter by feature IDs",
        examples=[
            []
        ],
    )

    plot_or_building_number: Optional[StringFilter] = Field(
        default=None,
        description="Filter by plot or building number"
    )
    building_block_number: Optional[StringFilter] = Field(
        default=None,
        description="Filter by building block number"
    )
    postal_code: Optional[StringFilter] = Field(
        default=None,
        description="Filter by postal code"
    )


class RoomsFilter(BaseModel):
    codes: Optional[List[int]] = Field(
        default=None,
        description="Filter by codes",
        examples=[
            []
        ],
    )
    room_number: Optional[StringFilter] = Field(
        default=None,
        description="Filter by room number",
    )


class ParcelsFilter(BaseModel):
    unique_numbers: Optional[List[int]] = Field(
        default=None,
        description="Filter by unique numbers",
        examples=[
            []
        ],
    )

    cadastral_number: Optional[StringFilter] = Field(
        default=None,
        description="Filter by cadastral number"
    )


class StreetsFilter(GeneralBoundariesFilter):
    full_name: Optional[StringFilter] = Field(
        default=None,
        description="Filter by full name"
    )


class ResidentialAreasFilter(GeneralBoundariesFilter):
    pass


class EldershipsFilter(GeneralBoundariesFilter):
    pass


class MunicipalitiesFilter(GeneralBoundariesFilter):
    pass


class CountiesFilter(GeneralBoundariesFilter):
    pass


class BaseSearchFilterRequest(BaseModel):
    geometry: Optional[GeometryFilter] = Field(
        default=None,
        description="Filter by geometry",
    )


class CountiesSearchFilterRequest(BaseSearchFilterRequest):
    counties: Optional[CountiesFilter] = Field(
        default=None,
        description="Filter by counties",
    )


class MunicipalitiesSearchFilterRequest(CountiesSearchFilterRequest):
    municipalities: Optional[MunicipalitiesFilter] = Field(
        default=None,
        description="Filter by municipalities",
    )


class ResidentialAreasSearchFilterRequest(MunicipalitiesSearchFilterRequest):
    residential_areas: Optional[ResidentialAreasFilter] = Field(
        default=None,
        description="Filter by residential areas",
    )


class EldershipsSearchFilterRequest(MunicipalitiesSearchFilterRequest):
    elderships: Optional[EldershipsFilter] = Field(
        default=None,
        description="Filter by elderships",
    )


class StreetsSearchFilterRequest(ResidentialAreasSearchFilterRequest):
    streets: Optional[StreetsFilter] = Field(
        default=None,
        description="Filter by streets",
    )


class AddressesSearchFilterRequest(StreetsSearchFilterRequest):
    addresses: Optional[AddressesFilter] = Field(
        default=None,
        description="Filter by addresses",
    )


class RoomsSearchFilterRequest(AddressesSearchFilterRequest):
    rooms: Optional[RoomsFilter] = Field(
        default=None,
        description="Filter by rooms",
    )


class ParcelSearchFilterRequest(MunicipalitiesSearchFilterRequest):
    parcels: Optional[ParcelsFilter] = Field(
        default=None,
        description="Filter by parcels",
    )


class BaseSearchRequest(abc.ABC, BaseModel):
    filters: List[BaseSearchFilterRequest]


class CountiesSearchRequest(BaseSearchRequest):
    filters: List[CountiesSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching counties, combined using OR logic.",
    )


class MunicipalitiesSearchRequest(BaseSearchRequest):
    filters: List[MunicipalitiesSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching municipalities, combined using OR logic.",
    )


class ResidentialAreasSearchRequest(BaseSearchRequest):
    filters: List[ResidentialAreasSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching residential areas, combined using OR logic.",
    )


class EldershipsSearchRequest(BaseSearchRequest):
    filters: List[EldershipsSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching elderships, combined using OR logic.",
    )


class StreetsSearchRequest(BaseSearchRequest):
    filters: List[StreetsSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching streets, combined using OR logic.",
    )


class AddressesSearchRequest(BaseSearchRequest):
    filters: List[AddressesSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching addresses, combined using OR logic.",
    )


class RoomsSearchRequest(BaseSearchRequest):
    filters: List[RoomsSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching rooms, combined using OR logic.",
    )


class ParcelsSearchRequest(BaseSearchRequest):
    filters: List[ParcelSearchFilterRequest] = Field(
        default=[],
        description="A list of filters to apply for searching parcels, combined using OR logic.",
    )
