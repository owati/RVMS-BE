from typing import Any
from bson.objectid import ObjectId
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue

class ObjectIdAnnotation:
    @classmethod
    def validate_object_id(cls, v: Any, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v

        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler) -> core_schema.CoreSchema:
        def validate_from_str(value: str) -> ObjectId:
            return ObjectId(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                from_str_schema
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x : str(x)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        pass
        return handler(core_schema.str_schema())
