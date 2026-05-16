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
# TEAM INFO
# -----------------------------------

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
# ADMIN
# -----------------------------------

ADMIN_PASSWORD = "wk2026"


# -----------------------------------
# FIRST CAPTURES
# -----------------------------------

FIRST_CAPTURES = {
    "red": 0,
    "blue": 0,
    "green": 0,
    "yellow": 0,
    "pink": 0
}


# -----------------------------------
# POWERUPS
# -----------------------------------

POWERUP_LOCATIONS = [12, 26]


# -----------------------------------
# KAART GENEREREN
# -----------------------------------

def generate_map():

    locations = load_locations()

    m = folium.Map(
        location=[52.0907, 5.1214],
        zoom_start=15,
        tiles="CartoDB positron"
    )

    for loc in locations:

        image_path = f"/static/images/{loc['image']}"

        # safety
        if "first_captured_by" not in loc:
            loc["first_captured_by"] = None

        popup_html = f"""
        <div style="
            width:250px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14px;
            line-height: 1.4;
        ">

            <h3>{loc['name']}</h3>

            <img src="{image_path}"
                 width="220"
                 style="border-radius:10px">

            <p>
                <b>Info:</b><br>
                {loc['information']}
            </p>

            <p>
                <b>Veroverd door:</b>
                {TEAM_NAMES[loc['team']]}
            </p>

            <details style="margin-top:10px;">
                <summary style="cursor:pointer;">
                    Alleen voor coach Lars & Jelle
                </summary>

                <form action="/capture" method="POST">

                    <input type="hidden"
                           name="id"
                           value="{loc['id']}">

                    <input type="password"
                           name="password"
                           placeholder="Admin wachtwoord"
                           style="
                               width:95%;
                               margin-top:10px;
                               margin-bottom:8px;
                               padding:6px;
                           ">

                    <select name="team"
                            style="
                                width:100%;
                                margin-bottom:8px;
                                padding:6px;
                            ">

                        <option value="red">Turkije</option>
                        <option value="blue">Curaçao</option>
                        <option value="green">Zuid-Korea</option>
                        <option value="yellow">Oostenrijk</option>
                        <option value="pink">Engeland</option>
                        <option value="none">Reset</option>

                    </select>

                    <button type="submit"
                            style="
                                width:100%;
                                padding:8px;
                                cursor:pointer;
                            ">
                        Opslaan
                    </button>

                </form>
            </details>

        </div>
        """

        # -----------------------------------
        # VEROEVERD → VLAG MARKER
        # -----------------------------------

        if loc["team"] != "none":

            star_html = ""

            # powerup ster
            if loc["id"] in POWERUP_LOCATIONS:

                star_html = """
                <div style="
                    position:absolute;
                    top:-18px;
                    left:6px;
                    font-size:20px;
                    z-index:999;
                    text-shadow:0 0 8px gold;
                ">
                    ⭐
                </div>
                """

            icon_html = f"""
            <div style="
                position:relative;
                width:32px;
                height:32px;
            ">

                {star_html}

                <div style="
                    width:32px;
                    height:32px;
                    border-radius:40%;
                    overflow:hidden;
                    border:2px solid white;
                    box-shadow:0 0 6px rgba(0,0,0,0.4);
                ">
                    <img src='/{TEAM_ICONS[loc["team"]]}'
                         style='
                            width:100%;
                            height:100%;
                            object-fit:cover;
                         '>
                </div>

            </div>
            """

            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=loc["name"],
                icon=folium.DivIcon(html=icon_html)
            ).add_to(m)

        # -----------------------------------
        # NIET VEROEVERD
        # -----------------------------------

        else:

            # -----------------------------------
            # POWERUP OP NIET-VEROVERDE LOCATIES
            # -----------------------------------

            if loc["id"] in POWERUP_LOCATIONS:

                icon_html = """
                <div style="
                    position:relative;
                    width:32px;
                    height:32px;
                ">

                    <div style="
                        position:absolute;
                        top:-18px;
                        left:6px;
                        font-size:20px;
                        z-index:999;
                        text-shadow:0 0 8px gold;
                    ">
                        ⭐
                    </div>

                    <div style="
                        width:32px;
                        height:32px;
                        border-radius:50%;
                        background:#999;
                        border:2px solid white;
                        box-shadow:0 0 6px rgba(0,0,0,0.4);
                    ">
                    </div>

                </div>
                """

                folium.Marker(
                    location=[loc["lat"], loc["lon"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=loc["name"],
                    icon=folium.DivIcon(html=icon_html)
                ).add_to(m)

            # normale marker
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
# INDEX
# -----------------------------------

@app.route("/")
def index():

    locations = load_locations()

    scores = {
        "red": 0,
        "blue": 0,
        "green": 0,
        "yellow": 0,
        "pink": 0
    }

    for loc in locations:

        if loc["team"] in scores:
            scores[loc["team"]] += 1

    return render_template(
        "index.html",
        map_html=generate_map(),
        scores=scores,
        first_captures=FIRST_CAPTURES
    )


# -----------------------------------
# CAPTURE LOGICA
# -----------------------------------

@app.route("/capture", methods=["POST"])
def capture():

    global FIRST_CAPTURES

    loc_id = int(request.form["id"])
    new_team = request.form["team"]
    password = request.form["password"]

    # admin check
    if password != ADMIN_PASSWORD:
        return "Verkeerd admin wachtwoord"

    locations = load_locations()

    for loc in locations:

        if loc["id"] == loc_id:

            old_team = loc["team"]

            if "first_captured_by" not in loc:
                loc["first_captured_by"] = None

            # -----------------------------------
            # RESET
            # -----------------------------------

            if new_team == "none":

                owner = loc.get("first_captured_by")

                if owner in FIRST_CAPTURES:

                    FIRST_CAPTURES[owner] = max(
                        0,
                        FIRST_CAPTURES[owner] - 1
                    )

                loc["first_captured"] = False
                loc["first_captured_by"] = None

            # -----------------------------------
            # FIRST CAPTURE
            # -----------------------------------

            elif (
                old_team == "none"
                and not loc.get("first_captured", False)
            ):

                FIRST_CAPTURES[new_team] += 1

                loc["first_captured"] = True
                loc["first_captured_by"] = new_team

            # -----------------------------------
            # TEAM UPDATEN
            # -----------------------------------

            loc["team"] = new_team

    save_locations(locations)

    return redirect("/")


# -----------------------------------
# START SERVER
# -----------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)