import logging
from flask import Flask, request, jsonify
from jaeger_client import Config
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

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

@app.route("/")
def homepage():
    with tracer.start_span('say-hello') as span:
        span.set_tag('test-tag', "test")
    
    return "Hello World"

if __name__ == "__main__":
    app.run()