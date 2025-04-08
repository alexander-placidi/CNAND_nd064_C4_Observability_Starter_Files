import logging, requests
from flask import Flask, request, jsonify
from jaeger_client import Config
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from environs import env
import random

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


tracer = init_tracer("backend")

NASA_API_KEY = env("NASA_API_KEY", default="DEMO_KEY")

@app.route("/asteroids")
def homepage():
    with tracer.start_span('get_asteroids') as span:
        res = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date=2015-09-07&end_date=2015-09-08&api_key={NASA_API_KEY}")
        json_response = res.json()
        near_earth_objects_dict = json_response["near_earth_objects"]
        span.set_tag("asteroids_count", json_response["element_count"])
        asteroids = []
        
        for k, v in near_earth_objects_dict.items():
            logging.info(f"Getting near earth asteriods {k}")
            for near_earth_object in v:
                asteroid = {}
                
                with tracer.start_span("request-Near_Earth_Object_Web_Service") as site_span:
                    logging.info(f"Name: {near_earth_object["name"]} Hazardous: {near_earth_object["is_potentially_hazardous_asteroid"]}")
                    try:
                        asteroid["name"] = near_earth_object["name"]
                        asteroid["is_potentially_hazardous_asteroid"] = near_earth_object["is_potentially_hazardous_asteroid"]
                        asteroids.append(asteroid)
                        site_span.set_tag("http.status_code", res.status_code)
                        site_span.set_tag("asteriod_name", asteroid["name"])
                        site_span.set_tag("is_potentially_hazardous_asteroid", asteroid["is_potentially_hazardous_asteroid"])
                    except Exception:
                        logging.error(f"Unable to get asteroid info")
                        site_span.set_tag("http.status_code", res.status_code)      
    
    return asteroids

@app.route("/trail")
def trail():
    n = random.randrange(0, 10)
    if(n < 3):
        raise Exception("Service not available.")
    else:
        return "Hello"

if __name__ == "__main__":
    app.run()