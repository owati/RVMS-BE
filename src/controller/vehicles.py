import json
import traceback
import threading
from datetime import datetime
from redis import Redis
from flask_socketio import SocketIO
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from src.db.vehicle import Vehicle
from src.db.monitoring_data import MonitoringData
from src.db.journey import JourneyData


def vehicle_controller_factory(socketio : SocketIO, redis_client : Redis):

    vehicles_controller = Blueprint('vehicles', __name__)

    @vehicles_controller.post('/')
    def create_vehicles():
        try:
            data = json.loads(request.data)
            vehicle = Vehicle(
                name=data['name'],
                model=data['model'],
                date_created=datetime.now()
            ).create()
            return jsonify({
                    "message" : "Vehicle created successfully",
                    "data" : vehicle.model_dump()
                }), 201
        except Exception as err:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
        
    @vehicles_controller.get("/")
    def get_vehicles():
        try:
            vehicles = Vehicle.find_all()
            return jsonify({
                "message" : "Fetched successfully",
                "data" : vehicles
            }), 200
        except:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
        

    @vehicles_controller.post('/monitoring/<string:vehicle_id>')
    def update_monitoring(vehicle_id : str):
        try:
            journey_id = redis_client.get(vehicle_id)
            current_time = datetime.now()
            if not journey_id:
                # Probably a new journey 😁
                journey = JourneyData(
                    vehicle_id=vehicle_id,
                    start_time=current_time,
                    end_time=current_time
                ).create()
                journey_id = journey.id
                redis_client.set(vehicle_id, str(journey_id), ex=1_800, nx=True)
            else:
                journey_id = ObjectId(journey_id.decode("utf-8"))

            data = MonitoringData.parse_data(json.loads(request.data))
            data['journey_id'] = ObjectId(journey_id)
            monitorind_data = MonitoringData(**data).create()
            thread = threading.Thread(target=lambda : socketio.emit('data', 
                                                                    monitorind_data.model_dump()))
            thread.start()
            redis_client.expire(vehicle_id, 1_800, xx=True)
            JourneyData.update_end_time(journey_id, current_time)
            
            return jsonify({"message" : "Sucess"}), 200
        except:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
        
    @vehicles_controller.get('/journey-completed/<string:vehicle_id>')
    def get_completed_journey(vehicle_id : str):
        try:
            journeys = JourneyData.find_completed_by_vehicle_id(vehicle_id)
            return jsonify({
                "message" : "Fetched successfully",
                "data" : journeys
            }), 200
        except:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
        
    @vehicles_controller.get('/journey-current')
    def get_current_journey():
        try:
            journeys = JourneyData.find_all_current_journey()
            return jsonify({
                "message" : "Fetched successfully",
                "data" : journeys
            }), 200
        except:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
        
    
    @vehicles_controller.get('/journey-data/<string:journey_id>')
    def get_journey_data(journey_id):
        try:
            agg_data = MonitoringData.aggregate_for_journey(journey_id)
            return jsonify({
                "message" : "Fetched successfully",
                "data" : agg_data
            })
        except:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
          
    @vehicles_controller.get('/journey-data-full/<string:journey_id>')
    def get_journey_data_full(journey_id):
        try:
            data = MonitoringData.get_full_data_for_journey(journey_id)
            return jsonify({
                "message" : "Fetched successfully",
                "data" : data
            })
        except:
            traceback.print_exc()
            return jsonify({"message" : "Something is wrong"}), 400
          
        
    return vehicles_controller