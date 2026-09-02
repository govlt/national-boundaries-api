import os

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


# Logging every statement and pool event is expensive under load, so it is opt-in.
_echo_sql = os.environ.get("SQL_ECHO", "").lower() in ("1", "true", "yes")

engine = create_engine(
    "sqlite://",
    creator=_connect,
    echo=_echo_sql,
    echo_pool=_echo_sql,
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
    name = "geometry"
    from_text = 'ST_GeomFromEWKT'
    as_binary = 'AsEWKT'
    ElementType = WKTElement

    cache_ok = False

    # We need to override the constructor only to set extended to True. Forwarding *args/**kwargs
    # keeps this working across GeoAlchemy2 releases instead of restating its signature.
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extended = True
