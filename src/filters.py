from abc import ABC
from typing import Iterator

from geoalchemy2.functions import ST_Intersects, ST_Transform, ST_GeomFromEWKT, ST_Contains, ST_IsValid
from sqlalchemy.orm import Session, InstrumentedAttribute
from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlalchemy.sql.functions import GenericFunction, func
from sqlean import OperationalError

from src import database, schemas, models


class BaseFilter(ABC):
    def apply(self, search_filter: schemas.BaseSearchFilterRequest, db: Session) -> Iterator[ColumnExpressionArgument]:
        if geometry_filter := search_filter.geometry:
            yield from self._apply_geometry_filter(
                geometry_filter=geometry_filter,
                db=db,
            )

    @staticmethod
    def _apply_general_boundaries_filter(
            general_boundaries_filter: schemas.GeneralBoundariesFilter,
            model_class: type[models.BaseBoundaries],
    ) -> Iterator[ColumnExpressionArgument]:
        if hasattr(model_class, 'name') and general_boundaries_filter.name:
            yield from _filter_by_string_field(string_filter=general_boundaries_filter.name,
                                               string_field=getattr(model_class, 'name'))

        feature_ids = general_boundaries_filter.feature_ids
        if feature_ids and len(general_boundaries_filter.feature_ids) > 0:
            yield getattr(model_class, 'feature_id').in_(feature_ids)

        codes = general_boundaries_filter.codes
        if codes and len(codes) > 0:
            yield getattr(model_class, 'code').in_(codes)

    @staticmethod
    def _filter_by_geometry(
            db: Session,
            geom_value: str,
            field: str,
            geom_field: InstrumentedAttribute,
            filter_func_type: type[GenericFunction],
            geom_from_func_type: type[GenericFunction],
    ) -> Iterator[ColumnExpressionArgument]:
        geom = ST_Transform(geom_from_func_type(geom_value), 3346)
        if not _is_valid_geometry(db, geom):
            raise InvalidFilterGeometry(message="Invalid geometry", field=field, value=geom_value)

        yield filter_func_type(geom, geom_field)

    def _apply_geometry_filter(
            self,
            geometry_filter: schemas.GeometryFilter,
            db: Session,
    ) -> Iterator[ColumnExpressionArgument]:
        filter_func_type = _get_filter_func(geometry_filter.method)
        geom_field = self.Meta.geom_field
        if geom_field is None:
            raise ValueError('geom_field in meta is not defined')

        if ewkb := geometry_filter.ewkb:
            yield from self._filter_by_geometry(
                db=db,
                field="ewkb",
                geom_value=ewkb,
                filter_func_type=filter_func_type,
                geom_from_func_type=database.GeomFromEWKB,
                geom_field=geom_field,
            )

        if ewkt := geometry_filter.ewkt:
            yield from self._filter_by_geometry(
                db=db,
                field="ewkt",
                geom_value=ewkt,
                filter_func_type=filter_func_type,
                geom_from_func_type=ST_GeomFromEWKT,
                geom_field=geom_field,
            )

        if geojson := geometry_filter.geojson:
            yield from self._filter_by_geometry(
                db=db,
                field="geojson",
                geom_value=geojson,
                filter_func_type=filter_func_type,
                geom_from_func_type=database.GeomFromGeoJSON,
                geom_field=geom_field,
            )


