import os
from flask import Flask, jsonify, request

app = Flask(__name__)


# Simulated data
class Event:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def to_dict(self):
        return {"id": self.id, "title": self.title}


# In-memory "database"
events = [
    Event(1, "Tech Meetup"),
    Event(2, "Python Workshop"),
]


def get_next_id():
    """Avoids ID reuse after deletions."""
    return max((e.id for e in events), default=0) + 1


def validate_title(data):
    if not data or "title" not in data:
        return None, ("Title is required", 400)
    title = data["title"]
    if not isinstance(title, str) or not title.strip():
        return None, ("Title must be a non-empty string", 400)
    return title.strip(), None


# Welcome route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Events API"})


# Get all events
@app.route("/events", methods=["GET"])
def get_events():
    return jsonify([event.to_dict() for event in events])


# Create a new event
@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)
    title, error = validate_title(data)
    if error:
        message, status = error
        return jsonify({"error": message}), status

    new_event = Event(get_next_id(), title)
    events.append(new_event)
    return jsonify(new_event.to_dict()), 201


# Update an existing event
@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    data = request.get_json(silent=True)
    title, error = validate_title(data)
    if error:
        message, status = error
        return jsonify({"error": message}), status

    for event in events:
        if event.id == event_id:
            event.title = title
            return jsonify(event.to_dict()), 200
    return jsonify({"error": "Event not found"}), 404


# Delete an event
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    for event in events:
        if event.id == event_id:
            events.remove(event)
            return jsonify({"message": "Event deleted successfully"}), 200
    return jsonify({"error": "Event not found"}), 404


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)