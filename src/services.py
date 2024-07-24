import abc
from typing import Optional, Type

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Transform
from sqlalchemy import select, Select, func, text, Row, Label, or_, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.sql import operators

from src import filters, schemas, models, database

# FastAPI has very poor support for nested types
# Build jsonb in order to avoid N+1 and deserialization problems
_county_object = func.json_object(
    text("'code', counties.code"),
    text("'name', counties.name"),
    text("'feature_id', counties.feature_id"),
    type_=JSONB,
).label("county")

_municipality_object = func.json_object(
    text("'code', municipalities.code"),
    text("'name', municipalities.name"),
    text("'feature_id', municipalities.feature_id"),
    "county", _county_object,
    type_=JSONB,
).label("municipality")

_flat_residential_area_object = func.json_object(
    text("'code', residential_areas.code"),
    text("'name', residential_areas.name"),
    text("'feature_id', residential_areas.feature_id"),
    type_=JSONB,
).label("residential_area")

_residential_area_object = func.json_object(
    text("'code', residential_areas.code"),
    text("'name', residential_areas.name"),
    text("'feature_id', residential_areas.feature_id"),
    "municipality", _municipality_object,
    type_=JSONB,
).label("residential_area")

_flat_street_object = func.json_object(
    text("'code', streets.code"),
    text("'name', streets.name"),
    text("'full_name', streets.full_name"),
    text("'feature_id', streets.feature_id"),
    type_=JSONB,
).label("street")

_address_short_object = func.json_object(
    text("'code', addresses.code"),
    text("'feature_id', addresses.feature_id"),
    text("'plot_or_building_number', addresses.plot_or_building_number"),
    text("'building_block_number', addresses.building_block_number"),
    text("'postal_code', addresses.postal_code"),
    "residential_area", _flat_residential_area_object,
    "municipality", _municipality_object,
    "street", _flat_street_object,
    type_=JSONB,
).label("address")


class BaseBoundariesService(abc.ABC):
    model_class: Type[models.BaseBoundaries]

    @abc.abstractmethod
    def _get_select_query(self, srid: Optional[int],
                          geometry_output_format: Optional[schemas.GeometryOutputFormat]) -> Select:
        pass

    @abc.abstractmethod
    def _filter_by_code(self, query: Select, code: int) -> Select:
        pass

    @staticmethod
    def _get_geometry_output_type(geometry_output_format: schemas.GeometryOutputFormat):
        match geometry_output_format:
            case schemas.GeometryOutputFormat.ewkt:
                return database.EWKTGeometry
            case schemas.GeometryOutputFormat.ewkb:
                return Geometry()
            case _:
                raise ValueError(f"Unable to map geometry output format {geometry_output_format}")

    @staticmethod
    def _get_geometry_field(
            field: InstrumentedAttribute,
            srid: int,
            geometry_output_format: schemas.GeometryOutputFormat
    ) -> Label:
        geometry_output_type = BaseBoundariesService._get_geometry_output_type(geometry_output_format)

        return ST_Transform(field, srid, type_=geometry_output_type).label("geometry")

    def search(
            self,
            db: Session,
            sort_by_field: str,
            sort_order: schemas.SearchSortOrder,
            request: schemas.BaseSearchRequest,
            boundaries_filter: filters.BaseFilter,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat]
    ) -> Page:
        query = self._get_select_query(srid=srid, geometry_output_format=geometry_output_format)

        query_search_filters = []
        for search_filter in request.filters:
            query_and_filters = list(boundaries_filter.apply(search_filter, db))

            if len(query_and_filters) > 0:
                query_search_filters.append(and_(*query_and_filters))

        query = query.where(or_(*query_search_filters))

        sort_attr = getattr(self.model_class, sort_by_field)
        sort_by = operators.collate(sort_attr, "NOCASE")

        if sort_order == schemas.SearchSortOrder.desc:
            sort_by = sort_by.desc()

        # Do natural sort on room numbers and plot_or_building_number e.g. 1, 1A, 2, 101, 101A, 102
        if sort_by_field == 'room_number' or sort_by_field == 'plot_or_building_number':
            if sort_order == schemas.SearchSortOrder.asc:
                query = query.order_by((sort_attr * 1).asc())
            else:
                query = query.order_by((sort_attr * 1).desc())

        query = query.order_by(sort_by, self.model_class.code.asc())
        return paginate(db, query)

    def get_by_code(
            self,
            db: Session,
            code: int,
            geometry_output_format: Optional[schemas.GeometryOutputFormat] = None,
            srid: Optional[int] = None,
    ) -> Row | None:
        query = self._get_select_query(srid=srid, geometry_output_format=geometry_output_format)
        query = self._filter_by_code(code=code, query=query)

        return db.execute(query).first()