class CountiesFilter(BaseFilter):
    def apply(
            self,
            search_filter: schemas.CountiesSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if counties_filter := search_filter.counties:
            yield from self._apply_general_boundaries_filter(
                general_boundaries_filter=counties_filter,
                model_class=models.Counties
            )

    class Meta:
        geom_field = models.Counties.geom


class MunicipalitiesFilter(CountiesFilter):

    def apply(
            self,
            search_filter: schemas.MunicipalitiesSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if municipalities_filter := search_filter.municipalities:
            yield from self._apply_general_boundaries_filter(
                general_boundaries_filter=municipalities_filter,
                model_class=models.Municipalities
            )

    class Meta:
        geom_field = models.Municipalities.geom


class EldershipsFilter(MunicipalitiesFilter):

    def apply(
            self,
            search_filter: schemas.EldershipsSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)
        if elderships_filter := search_filter.elderships:
            yield from self._apply_general_boundaries_filter(
                general_boundaries_filter=elderships_filter,
                model_class=models.Elderships
            )

    class Meta:
        geom_field = models.Elderships.geom


class ResidentialAreasFilter(MunicipalitiesFilter):
    def apply(
            self,
            search_filter: schemas.ResidentialAreasSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)
        if residential_areas_filter := search_filter.residential_areas:
            yield from self._apply_general_boundaries_filter(
                general_boundaries_filter=residential_areas_filter,
                model_class=models.ResidentialAreas
            )

    class Meta:
        geom_field = models.ResidentialAreas.geom


class StreetsFilter(ResidentialAreasFilter):
    def apply(
            self,
            search_filter: schemas.StreetsSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)
        if streets_filter := search_filter.streets:
            yield from self._apply_general_boundaries_filter(
                general_boundaries_filter=streets_filter,
                model_class=models.Streets
            )

            if streets_filter.full_name:
                yield from _filter_by_string_field(string_filter=streets_filter.full_name,
                                                   string_field=models.Streets.full_name)

    class Meta:
        geom_field = models.Streets.geom


class AddressesFilter(StreetsFilter):

    def apply(
            self,
            search_filter: schemas.AddressesSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if address_filter := search_filter.addresses:
            yield from self._apply_streets_filters(address_filter)

    @staticmethod
    def _apply_streets_filters(address_filter: schemas.AddressesFilter) -> Iterator[ColumnExpressionArgument]:
        if address_filter.building_block_number:
            yield from _filter_by_string_field(string_filter=address_filter.building_block_number,
                                               string_field=models.Addresses.building_block_number)

        if address_filter.plot_or_building_number:
            yield from _filter_by_string_field(string_filter=address_filter.plot_or_building_number,
                                               string_field=models.Addresses.plot_or_building_number)
        if address_filter.postal_code:
            yield from _filter_by_string_field(string_filter=address_filter.postal_code,
                                               string_field=models.Addresses.postal_code)

        feature_ids = address_filter.feature_ids
        if feature_ids and len(address_filter.feature_ids) > 0:
            yield models.Addresses.feature_id.in_(feature_ids)

        codes = address_filter.codes
        if codes and len(codes) > 0:
            yield models.Addresses.code.in_(codes)

    class Meta:
        geom_field = models.Addresses.geom


class RoomsFilter(StreetsFilter):

    def apply(self, search_filter: schemas.RoomsSearchFilterRequest, db: Session) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if room_filter := search_filter.rooms:
            yield from self._apply_rooms_filters(room_filter)

    @staticmethod
    def _apply_rooms_filters(rooms_filter: schemas.RoomsFilter) -> Iterator[ColumnExpressionArgument]:
        if rooms_filter.room_number:
            yield from _filter_by_string_field(string_filter=rooms_filter.room_number,
                                               string_field=models.Rooms.room_number)
        codes = rooms_filter.codes
        if codes and len(codes) > 0:
            yield models.Rooms.code.in_(codes)

    class Meta:
        geom_field = models.Addresses.geom


def _is_valid_geometry(db: Session, geom: GenericFunction) -> bool:
    try:
        return db.execute(ST_IsValid(geom)).scalar() == 1
    except OperationalError:
        return False


def _get_filter_func(filter_method: schemas.GeometryFilterMethod) -> type[GenericFunction]:
    match filter_method:
        case schemas.GeometryFilterMethod.intersects:
            return ST_Intersects
        case schemas.GeometryFilterMethod.contains:
            return ST_Contains
        case _:
            raise ValueError(f"Unknown geometry filter method: {filter_method}")


def _filter_by_string_field(
        string_filter: schemas.StringFilter,
        string_field: InstrumentedAttribute
) -> Iterator[ColumnExpressionArgument]:
    if string_filter.exact:
        yield func.lower(string_field) == string_filter.exact.lower()
    elif string_filter.starts:
        yield string_field.istartswith(string_filter.starts)
    elif string_filter.contains:
        yield string_field.icontains(string_filter.contains)


class InvalidFilterGeometry(Exception):
    def __init__(self, message: str, field: str, value: str):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
