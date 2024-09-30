from typing import Dict

from fastapi import Query
from fastapi.openapi.models import Example

from src import schemas

query_srid: Query = Query(
    3346,
    openapi_examples={
        "example_wgs": {
            "summary": "WGS 84 (EPSG:4326)",
            "description": "The World Geodetic System (WGS 84) coordinate reference system.",
            "value": 4326
        },
        "example_lks": {
            "summary": "LKS 94 (EPSG:3346)",
            "description": "The Lithuanian Coordinate System (LKS 94) reference system.",
            "value": 3346
        },
    },
    description="A spatial reference identifier (SRID) for geometry output."
)

query_geometry_output_type: schemas.GeometryOutputFormat = Query(
    schemas.GeometryOutputFormat.ewkt,
    openapi_examples={
        "example_ewkt": {
            "summary": "EWKT",
            "description": "Extended Well-Known Text (EWKT) format for representing geometric data.",
            "value": schemas.GeometryOutputFormat.ewkt
        },
        "example_ewkb": {
            "summary": "EWKB",
            "description": "Extended Well-Known Binary (EWKB) format for representing geometric data.",
            "value": schemas.GeometryOutputFormat.ewkb
        },
    },
    description="Specify the format for geometry output."
)

openapi_examples_geometry_filtering: Dict[str, Example] = {
    "example_ewkb": {
        "summary": "Filter using EWKB and 'intersects'",
        "description": "Filter geometries using hexed EWKB (Extended Well-Known Binary) format and the 'intersects' method. SRID inside EWKB is mandatory.",
        "value": {
            "filters": [
                {
                    "geometry": {
                        "method": "intersects",
                        "ewkb": "0103000020E6100000010000000500000045F6419605473940B1DD3D40F7574B4045F641960547394061E124CD1F574B40719010E50B4A394061E124CD1F574B40719010E50B4A3940B1DD3D40F7574B4045F6419605473940B1DD3D40F7574B40"
                    }
                }
            ]
        }
    },
    "example_ewkt": {
        "summary": "Filter using EWKT and 'intersects'",
        "description": "Filter geometries using EWKT (Extended Well-Known Text) format with the default 'intersects' method. SRID inside EWKT is mandatory.",
        "value": {
            "filters": [
                {
                    "geometry": {
                        "ewkt": "SRID=4326;POLYGON((25.277429 54.687233, 25.277429 54.680658, 25.289244 54.680658, 25.289244 54.687233, 25.277429 54.687233))"
                    }
                }
            ]
        }
    },
    "example_geojson": {
        "summary": "Filter using GeoJSON and 'contains'",
        "description": "Filter geometries using GeoJSON format and the 'contains' method. CRS inside GeoJSON is mandatory.",
        "value": {
            "filters": [
                {
                    "geometry": {
                        "method": "contains",
                        "geojson": "{\"crs\":{\"type\":\"name\",\"properties\":{\"name\":\"EPSG:4326\"}},"
                                   "\"type\":\"Polygon\",\"coordinates\":[[[25.277429,54.687233],"
                                   "[25.277429,54.680658],[25.289244,54.680658],[25.289244,54.687233],"
                                   "[25.277429,54.687233]]]}"
                    }
                }
            ]
        }
    }
}

