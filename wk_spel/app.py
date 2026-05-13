from flask import Flask, render_template, request, redirect
import folium
import json
import os

app = Flask(__name__)

LOCATION_FILE = "locations.json"


# -----------------------------------
# DATA LADEN
# -----------------------------------

def load_locations():
    with open(LOCATION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_locations(data):
    with open(LOCATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# -----------------------------------
# TEAM KLEUREN
# -----------------------------------

TEAM_COLORS = {
    "none": "gray",
    "red": "red",
    "blue": "blue",
    "green": "green",
    "yellow": "orange"
}


# -----------------------------------
# KAART GENEREREN
# -----------------------------------

def generate_map():

    locations = load_locations()

    # Utrecht centrum
    m = folium.Map(
        location=[52.0907, 5.1214],
        zoom_start=15,
        tiles="CartoDB positron"
    )

    # Marker toevoegen
    for loc in locations:

        color = TEAM_COLORS.get(loc["team"], "gray")

        image_path = f"/static/images/{loc['image']}"

        popup_html = f"""
        <div style="width:250px">
            <h3>{loc['name']}</h3>

            <img src="{image_path}"
                 width="220"
                 style="border-radius:10px">

            <p>
                <b>Opdracht:</b><br>
                {loc['challenge']}
            </p>

            <p>
                <b>Bezit:</b> {loc['team']}
            </p>

            <form action="/capture" method="POST">

                <input type="hidden"
                       name="id"
                       value="{loc['id']}">

                <select name="team">
                    <option value="red">Rood</option>
                    <option value="blue">Blauw</option>
                    <option value="green">Groen</option>
                    <option value="yellow">Geel</option>
                    <option value="none">Reset</option>
                </select>

                <button type="submit">
                    Verover
                </button>

            </form>
        </div>
        """

        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=loc["name"],
            icon=folium.Icon(color=color, icon="flag")
        ).add_to(m)

    return m._repr_html_()


# -----------------------------------
# HOOFDPAGINA
# -----------------------------------

@app.route("/")
def index():

    locations = load_locations()

    # Scores berekenen
    scores = {
        "red": 0,
        "blue": 0,
        "green": 0,
        "yellow": 0
    }

    for loc in locations:
        team = loc["team"]

        if team in scores:
            scores[team] += 1

    map_html = generate_map()

    return render_template(
        "index.html",
        map_html=map_html,
        scores=scores
    )


# -----------------------------------
# LOCATIE VEROVEREN
# -----------------------------------

@app.route("/capture", methods=["POST"])
def capture():

    loc_id = int(request.form["id"])
    new_team = request.form["team"]

    locations = load_locations()

    for loc in locations:
        if loc["id"] == loc_id:
            loc["team"] = new_team

    save_locations(locations)

    return redirect("/")


# -----------------------------------
# START SERVER
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)