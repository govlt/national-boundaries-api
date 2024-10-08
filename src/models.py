from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Double, ForeignKey, Date
from sqlalchemy.orm import relationship

from src.database import Base


class BaseBoundaries(Base):
    __abstract__ = True

    feature_id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    geom = Column(
        Geometry(srid=3346, nullable=False), nullable=False
    )


class Counties(BaseBoundaries):
    __tablename__ = "counties"
    area_ha = Column(Double, nullable=False)
    created_at = Column(Date, nullable=False)

    municipalities = relationship("Municipalities", back_populates="county")


class Municipalities(BaseBoundaries):
    __tablename__ = "municipalities"

    area_ha = Column(Double, nullable=False)
    created_at = Column(Date, nullable=False)

    county_code = Column(Integer, ForeignKey("counties.code"))
    county = relationship("Counties", back_populates="municipalities")

    elderships = relationship("Elderships", back_populates="municipality")
    residential_areas = relationship("ResidentialAreas", back_populates="municipality")
    addresses = relationship("Addresses", back_populates="municipality")
    parcels = relationship("Parcels", back_populates="municipality")


class Elderships(BaseBoundaries):
    __tablename__ = "elderships"

    area_ha = Column(Double, nullable=False)
    created_at = Column(Date, nullable=False)

    municipality_code = Column(Integer, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="elderships")


class ResidentialAreas(BaseBoundaries):
    __tablename__ = "residential_areas"

    area_ha = Column(Double, nullable=False)
    created_at = Column(Date, nullable=False)
    municipality_code = Column(Integer, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="residential_areas")
    streets = relationship("Streets", back_populates="residential_area")
    addresses = relationship("Addresses", back_populates="residential_area")


class Streets(BaseBoundaries):
    __tablename__ = "streets"

    length_m = Column(Double, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)
    residential_area_code = Column(Integer, ForeignKey("residential_areas.code"))
    residential_area = relationship("ResidentialAreas", back_populates="streets")
    addresses = relationship("Addresses", back_populates="street")


class Addresses(Base):
    __tablename__ = "addresses"

    feature_id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False, index=True)

    plot_or_building_number = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    building_block_number = Column(String, nullable=False)
    geom = Column(
        Geometry(srid=3346, nullable=False), nullable=False
    )
    created_at = Column(Date, nullable=False)

    municipality_code = Column(Integer, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="addresses")

    residential_area_code = Column(Integer, ForeignKey("residential_areas.code"), nullable=True)
    residential_area = relationship("ResidentialAreas", back_populates="addresses")

    street_code = Column(Integer, ForeignKey("streets.code"), nullable=True)
    street = relationship("Streets", back_populates="addresses")

    rooms = relationship("Rooms", back_populates="address")


class Rooms(Base):
    __tablename__ = "rooms"

    code = Column(Integer, primary_key=True)
    room_number = Column(String, nullable=False)
    created_at = Column(Date, nullable=False)

    address_code = Column(Integer, ForeignKey("addresses.code"))
    address = relationship("Addresses", back_populates="rooms")


class StatusTypes(Base):
    __tablename__ = "status_types"

    status_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    name_en = Column(String, nullable=False)
    full_name_en = Column(String, nullable=False)

    updated_at = Column(Date, nullable=False)

    parcels = relationship("Parcels", back_populates="status")


class PurposeGroups(Base):
    __tablename__ = "purpose_groups"

    group_id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    updated_at = Column(Date, nullable=False)

    purpose_types = relationship("PurposeTypes", back_populates="purpose_group")


class PurposeTypes(Base):
    __tablename__ = "purpose_types"

    purpose_id = Column(Integer, primary_key=True)

    purpose_group_id = Column(Integer, ForeignKey("purpose_groups.group_id"), nullable=True)
    purpose_group = relationship("PurposeGroups", back_populates="purpose_types")

    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    name_en = Column(String, nullable=False)
    full_name_en = Column(String, nullable=False)

    updated_at = Column(Date, nullable=False)

    parcels = relationship("Parcels", back_populates="purpose")


class Parcels(Base):
    __tablename__ = "parcels"

    ogc_fid = Column(Integer, primary_key=True)
    unique_number = Column(Integer, nullable=False, index=True)
    cadastral_number = Column(String, nullable=False, index=True)

    status_id = Column(Integer, ForeignKey("status_types.status_id"), nullable=True)
    purpose_id = Column(Integer, ForeignKey("purpose_types.purpose_id"), nullable=False)
    purpose = relationship("PurposeTypes", back_populates="parcels")
    status = relationship("StatusTypes", back_populates="parcels")

    updated_at = Column(Date, nullable=False)
    area_ha = Column(Double, nullable=False)

    municipality_code = Column(Integer, ForeignKey("municipalities.code"))
    municipality = relationship("Municipalities", back_populates="parcels")

    geom = Column(
        Geometry(srid=3346, nullable=False), nullable=False
    )
