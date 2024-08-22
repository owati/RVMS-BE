
import json
from typing import Annotated, Optional
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from pydantic import BaseModel, Field
from src.db import db
from bson.json_util import dumps as bson_dumps
from src.pydantic_annotations.objectid_annotation import ObjectIdAnnotation

db = db()['journey-data']

class JourneyData(BaseModel):
    id : Annotated[Optional[ObjectId], ObjectIdAnnotation] = Field(default=None, alias="_id")
    vehicle_id : str
    start_time : datetime
    end_time : datetime

    def create(self):
        doc = self.model_dump()
        del doc["id"]
        data = db.insert_one(doc)
        self.id = data.inserted_id
        return self
    
    @staticmethod
    def update_end_time(_id, end_time):
        print("Updateing", _id)
        print(db.update_one({"_id" : _id}, {
            "$set" : {
                "end_time" : end_time
            }
        }))
    
    @staticmethod
    def find_completed_by_vehicle_id(vehicle_id : str):
        thirty_mins_ago = datetime.now() - timedelta(minutes=30)
        print(thirty_mins_ago)
        data = db.find({
            'vehicle_id' : vehicle_id, 
            "end_time" : { 
                "$lt" : thirty_mins_ago
            }
        })
        return [
            JourneyData(**datum).model_dump()
            for datum in data
        ]
    
    @staticmethod
    def find_all_current_journey():
        thirty_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
        data = db.aggregate(
            [
                {
                    "$match" : {
                        "end_time" : {"$gt" : thirty_mins_ago }
                    }
                },
                {
                    "$lookup" : {
                        "from" : "monitoring-data",
                        "localField" : "_id",
                        "foreignField" : "journey_id",
                        "as" : "monitoring_data",
                        "pipeline" : 
                        [
                            {
                                "$project" : 
                                {
                                    "_id" : 0,
                                    "journey_id" : 0 
                                }
                            }
                        ]
                    }
                }
            ]
        )

        return [json.loads(bson_dumps(datum))  for datum in data]
    
