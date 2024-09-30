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


class RoomsFilter(AddressesFilter):

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


class PurposeTypesFilter(BaseFilter):

    def apply(
            self,
            search_filter: schemas.PurposeTypesSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if purpose_filter := search_filter.purposes:
            yield from self._apply_purposes_filters(purpose_filter)

    @staticmethod
    def _apply_purposes_filters(purpose_filter: schemas.PurposeTypeFilter) -> Iterator[ColumnExpressionArgument]:

        purpose_ids = purpose_filter.purpose_ids
        if purpose_ids and len(purpose_ids) > 0:
            yield models.PurposeTypes.purpose_id.in_(purpose_ids)
        
        if purpose_filter.purpose_group:
            yield models.PurposeTypes.purpose_group == purpose_filter.purpose_group

        if purpose_filter.name:
            yield from _filter_by_string_field(string_filter=purpose_filter.name,
                                               string_field=models.PurposeTypes.name)

        if purpose_filter.full_name:
            yield from _filter_by_string_field(string_filter=purpose_filter.full_name,
                                               string_field=models.PurposeTypes.full_name)

        if purpose_filter.full_name_en:
            yield from _filter_by_string_field(string_filter=purpose_filter.full_name_en,
                                               string_field=models.PurposeTypes.full_name_en)

class StatusTypesFilter(BaseFilter):

    def apply(
            self,
            search_filter: schemas.StatusTypesSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if status_filter := search_filter.statuses:
            yield from self._apply_status_filters(status_filter)

    @staticmethod
    def _apply_status_filters(status_filter: schemas.StatusTypesFilter) -> Iterator[ColumnExpressionArgument]:

        status_ids = status_filter.status_ids
        if status_ids and len(status_ids) > 0:
            yield models.StatusTypes.status_id.in_(status_ids)
        
        if status_filter.name:
            yield from _filter_by_string_field(string_filter=status_filter.name,
                                               string_field=models.StatusTypes.name)

        if status_filter.name_en:
            yield from _filter_by_string_field(string_filter=status_filter.name_en,
                                               string_field=models.StatusTypes.name_en)

        if status_filter.full_name:
            yield from _filter_by_string_field(string_filter=status_filter.full_name,
                                               string_field=models.StatusTypes.full_name)

        if status_filter.full_name_en:
            yield from _filter_by_string_field(string_filter=status_filter.full_name_en,
                                               string_field=models.StatusTypes.full_name_en)


class ParcelsFilter(MunicipalitiesFilter, PurposeTypesFilter, StatusTypesFilter):

    def apply(
            self,
            search_filter: schemas.ParcelSearchFilterRequest,
            db: Session
    ) -> Iterator[ColumnExpressionArgument]:
        yield from super().apply(search_filter, db)

        if parcel_filter := search_filter.parcels:
            yield from self._apply_parcels_filters(parcel_filter)

    @staticmethod
    def _apply_parcels_filters(parcel_filter: schemas.ParcelsFilter) -> Iterator[ColumnExpressionArgument]:
        if parcel_filter.cadastral_number:
            yield from _filter_by_string_field(string_filter=parcel_filter.cadastral_number,
                                               string_field=models.Parcels.cadastral_number)

        unique_numbers = parcel_filter.unique_numbers
        if unique_numbers and len(unique_numbers) > 0:
            yield models.Parcels.unique_number.in_(unique_numbers)

        if parcel_filter.area_ha:
            yield from _filter_by_number_field(number_filter=parcel_filter.area_ha,
                                               number_field=models.Parcels.area_ha)

    class Meta:
        geom_field = models.Parcels.geom


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


def _filter_by_number_field(
        number_filter: schemas.NumberFilter,
        number_field: InstrumentedAttribute
) -> Iterator[ColumnExpressionArgument]:
    if number_filter.eq:
        yield number_field == number_filter.eq
    else:
        if number_filter.lt:
            yield number_field < number_filter.lt
        elif number_filter.lte:
            yield number_field <= number_filter.lte
        
        if number_filter.gt:
            yield number_field > number_filter.gt
        elif number_filter.gte:
            yield number_field >= number_filter.gte


class InvalidFilterGeometry(Exception):
    def __init__(self, message: str, field: str, value: str):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)
