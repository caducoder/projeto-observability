import json
import platform
from flask import Flask, jsonify, request
from prometheus_client import start_http_server, Counter, REGISTRY

app = Flask(__name__)

employees = [
    {"id": 1, "name": "Ashley"},
    {"id": 2, "name": "Kate"},
    {"id": 3, "name": "Joe"},
]

request_counter = Counter("http_requests", "HTTP request", ["status_code", "instance"])

nextEmployeeId = 4


@app.route("/employees", methods=["GET"])
def get_employees():
    request_counter.labels(status_code="200", instance=platform.node()).inc()
    return jsonify(employees)


@app.route("/employees/<int:id>", methods=["GET"])
def get_employee_by_id(id: int):
    employee = get_employee(id)
    if employee is None:
        return jsonify({"error": "Employee does not exist"}), 404
    request_counter.labels(status_code="200", instance=platform.node()).inc()
    return jsonify(employee)


def get_employee(id):
    return next((e for e in employees if e["id"] == id), None)


def employee_is_valid(employee):
    for key in employee.keys():
        if key != "name":
            return False
    return True


@app.route("/employees", methods=["POST"])
def create_employee():
    global nextEmployeeId
    employee = json.loads(request.data)
    if not employee_is_valid(employee):
        request_counter.labels(status_code="400", instance=platform.node()).inc()
        return jsonify({"error": "Invalid employee properties."}), 400

    employee["id"] = nextEmployeeId
    nextEmployeeId += 1
    employees.append(employee)

    request_counter.labels(status_code="201", instance=platform.node()).inc()
    return "", 201, {"location": f'/employees/{employee["id"]}'}


@app.route("/employees/<int:id>", methods=["PUT"])
def update_employee(id: int):
    employee = get_employee(id)
    if employee is None:
        request_counter.labels(status_code="404", instance=platform.node()).inc()
        return jsonify({"error": "Employee does not exist."}), 404

    updated_employee = json.loads(request.data)
    if not employee_is_valid(updated_employee):
        request_counter.labels(status_code="400", instance=platform.node()).inc()
        return jsonify({"error": "Invalid employee properties."}), 400

    employee.update(updated_employee)

    request_counter.labels(status_code="200", instance=platform.node()).inc()
    return jsonify(employee)


@app.route("/employees/<int:id>", methods=["DELETE"])
def delete_employee(id: int):
    global employees
    employee = get_employee(id)
    if employee is None:
        request_counter.labels(status_code="404", instance=platform.node()).inc()
        return jsonify({"error": "Employee does not exist."}), 404

    employees = [e for e in employees if e["id"] != id]

    request_counter.labels(status_code="200", instance=platform.node()).inc()
    return jsonify(employee), 200


if __name__ == "__main__":
    start_http_server(9000)
    app.run(port=5000)