openapi_examples_counties_filtering: Dict[str, Example] = {
    "example_counties_codes": {
        "summary": "Filter by county codes",
        "description": "Retrieve data for counties by specifying county codes.",
        "value": {
            "filters": [
                {
                    "counties": {
                        "codes": [5, 10]
                    }
                }
            ]
        }
    },
    "example_counties_feature_ids": {
        "summary": "Filter by county feature IDs",
        "description": "Retrieve data for counties by specifying feature IDs.",
        "value": {
            "filters": [
                {
                    "counties": {
                        "feature_ids": [3, 9]
                    }
                }
            ]
        }
    },
    "example_counties_name_starts": {
        "summary": "Filter by county name prefix",
        "description": "Retrieve data for counties where names start with the specified prefix.",
        "value": {
            "filters": [
                {
                    "counties": {
                        "name": {
                            "starts": "alyt"
                        }
                    }
                }
            ]
        }
    },
    "example_counties_name_exact": {
        "summary": "Filter by county exact name",
        "description": "Retrieve data for counties matching the exact specified name.",
        "value": {
            "filters": [
                {
                    "counties": {
                        "name": {
                            "exact": "Panevėžio apskr."
                        }
                    }
                }
            ]
        }
    },
    "example_counties_name_contains": {
        "summary": "Filter by county name substring",
        "description": "Retrieve data for counties where names contain the specified substring.",
        "value": {
            "filters": [
                {
                    "counties": {
                        "name": {
                            "contains": "no"
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_municipalities_filtering: Dict[str, Example] = {
    "example_municipalities_codes": {
        "summary": "Filter by municipality codes",
        "description": "Retrieve data for municipalities by specifying municipality codes.",
        "value": {
            "filters": [
                {
                    "municipalities": {
                        "codes": [21, 23]
                    }
                }
            ]
        }
    },
    "example_municipalities_feature_ids": {
        "summary": "Filter by municipality feature IDs",
        "description": "Retrieve data for municipalities by specifying feature IDs.",
        "value": {
            "filters": [
                {
                    "municipalities": {
                        "feature_ids": [6, 37]
                    }
                }
            ]
        }
    },
    "example_municipalities_name_starts": {
        "summary": "Filter by municipality name prefix",
        "description": "Retrieve data for municipalities where names start with the specified prefix.",
        "value": {
            "filters": [
                {
                    "municipalities": {
                        "name": {
                            "starts": "nerin"
                        }
                    }
                }
            ]
        }
    },
    "example_municipalities_name_exact": {
        "summary": "Filter by municipality exact name",
        "description": "Retrieve data for municipalities matching the exact specified name.",
        "value": {
            "filters": [
                {
                    "municipalities": {
                        "name": {
                            "exact": "Klaipėdos m. sav."
                        }
                    }
                }
            ]
        }
    },
    "example_municipalities_name_contains": {
        "summary": "Filter by municipality name substring",
        "description": "Retrieve data for municipalities where names contain the specified substring.",
        "value": {
            "filters": [
                {
                    "municipalities": {
                        "name": {
                            "contains": "r."
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_elderships_filtering: Dict[str, Example] = {
    "example_elderships_codes": {
        "summary": "Filter by eldership codes",
        "description": "Retrieve data for elderships by specifying eldership codes.",
        "value": {
            "filters": [
                {
                    "elderships": {
                        "codes": [1302, 1303]
                    }
                }
            ]
        }
    },
    "example_elderships_feature_ids": {
        "summary": "Filter by eldership feature IDs",
        "description": "Retrieve data for elderships by specifying feature IDs.",
        "value": {
            "filters": [
                {
                    "elderships": {
                        "feature_ids": [37, 282]
                    }
                }
            ]
        }
    },
    "example_elderships_name_starts": {
        "summary": "Filter by eldership name prefix",
        "description": "Retrieve data for elderships where names start with the specified prefix.",
        "value": {
            "filters": [
                {
                    "elderships": {
                        "name": {
                            "starts": "Lazdynų"
                        }
                    }
                }
            ]
        }
    },
    "example_elderships_name_exact": {
        "summary": "Filter by eldership exact name",
        "description": "Retrieve data for elderships matching the exact specified name.",
        "value": {
            "filters": [
                {
                    "elderships": {
                        "name": {
                            "exact": "Naujamiesčio sen."
                        }
                    }
                }
            ]
        }
    },
    "example_elderships_name_contains": {
        "summary": "Filter by eldership name substring",
        "description": "Retrieve data for elderships where names contain the specified substring.",
        "value": {
            "filters": [
                {
                    "elderships": {
                        "name": {
                            "contains": "miesčio"
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_residential_areas_filtering: Dict[str, Example] = {
    "example_residential_areas_codes": {
        "summary": "Filter by residential area codes",
        "description": "Retrieve data for residential areas by specifying residential area codes.",
        "value": {
            "filters": [
                {
                    "residential_areas": {
                        "codes": [10184, 10264]
                    }
                }
            ]
        }
    },
    "example_residential_areas_feature_ids": {
        "summary": "Filter by residential area feature IDs",
        "description": "Retrieve data for residential areas by specifying feature IDs.",
        "value": {
            "filters": [
                {
                    "residential_areas": {
                        "feature_ids": [279, 15942]
                    }
                }
            ]
        }
    },
    "example_residential_areas_name_starts": {
        "summary": "Filter by residential area name prefix",
        "description": "Retrieve data for residential areas where names start with the specified prefix.",
        "value": {
            "filters": [
                {
                    "residential_areas": {
                        "name": {
                            "starts": "Nema"
                        }
                    }
                }
            ]
        }
    },
    "example_residential_areas_name_exact": {
        "summary": "Filter by residential area exact name",
        "description": "Retrieve data for residential areas matching the exact specified name.",
        "value": {
            "filters": [
                {
                    "residential_areas": {
                        "name": {
                            "exact": "Neveronys"
                        }
                    }
                }
            ]
        }
    },
    "example_residential_areas_name_contains": {
        "summary": "Filter by residential area name substring",
        "description": "Retrieve data for residential areas where names contain the specified substring.",
        "value": {
            "filters": [
                {
                    "residential_areas": {
                        "name": {
                            "contains": "aka"
                        }
                    }
                }
            ]
        }
    }
}
openapi_examples_streets_filtering: Dict[str, Example] = {
    "example_streets_codes": {
        "summary": "Filter by street codes",
        "description": "Retrieve data for streets by specifying street codes.",
        "value": {
            "filters": [
                {
                    "streets": {
                        "codes": [1207622, 1611772]
                    }
                }
            ]
        }
    },
    "example_streets_feature_ids": {
        "summary": "Filter by street feature IDs",
        "description": "Retrieve data for streets by specifying feature IDs.",
        "value": {
            "filters": [
                {
                    "streets": {
                        "feature_ids": [19910, 21783]
                    }
                }
            ]
        }
    },
    "example_streets_name_starts": {
        "summary": "Filter by street name prefix",
        "description": "Retrieve data for streets where names start with the specified prefix.",
        "value": {
            "filters": [
                {
                    "streets": {
                        "name": {
                            "starts": "žemaičių"
                        }
                    }
                }
            ]
        }
    },
    "example_streets_name_exact": {
        "summary": "Filter by street exact name",
        "description": "Retrieve data for streets matching the exact specified name.",
        "value": {
            "filters": [
                {
                    "streets": {
                        "name": {
                            "exact": "Žemaičių g."
                        }
                    }
                }
            ]
        }
    },
    "example_streets_name_contains": {
        "summary": "Filter by street name substring",
        "description": "Retrieve data for streets where names contain the specified substring.",
        "value": {
            "filters": [
                {
                    "streets": {
                        "name": {
                            "contains": "al."
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_addresses_filtering: Dict[str, Example] = {
    "example_addresses_codes": {
        "summary": "Filter by address codes",
        "description": "Retrieve data for addresses by specifying address codes.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "codes": [157385248, 156657369]
                    }
                }
            ]
        }
    },
    "example_addresses_feature_ids": {
        "summary": "Filter by address feature IDs",
        "description": "Retrieve data for addresses by specifying feature IDs.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "feature_ids": [115834, 174273]
                    }
                }
            ]
        }
    },
    "example_plot_or_building_number_contains": {
        "summary": "Filter by address plot or building number containing substring",
        "description": "Retrieve data for addresses where plot or building number contains the specified substring.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "plot_or_building_number": {
                            "contains": "A"
                        }
                    }
                }
            ]
        }
    },
    "example_plot_or_building_number_exact": {
        "summary": "Filter by address exact plot or building number",
        "description": "Retrieve data for addresses matching the exact plot or building number.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "plot_or_building_number": {
                            "exact": "21"
                        }
                    }
                }
            ]
        }
    },
    "example_plot_or_building_number_starts": {
        "summary": "Filter by address plot or building number starting with prefix",
        "description": "Retrieve data for addresses where plot or building number starts with the specified prefix.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "plot_or_building_number": {
                            "starts": "21"
                        }
                    }
                }
            ]
        }
    },
    "example_building_block_number_contains": {
        "summary": "Filter by address building block number containing substring",
        "description": "Retrieve data for addresses where building block number contains the specified substring.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "building_block_number": {
                            "contains": "A"
                        }
                    }
                }
            ]
        }
    },
    "example_building_block_number_exact": {
        "summary": "Filter by address exact building block number",
        "description": "Retrieve data for addresses matching the exact building block number.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "building_block_number": {
                            "exact": "9"
                        }
                    }
                }
            ]
        }
    },
    "example_building_block_number_starts": {
        "summary": "Filter by address building block number starting with prefix",
        "description": "Retrieve data for addresses where building block number starts with the specified prefix.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "building_block_number": {
                            "starts": "9"
                        }
                    }
                }
            ]
        }
    },
    "example_postal_code_contains": {
        "summary": "Filter by address postal code containing substring",
        "description": "Retrieve data for addresses where postal codes contain the specified substring.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "postal_code": {
                            "contains": "36128"
                        }
                    }
                }
            ]
        }
    },
    "example_postal_code_exact": {
        "summary": "Filter by address exact postal code",
        "description": "Retrieve data for addresses matching the exact postal code.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "postal_code": {
                            "exact": "LT-36128"
                        }
                    }
                }
            ]
        }
    },
    "example_postal_code_starts": {
        "summary": "Filter by address postal code starting with prefix",
        "description": "Retrieve data for addresses where postal codes start with the specified prefix.",
        "value": {
            "filters": [
                {
                    "addresses": {
                        "postal_code": {
                            "starts": "LT-361"
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_rooms_filtering: Dict[str, Example] = {
    "example_rooms_codes": {
        "summary": "Filter by room codes",
        "description": "Retrieve data for rooms by specifying room codes.",
        "value": {
            "filters": [
                {
                    "rooms": {
                        "codes": [160311305, 160311324]
                    }
                }
            ]
        }
    },
    "example_room_number_contains": {
        "summary": "Filter by room number containing substring",
        "description": "Retrieve data for rooms where room number contains the specified substring.",
        "value": {
            "filters": [
                {
                    "rooms": {
                        "room_number": {
                            "contains": "7"
                        }
                    }
                }
            ]
        }
    },
    "example_room_number_exact": {
        "summary": "Filter by room exact number",
        "description": "Retrieve data for rooms matching the exact room number.",
        "value": {
            "filters": [
                {
                    "rooms": {
                        "room_number": {
                            "exact": "7"
                        }
                    }
                }
            ]
        }
    },
    "example_room_number_starts": {
        "summary": "Filter by room number starting with prefix",
        "description": "Retrieve data for rooms where room number starts with the specified prefix.",
        "value": {
            "filters": [
                {
                    "rooms": {
                        "room_number": {
                            "starts": "7"
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_parcels_filtering: Dict[str, Example] = {
    "example_parcels_unique_numbers": {
        "summary": "Filter by unique numbers",
        "description": "Retrieve data for parcels by specifying parcel unique numbers.",
        "value": {
            "filters": [
                {
                    "parcels": {
                        "unique_numbers": [110100090085, 110100210172]
                    }
                }
            ]
        }
    },
    "example_parcel_cadastral_number_contains": {
        "summary": "Filter by parcel cadastral number containing substring",
        "description": "Retrieve data for parcels where parcel cadastral number contains the specified substring.",
        "value": {
            "filters": [
                {
                    "parcels": {
                        "cadastral_number": {
                            "contains": "1101/0028"
                        }
                    }
                }
            ]
        }
    },
    "example_parcel_cadastral_number_exact": {
        "summary": "Filter by parcel exact cadastral number",
        "description": "Retrieve data for parcels matching the exact parcel cadastral number.",
        "value": {
            "filters": [
                {
                    "parcels": {
                        "cadastral_number": {
                            "exact": "1101/0028:0196"
                        }
                    }
                }
            ]
        }
    },
    "example_parcel_cadastral_number_starts": {
        "summary": "Filter by parcel cadastral number starting with prefix",
        "description": "Retrieve data for parcels where parcel cadastral number starts with the specified prefix.",
        "value": {
            "filters": [
                {
                    "parcels": {
                        "cadastral_number": {
                            "starts": "1101/0028"
                        }
                    }
                }
            ]
        }
    },
    "example_parcel_area_equal": {
        "summary": "Filter by parcel area equal to",
        "description": "Retrieve data for parcels where parcel area is equal to number.",
        "value": {
            "filters": [
                {
                    "parcels": {
                        "area_ha": {
                            "eq": 0.01
                        }
                    }
                }
            ]
        }
    },
    "example_parcel_area_combo": {
        "summary": "Filter by parcel area less/greater than",
        "description": "Retrieve data for parcels where parcel area is less / less or equal / greater / greater or equal to numbers.",
        "value": {
            "filters": [
                {
                    "parcels": {
                        "area_ha": {
                            "gte": 0.01,
                            "lt": 0.02
                        }
                    }
                },
                {
                    "parcels": {
                        "area_ha": {
                            "gt": 1000,
                            "lte": 2000
                        }
                    }
                }
            ]
        }
    }
}

openapi_examples_purpose_types_filtering: Dict[str, Example] = {
    "example_purpose_types_ids": {
        "summary": "Filter by purpose IDs",
        "description": "Retrieve data for purpose types by specifying purpose type IDs.",
        "value": {
            "filters": [
                {
                    "purposes": {
                        "purpose_ids": [610, 995]
                    }
                }
            ]
        }
    },
    "example_purpose_types_name_contains": {
        "summary": "Filter by purpose type name containing substring",
        "description": "Retrieve data for purpose types where purpose type name contains the specified substring.",
        "value": {
            "filters": [
                {
                    "purposes": {
                        "name": {
                            "contains": "ūkio"
                        }
                    }
                }
            ]
        }
    },
    "example_purpose_types_name_exact": {
        "summary": "Filter by purpose type exact name",
        "description": "Retrieve data for purpose types matching the exact purpose type name.",
        "value": {
            "filters": [
                {
                    "purposes": {
                        "name": {
                            "exact": "žemės ūkio"
                        }
                    }
                }
            ]
        }
    },
    "example_purpose_types_name_starts": {
        "summary": "Filter by purpose type cadastral number starting with prefix",
        "description": "Retrieve data for purpose types where purpose type cadastral number starts with the specified prefix.",
        "value": {
            "filters": [
                {
                    "purposes": {
                        "name": {
                            "starts": "žemės"
                        }
                    }
                }
            ]
        }
    }
}


openapi_examples_status_types_filtering: Dict[str, Example] = {
    "example_status_types_ids": {
        "summary": "Filter by status IDs",
        "description": "Retrieve data for status types by specifying status type IDs.",
        "value": {
            "filters": [
                {
                    "statuses": {
                        "status_ids": [21, 22]
                    }
                }
            ]
        }
    },
    "example_status_types_name_contains": {
        "summary": "Filter by status type name containing substring",
        "description": "Retrieve data for status types where status type name contains the specified substring.",
        "value": {
            "filters": [
                {
                    "statuses": {
                        "name": {
                            "contains": "performuotas"
                        }
                    }
                }
            ]
        }
    },
    "example_status_types_name_exact": {
        "summary": "Filter by status type exact name",
        "description": "Retrieve data for status types matching the exact status type name.",
        "value": {
            "filters": [
                {
                    "statuses": {
                        "name": {
                            "exact": "daiktas performuotas"
                        }
                    }
                }
            ]
        }
    },
    "example_status_types_name_starts": {
        "summary": "Filter by status type cadastral number starting with prefix",
        "description": "Retrieve data for status types where status type cadastral number starts with the specified prefix.",
        "value": {
            "filters": [
                {
                    "statuses": {
                        "name": {
                            "starts": "daiktas"
                        }
                    }
                }
            ]
        }
    }
}
