# app.py
from flask import Flask, render_template, request, jsonify
import requests
from collections import Counter
from datetime import datetime

app = Flask(__name__)

# Example API source: AviationStack (Free Tier)
# Replace 'YOUR_API_KEY' with actual key if needed
API_URL = "http://api.aviationstack.com/v1/flights"
API_KEY = "b0d806afb9da286883d9f3b0636cf304"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/trends")
def get_trends():
    params = {
        'access_key': API_KEY,
        'limit': 100
    }
    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

        routes = []
        departure_cities = []
        arrival_cities = []
        airlines = []
        dates = []
        price_trends = {}

        for flight in data.get("data", []):
            dep_airport = flight.get("departure", {}).get("airport")
            arr_airport = flight.get("arrival", {}).get("airport")
            airline_name = flight.get("airline", {}).get("name")
            scheduled_time = flight.get("departure", {}).get("scheduled", "")[:10]

            if dep_airport and arr_airport:
                route = f"{dep_airport} → {arr_airport}"
                routes.append(route)
                departure_cities.append(dep_airport)
                arrival_cities.append(arr_airport)

                # Simulated price data: 100 to 500
                if route not in price_trends:
                    price_trends[route] = []
                price_trends[route].append(100 + hash(route + scheduled_time) % 400)

            if airline_name:
                airlines.append(airline_name)

            if scheduled_time:
                dates.append(scheduled_time)

        top_routes = Counter(routes).most_common(5)
        top_departures = Counter(departure_cities).most_common(5)
        top_arrivals = Counter(arrival_cities).most_common(5)
        top_airlines = Counter(airlines).most_common(5)
        top_dates = Counter(dates).most_common(5)

        # Prepare average price per top route
        avg_prices = [
            [route, round(sum(prices) / len(prices), 2)]
            for route, prices in price_trends.items()
            if route in dict(top_routes)
        ]

        return jsonify({
            "routes": top_routes,
            "departures": top_departures,
            "arrivals": top_arrivals,
            "airlines": top_airlines,
            "dates": top_dates,
            "avg_prices": avg_prices
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
