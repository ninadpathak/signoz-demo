from flask import Flask, jsonify
import logging
import random
import time
from contextlib import nullcontext
from opentelemetry import metrics, trace

app = Flask(__name__)

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DummySpan:
    def set_attribute(self, *args, **kwargs):
        pass

    def add_event(self, *args, **kwargs):
        pass


class DummyCounter:
    def add(self, *args, **kwargs):
        pass


DUMMY_SPAN = DummySpan()
DUMMY_COUNTER = DummyCounter()

if trace is not None:
    try:
        tracer = trace.get_tracer("order-service")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Unable to acquire tracer: %s", exc)
        tracer = None
else:
    tracer = None

if metrics is not None:
    try:
        meter = metrics.get_meter("order-service")
        order_counter = meter.create_counter(
            name="orders_processed",
            description="Number of orders processed",
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Unable to create counter: %s", exc)
        order_counter = DUMMY_COUNTER
else:
    order_counter = DUMMY_COUNTER


def start_span(name):
    if tracer is None:
        return nullcontext(DUMMY_SPAN)
    return tracer.start_as_current_span(name)


@app.route('/createOrder', methods=['POST'])
def create_order():
    with start_span("db_process_order") as span:
        order_id = f"ORD-{random.randint(10000, 99999)}"
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.value", random.randint(50, 500))

        time.sleep(random.uniform(0.05, 0.15))

        if random.random() < 0.9:
            span.add_event("Order created successfully", {"order.status": "success"})
            order_counter.add(1, {"status": "success"})
            return jsonify({
                "status": "success",
                "orderId": order_id,
            }), 200

        span.add_event("Order creation failed", {"order.status": "failed"})
        order_counter.add(1, {"status": "failed"})
        return jsonify({
            "status": "error",
            "message": "Failed to create order",
        }), 500


@app.route('/checkInventory', methods=['GET'])
def check_inventory():
    with start_span("inventory_check") as span:
        delay = random.uniform(0.2, 0.8)
        span.set_attribute("inventory.delay_ms", delay * 1000)
        time.sleep(delay)

        stock = random.randint(0, 1000)
        span.set_attribute("inventory.count", stock)
        return jsonify({"availableItems": stock}), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    print("Starting Order Service on http://localhost:5001")
    print("View traces at http://localhost:3301")
    app.run(host='0.0.0.0', port=5001, debug=False)
