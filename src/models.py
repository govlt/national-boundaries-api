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
