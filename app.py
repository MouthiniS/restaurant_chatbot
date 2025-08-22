from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Temporary session storage (per single user for demo)
user_state = {
    "name": None,
    "step": None,
    "booking_type": None
}

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json.get("message").lower()
    response = ""

    # Helper: extract number from message
    def extract_number(text):
        numbers = re.findall(r"\d+", text)
        return int(numbers[0]) if numbers else None

    # 1. Ask for name first
    if user_state["name"] is None:
        if "i am" in user_message or "my name is" in user_message:
            user_state["name"] = user_message.split()[-1].capitalize()
            response = f"Hello {user_state['name']}! 🎉 You can ask about Menu, Events, or Bookings."
        else:
            response = "👋 Hi! What's your name?"
        return jsonify({"response": response})

    # 2. Handle booking flow
    if "booking" in user_message:
        user_state["step"] = "choose_booking"
        response = "Would you like to book a Table 🍽️ or a Room 🏨?"
        return jsonify({"response": response})

    # Choosing booking type
    if user_state["step"] == "choose_booking":
        if "table" in user_message:
            user_state["booking_type"] = "table"
            user_state["step"] = "table_people"
            response = "How many people are you booking the table for?"
        elif "room" in user_message:
            user_state["booking_type"] = "room"
            user_state["step"] = "room_count"
            response = "How many rooms would you like to book?"
        else:
            response = "Please type either 'Table' 🍽️ or 'Room' 🏨."
        return jsonify({"response": response})

    # Table booking flow
    if user_state["step"] == "table_people":
        people = extract_number(user_message)
        if people:
            response = f"✅ Table booking confirmed for {people} people! 🎉 Your Table No: T{people+10}"
            user_state["step"] = None
            user_state["booking_type"] = None
        else:
            response = "Please enter a valid number of people."
        return jsonify({"response": response})

    # Room booking flow - number of rooms
    if user_state["step"] == "room_count":
        rooms = extract_number(user_message)
        if rooms:
            user_state["rooms"] = rooms
            user_state["step"] = "room_days"
            response = f"Great! For how many days do you want to book {rooms} room(s)?"
        else:
            response = "Please enter a valid number of rooms."
        return jsonify({"response": response})

    # Room booking flow - number of days
    if user_state["step"] == "room_days":
        days = extract_number(user_message)
        if days:
            rooms = user_state.get("rooms", 1)
            response = f"✅ Room booking confirmed! 🎉 {rooms} room(s) booked for {days} day(s). Room No: R{rooms*5}"
            user_state["step"] = None
            user_state["booking_type"] = None
            user_state.pop("rooms", None)
        else:
            response = "Please enter a valid number of days."
        return jsonify({"response": response})

    # Menu and Events
    if "menu" in user_message:
        response = "📖 Today's Menu:\n1. Pizza\n2. Pasta\n3. Burger\n4. Salad"
    elif "event" in user_message:
        response = "🎶 Upcoming Event: Live Music Night on Saturday!"
    elif "thank" in user_message:
        response = "🙏 You're welcome!"
    elif "hi" in user_message or "hello" in user_message:
        response = f"Hello {user_state['name']}! 👋 You can ask about Menu, Events, or Bookings."
    else:
        response = "❓ Sorry, I didn’t understand. Please ask about Menu, Events, or Bookings."

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
