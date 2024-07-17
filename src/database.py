from typing import Optional

import geoalchemy2
import sqlean
from geoalchemy2 import load_spatialite, Geometry, WKTElement
from geoalchemy2.functions import GenericFunction
from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import declarative_base, sessionmaker, Session


def _connect():
    sqlean.extensions.enable("unicode")
    conn = sqlean.connect("file:boundaries.sqlite?immutable=1", uri=True, check_same_thread=False)
    load_spatialite(conn)
    return conn


engine = create_engine(
    "sqlite://",
    creator=_connect,
    echo=True,
    echo_pool=True,
    poolclass=NullPool,
)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    db = session()
    try:
        yield db
    finally:
        db.close()


class GeomFromGeoJSON(GenericFunction):
    """
    Returns the GeoJSON [Geographic JavaScript Object Notation] representation

    see https://www.gaia-gis.it/gaia-sins/spatialite-sql-5.1.0.html

    Return type: :class:`geoalchemy2.types.Geometry`.
    """

    type = geoalchemy2.types.Geometry()
    inherit_cache = True


class GeomFromEWKB(GenericFunction):
    type = geoalchemy2.types.Geometry()
    inherit_cache = True


class EWKTGeometry(Geometry):
    # We need to override constructor only to set extended to True
    def __init__(self, geometry_type: Optional[str] = "GEOMETRY", srid=-1, dimension=2, spatial_index=True,
                 use_N_D_index=False, use_typmod: Optional[bool] = None, from_text: Optional[str] = None,
                 name: Optional[str] = None, nullable=True, _spatial_index_reflected=None) -> None:
        super().__init__(geometry_type, srid, dimension, spatial_index, use_N_D_index, use_typmod, from_text, name,
                         nullable, _spatial_index_reflected)
        self.extended = True

    name = "geometry"
    from_text = 'ST_GeomFromEWKT'
    as_binary = 'AsEWKT'
    ElementType = WKTElement

    cache_ok = False
