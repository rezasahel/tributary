from flask import Flask, request
import json
import redis as redis
from loguru import logger


app = Flask(__name__)


HISTORY_LENGTH = 10
DATA_KEY = 'engine_temperature'

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
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"record request successful")
    return {"success": True}, 200


@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    return {"success": True}, 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