class CountiesService(BaseBoundariesService):
    model_class = models.Counties

    def _get_select_query(
            self,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
                      models.Counties.code,
                      models.Counties.feature_id,
                      models.Counties.name,
                      models.Counties.area_ha,
                      models.Counties.area_ha,
                      models.Counties.created_at,
                  ] + ([self._get_geometry_field(models.Counties.geom, srid,
                                                 geometry_output_format)] if srid and geometry_output_format else [])

        return select(*columns).select_from(models.Counties)

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.Counties.code == code)


class MunicipalitiesService(BaseBoundariesService):
    model_class = models.Municipalities

    def _get_select_query(
            self,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
                      models.Municipalities.code,
                      models.Municipalities.feature_id,
                      models.Municipalities.name,
                      models.Municipalities.area_ha,
                      models.Municipalities.created_at,
                      _county_object,
                  ] + ([self._get_geometry_field(models.Municipalities.geom, srid)] if srid else [])

        return select(*columns).outerjoin_from(
            models.Municipalities, models.Municipalities.county
        )

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.Municipalities.code == code)


class EldershipsService(BaseBoundariesService):
    model_class = models.Elderships

    def _get_select_query(
            self,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
                      models.Elderships.code,
                      models.Elderships.feature_id,
                      models.Elderships.name,
                      models.Elderships.area_ha,
                      models.Elderships.created_at,
                      _municipality_object,
                  ] + ([self._get_geometry_field(models.Elderships.geom, srid)] if srid else [])

        return select(*columns).outerjoin_from(
            models.Elderships, models.Elderships.municipality
        ).outerjoin(models.Municipalities.county)

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.Elderships.code == code)


class ResidentialAreasService(BaseBoundariesService):
    model_class = models.ResidentialAreas

    def _get_select_query(
            self, srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
                      models.ResidentialAreas.code,
                      models.ResidentialAreas.feature_id,
                      models.ResidentialAreas.name,
                      models.ResidentialAreas.area_ha,
                      models.ResidentialAreas.created_at,
                      _municipality_object,
                  ] + ([self._get_geometry_field(models.ResidentialAreas.geom, srid)] if srid else [])

        return select(*columns).outerjoin_from(
            models.ResidentialAreas, models.ResidentialAreas.municipality
        ).outerjoin(models.Municipalities.county)

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.ResidentialAreas.code == code)


class StreetsService(BaseBoundariesService):
    model_class = models.Streets

    def _get_select_query(
            self,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
                      models.Streets.code,
                      models.Streets.feature_id,
                      models.Streets.name,
                      models.Streets.length_m,
                      models.Streets.full_name,
                      models.Streets.created_at,
                      _residential_area_object,
                  ] + ([self._get_geometry_field(models.Streets.geom, srid)] if srid else [])

        return select(*columns).outerjoin_from(
            models.Streets, models.Streets.residential_area
        ).outerjoin(models.ResidentialAreas.municipality).outerjoin(models.Municipalities.county)

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.Streets.code == code)


class AddressesService(BaseBoundariesService):
    model_class = models.Addresses

    def _get_select_query(
            self,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
            models.Addresses.feature_id,
            models.Addresses.code,
            models.Addresses.plot_or_building_number,
            models.Addresses.building_block_number,
            models.Addresses.postal_code,
            models.Addresses.created_at,
            _flat_residential_area_object,
            _municipality_object,
            _flat_street_object,
            self._get_geometry_field(models.Addresses.geom, srid, geometry_output_format)
        ]

        return select(*columns).select_from(models.Addresses) \
            .outerjoin(models.Addresses.municipality) \
            .outerjoin(models.Municipalities.county) \
            .outerjoin(models.Addresses.street) \
            .outerjoin(models.Addresses.residential_area)

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.Addresses.code == code)


class RoomsService(BaseBoundariesService):
    model_class = models.Rooms

    def _get_select_query(
            self,
            srid: Optional[int],
            geometry_output_format: Optional[schemas.GeometryOutputFormat],
    ) -> Select:
        columns = [
                      models.Rooms.code,
                      models.Rooms.room_number,
                      models.Rooms.created_at,
                      _address_short_object,
                  ] + ([self._get_geometry_field(models.Addresses.geom, srid,
                                                 geometry_output_format)] if srid and geometry_output_format else [])

        return select(*columns).select_from(models.Rooms) \
            .outerjoin(models.Rooms.address) \
            .outerjoin(models.Addresses.municipality) \
            .outerjoin(models.Municipalities.county) \
            .outerjoin(models.Addresses.street) \
            .outerjoin(models.Addresses.residential_area)

    def _filter_by_code(self, query: Select, code: int) -> Select:
        return query.filter(models.Rooms.code == code)
