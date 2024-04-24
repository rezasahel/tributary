from flask import Flask, request, jsonify
import json
import redis
from loguru import logger

app = Flask(__name__)

HISTORY_LENGTH = 10
DATA_KEY = 'engine_temperature'

def get_current_temperature():
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    current_temperature = database.lindex(DATA_KEY, 0)
    return current_temperature

def calculate_average_temperature():
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    temperatures = database.lrange(DATA_KEY, 0, -1)
    temperatures = [float(temp) for temp in temperatures]
    average_temperature = sum(temperatures) / len(temperatures) if temperatures else 0
    return average_temperature

@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get('engine_temperature')
    logger.info(f'engine temperature to record is: {engine_temperature}')

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    logger.info(f"record request successful")
    return {"success": True}, 200

@app.route('/collect', methods=['GET'])
def collect_engine_temperature():
    current_temperature = get_current_temperature()
    average_temperature = calculate_average_temperature()
    response = {
        "current_engine_temperature": current_temperature,
        "average_engine_temperature": average_temperature
    }
    return jsonify(response), 200

