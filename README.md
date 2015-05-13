# Municipality of Anchorage Property Tax Data to GeoJSON

A simple data loader for parsing MOA property tax data and merging it with GIS data
to produce a bulk GeoJSON output. More details to come.

```json
{
    "type": "FeatureCollection",
    "features":
        [
            {
                "type": "Feature",
                "geometry":
                    {
                        "type": "MultiLineString",
                        "coordinates":
                            [[
                                [-149.8991555097872,  61.22039824848633],
                                [-149.89887073444086, 61.22039991294965],
                                [-149.8988718620727,  61.22004489790546],
                                [-149.8991566398672,  61.22004323891429],
                                [-149.8991555097872,  61.22039824848633]
                            ]]
                    },
                "properties":
                    {
                        "area": 6514.352207645774,
                        "deed_date": "2012-07-23T00:00:00",
                        "year_built": null,
                        "2006":
                            {
                                "zone": "B2C",
                                "total_value": 118000,
                                "tax_district": "001",
                                "bldg_value": 0,
                                "land_value": 118000,
                                "land_use_code": "PARKING MISC.",
                                "lci": "Com"
                            },
                        "2009":
                            {
                                "zone": "B2C",
                                "total_value": 118000,
                                "tax_district": "001",
                                "bldg_value": 0,
                                "land_value": 118000,
                                "land_use_code": "PARKING MISC.",
                                "lci": "Com"
                            },
                        "2012":
                            {
                                "zone": "B2C",
                                "total_value": 118000,
                                "tax_district": "001",
                                "bldg_value": 0,
                                "land_value": 118000,
                                "land_use_code": "PARKING MISC.",
                                "lci": "Com"
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
