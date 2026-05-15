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
    "yellow": "orange",
    "pink": "pink"
}

TEAM_NAMES = {
    "red": "Turkije",
    "blue": "Curaçao",
    "green": "Zuid-Korea",
    "yellow": "Oostenrijk",
    "pink": "Engeland",
    "none": "Niemand"
}

TEAM_ICONS = {
    "red": "static/icons/turkey.jpg",
    "blue": "static/icons/curacao.jpg",
    "green": "static/icons/korea.jpg",
    "yellow": "static/icons/austria.jpg",
    "pink": "static/icons/england.jpg"
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

        image_path = f"/static/images/{loc['image']}"

        popup_html = f"""
        <div style="width:250px">
            <h3>{loc['name']}</h3>

            <img src="{image_path}"
                 width="220"
                 style="border-radius:10px">

            <p>
                <b>Info:</b><br>
                {loc['information']}
            </p>

            <p>
                <b>Verovert door:</b> {TEAM_NAMES[loc['team']]}
            </p>

            <form action="/capture" method="POST">

                <input type="hidden"
                       name="id"
                       value="{loc['id']}">

                <select name="team">
                    <option value="red">Turkije</option>
                    <option value="blue">Curaçao</option>
                    <option value="green">Zuid-Korea</option>
                    <option value="yellow">Oostenrijk</option>
                    <option value="pink">Engeland</option>
                    <option value="none">Nog niet veroverd</option>
                </select>

                <button type="submit">
                    Verover
                </button>

            </form>
        </div>
        """

        # -----------------------------------
        # VEROEVERDE LOCATIE → VLAG MARKER
        # -----------------------------------

        if loc["team"] != "none":

            icon_html = f"""
            <div style="
                width:32px;
                height:32px;
                border-radius:40%;
                overflow:hidden;
                border:2px solid white;
                box-shadow:0 0 6px rgba(0,0,0,0.4);
            ">
                <img src='/{TEAM_ICONS[loc["team"]]}'
                     style='width:100%; height:100%; object-fit:cover;'>
            </div>
            """

            custom_icon = folium.DivIcon(
                html=icon_html
            )

            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=loc["name"],
                icon=custom_icon
            ).add_to(m)

        # -----------------------------------
        # NIET VEROEVERD → GRIJZE MARKER
        # -----------------------------------

        else:

            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=loc["name"],
                icon=folium.Icon(
                    color="gray",
                    icon="info-sign"
                )
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
        "yellow": 0,
        "pink": 0
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
    app.run(host="0.0.0.0", port=5000, debug=True)