from typing import Annotated, Optional
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from src.db import db
from src.pydantic_annotations.objectid_annotation import ObjectIdAnnotation

db = db()['monitoring-data']

class MonitoringData(BaseModel):
    id : Annotated[Optional[ObjectId], ObjectIdAnnotation] = Field(default=None, alias="_id")
    journey_id : Annotated[ObjectId, ObjectIdAnnotation]
    longitude : float
    lattitude : float
    fuelLevel : float
    speed : float

    def create(self):
        doc = self.model_dump()
        doc['journey_id'] = ObjectId(doc['journey_id'])
        del doc['id']
        data = db.insert_one(doc)
        self.id = data.inserted_id
        return self
    
    @staticmethod
    def parse_data(data : dict):
        value, direction = float(data['longitude'][:-1]), data['longitude'][-1]
        data['longitude'] = -value if direction == 'W' else value

        value, direction = float(data['lattitude'][:-1]), data['lattitude'][-1]
        data['lattitude'] = -value if direction == 'S' else value

        return data
    
    @staticmethod
    def aggregate_for_journey(journey_id):
        data = db.aggregate([
            {
                '$match': {
                    'journey_id': ObjectId(journey_id)
                }
            }, {
                '$group': {
                    '_id': None, 
                    'avg_fuel_level': {
                        '$avg': '$fuelLevel'
                    }, 
                    'avg_speed': {
                        '$avg': '$speed'
                    }, 
                    'count': {
                        '$count': {}
                    }
                }
            }
        ])
        
        return list(data)
    
    @staticmethod
    def get_full_data_for_journey(journey_id):
        data = db.find({
            "journey_id" : ObjectId(journey_id)
        })
        return [MonitoringData(**datum).model_dump() for datum in data]