from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.json_schema import JsonSchemaValue
from bson.objectid import ObjectId
from src.db import db
from src.pydantic_annotations.objectid_annotation import ObjectIdAnnotation

db = db()['vehicles']

class Vehicle(BaseModel):
    id : Annotated[Optional[ObjectId], ObjectIdAnnotation] = Field(default=None, alias="_id")
    name : str
    model : str
    date_created : datetime

    def create(self):
        doc = self.model_dump()
        del doc['id']
        record = db.insert_one(doc)
        self.id = record.inserted_id
        return self
    
    @staticmethod
    def find_all():
        data = db.find({})
        return [Vehicle(**datum).model_dump() for datum in data]
