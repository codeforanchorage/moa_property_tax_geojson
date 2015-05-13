import ogr
import osr
import json
import logging
from datetime import datetime
from os import SEEK_END
from bson.code import Code
from pymongo import MongoClient, UpdateOne, InsertOne
from lookups import lci, land_use_code


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)d %(levelname)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("tax_logger")
logger.info("getting started")

SHOW_OWNER = False

def taxdata(record, year=None):
    temp                  = {}
    temp['tax_district']  = record[319:319+3].strip()
    temp['zone']          = record[322:322+5].strip()
    temp['land_value']    = int(record[337:337+9].strip())
    temp['bldg_value']    = int(record[346:346+9].strip())
    temp['total_value']   = int(record[355:355+9].strip())
    temp['lci']           = lci[record[450:450+1].strip()]
    temp['land_use_code'] = land_use_code[record[451:451+3].strip()]
    if SHOW_OWNER:
        owner          = {}
        owner['name']  = record[13:13+30].strip()
        owner['city']  = record[133:133+16].strip()
        owner['state'] = record[149:149+2].strip()
        owner['zip']   = record[151:151+9].strip()
        temp['owner']  = owner

    output              = {}
    output[year]        = temp
    output['parcel_id'] = record[0:0+11]

    try:
        output['deed_date'] = datetime.strptime(record[271:271+8], '%m%d%Y')
    except ValueError:
        output['deed_date'] = None
    if temp['lci'] == 'Res':
        tmp_year_built = record[506:506+4].strip()
    elif temp['lci'] == 'Com':
        tmp_year_built = record[502:502+4].strip()
    if tmp_year_built:
        try:
            output['year_built'] = int(datetime.strptime(tmp_year_built, '%Y').year)
        except ValueError:
            output['year_built'] = None
    return output

def import_data():
    client = MongoClient('mongodb://127.0.0.1:27017/')
    logger.info("using db 'moa_property_tax'")
    db = client['moa_property_tax']
    logger.info("dropping temp, tax_data, geojson")
    db.drop_collection('temp')
    db.drop_collection('tax_data')
    db.drop_collection('geojson')
    mtemp = db['temp']
    mtax_data = db['tax_data']
    mgeojson = db['geojson']

    # first, import property tax data
    files = ['data/Anchorage-Property-Tax-Data/2006.ascii',
             'data/Anchorage-Property-Tax-Data/2009.ascii',
             'data/Anchorage-Property-Tax-Data/2012.ascii',
             'data/Anchorage-Property-Tax-Data/2014.ascii']
    mapper = """
        function() {
            emit(
                this.parcel_id,
                {
    """
    reducer = """
        function(key, values) {
            var result = {
    """
    years = []
    for path in files:
        with open(path, "r") as f:
            year = path[-10:-6]
            mapper += '"{}": this["{}"],'.format(year, year)
            reducer += '"{}": null,'.format(year)
            years.append(year)
            logger.info("processing {}".format(year))
            transaction = []
            for line in f:
                transaction.append(InsertOne(taxdata(line, year)))
            logger.info("writing tax data results")
            result = mtemp.bulk_write(transaction)
    mapper += """
                    deed_date: this.deed_date,
                    year_built: this.year_built
                }
            );
        }
    """
    reducer +=  """
                deed_date: null,
                year_built: null
            };

            values.forEach(function(value) {
                for (var property in value) {
                    if (result[property] === null && value[property] !== null) {
                        result[property] = value[property];
                    }
                }
            });
            return result;
        }
    """

    mtemp.map_reduce(Code(mapper), Code(reducer), "tax_data")
    db.drop_collection('temp')

    # then, import parcel geometry
    driver = ogr.GetDriverByName("ESRI Shapefile")
    shpfile = driver.Open('data/parcels_shp/parcels.shp', 0)
    layer = shpfile.GetLayer()
    source_projection = layer.GetSpatialRef()
    target_projection = osr.SpatialReference()
    target_projection.ImportFromEPSG(4326)
    transformer = osr.CoordinateTransformation(source_projection, target_projection)

    transaction = []
    logger.info("extracting geometry")
    for feature in layer:
        geometry = feature.GetGeometryRef()
        area = 0
        if geometry:
            area = geometry.GetArea()
            geometry_clone = geometry.Clone()
            geometry_clone.Transform(transformer)
            geometry_clone = geometry_clone.SimplifyPreserveTopology(0.0001)
            geometry_clone = ogr.ForceToMultiLineString(geometry_clone)
            feature.SetGeometry(geometry_clone)
        transaction.append(UpdateOne(
            {'_id': feature.GetFieldAsString('PARCEL_NUM')},
            {'$set': {
                'geometry': json.loads(feature.GetGeometryRef().ExportToJson()),
                'value.area': area
            }}))
    logger.info("writing geometry")
    result = mtax_data.bulk_write(transaction)

    # convert to geojson
    logger.info("converting to geojson")
    transaction = []
    for record in mtax_data.find({"geometry": {"$ne": None}}):
        record['type'] = 'Feature'
        record['geometry']['type'] = 'Polygon'
        record['properties'] = record.pop('value')
        record['properties']['parcel_id'] = record['_id']
        record['properties']['prior'] = {}
        for year in years:
            record['properties']['prior'][year] = record['properties'].pop(year)
        for year in reversed(years):
            if year in record['properties']['prior'] and record['properties']['prior'][year]:
                record['properties'].update(record['properties']['prior'].pop(year))
                record['properties']['tax_year'] = year
                break
        transaction.append(InsertOne(record))
    logger.info("writing geojson results")
    result = mgeojson.bulk_write(transaction)

    logger.info("dumping geojson to disk")
    with open('output.geojson', 'w') as json_file:
        json_file.write('{"type":"FeatureCollection","features":[')
        for record in mgeojson.find():
            del record['_id']
            if record['properties']['deed_date']:
                record["properties"]["deed_date"] = record["properties"]["deed_date"].isoformat()
            json.dump(record, json_file, separators=(',', ':'))
            json_file.write(',')
    with open('output.geojson', 'r+') as json_file:
        json_file.seek(-1, SEEK_END)
        json_file.truncate()
        json_file.write(']}')
    logger.info("done!")

    client.close()


if __name__=='__main__':
    import_data()
