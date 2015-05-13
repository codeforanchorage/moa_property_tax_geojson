# Municipality of Anchorage Property Tax Data to GeoJSON

Get the data here:

https://github.com/codeforanchorage/moa_property_tax_geojson/releases/latest

A simple data loader for parsing MOA property tax data and merging it with GIS data
to produce a bulk GeoJSON output. More details to come.

```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "coordinates": [
                    [
                        [
                            -149.90791833095705,
                            61.21721713678784
                        ],
                        [
                            -149.90838226848814,
                            61.21721349277347
                        ],
                        [
                            -149.9079189749373,
                            61.21749577900827
                        ],
                        [
                            -149.90791833095705,
                            61.21721713678784
                        ]
                    ]
                ],
                "type": "Polygon"
            },
            "properties": {
                "area": 4165.404167801142,
                "bldg_value": 324100,
                "deed_date": "2006-09-22T00:00:00",
                "land_use_code": "SINGLE FAMILY",
                "land_value": 201900,
                "lci": "Res",
                "parcel_id": "00103103000",
                "tax_district": "001",
                "tax_year": "2014",
                "total_value": 526000,
                "year_built": 1959.0,
                "zone": "R3",
                "prior": {
                    "2006": {
                        "bldg_value": 324100,
                        "land_use_code": "SINGLE FAMILY",
                        "land_value": 201900,
                        "lci": "Res",
                        "tax_district": "001",
                        "total_value": 526000,
                        "zone": "R3"
                    },
                    "2009": {
                        "bldg_value": 324100,
                        "land_use_code": "SINGLE FAMILY",
                        "land_value": 201900,
                        "lci": "Res",
                        "tax_district": "001",
                        "total_value": 526000,
                        "zone": "R3"
                    },
                    "2012": {
                        "bldg_value": 324100,
                        "land_use_code": "SINGLE FAMILY",
                        "land_value": 201900,
                        "lci": "Res",
                        "tax_district": "001",
                        "total_value": 526000,
                        "zone": "R3"
                    }
                }
            }
        },
        {...},
        {...},
        {...},
    ]
}
```

## Requirements:

- ogr2ogr
- MongoDB
- MOA source data

## To install (Mac with Homebrew GDAL):

    $ virtualenv --system-site-packages venv
    $ source venv/bin/activate
    $ pip install -I -r requirements-nogdal.txt

## To install (everyone else):

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

## To run:

    $ mongod
    $ python main.py
