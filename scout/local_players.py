# local_players.py

import random

POSITION_MAP = {
    "Forward": "F",
    "Midfielder": "M",
    "Defender": "D",
    "Goalkeeper": "G",
}

POSITION_LABELS = {
    "F": "Forward",
    "M": "Midfielder",
    "D": "Defender",
    "G": "Goalkeeper",
}

LEAGUES = [
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1",
]

TEAMS = [
    "Manchester City",
    "Arsenal",
    "Liverpool",
    "Chelsea",
    "Manchester United",
    "Real Madrid",
    "Barcelona",
    "Atletico Madrid",
    "Bayern Munich",
    "Borussia Dortmund",
    "PSG",
    "Marseille",
    "Inter Milan",
    "AC Milan",
    "Juventus",
    "Napoli",
]

NATIONALITIES = [
    "England",
    "France",
    "Brazil",
    "Spain",
    "Germany",
    "Portugal",
    "Argentina",
    "Norway",
    "Netherlands",
    "Belgium",
    "Italy",
    "Morocco",
]

PLAYERS = [
    {
        "id": 1,
        "name": "Erling Haaland",
        "position": "F",
        "team": "Manchester City",
        "league": "Premier League",
        "nationality": "Norway",
        "age": 24,
        "market_value": 180000000,
        "photo": "https://media.api-sports.io/football/players/1100.png",
        "goals": 32,
        "assists": 6,
        "appearances": 35,
        "rating": 8.4,
        "pace": 89,
        "shooting": 94,
        "passing": 76,
        "dribbling": 84,
        "defending": 42,
        "physical": 91,
    },

    {
        "id": 2,
        "name": "Kylian Mbappe",
        "position": "F",
        "team": "Real Madrid",
        "league": "La Liga",
        "nationality": "France",
        "age": 26,
        "market_value": 175000000,
        "photo": "https://media.api-sports.io/football/players/278.png",
        "goals": 29,
        "assists": 9,
        "appearances": 33,
        "rating": 8.3,
        "pace": 97,
        "shooting": 91,
        "passing": 80,
        "dribbling": 93,
        "defending": 39,
        "physical": 82,
    },

    {
        "id": 3,
        "name": "Jude Bellingham",
        "position": "M",
        "team": "Real Madrid",
        "league": "La Liga",
        "nationality": "England",
        "age": 21,
        "market_value": 150000000,
        "photo": "https://media.api-sports.io/football/players/284352.png",
        "goals": 18,
        "assists": 11,
        "appearances": 34,
        "rating": 8.1,
        "pace": 81,
        "shooting": 84,
        "passing": 87,
        "dribbling": 88,
        "defending": 78,
        "physical": 85,
    },

    {
        "id": 4,
        "name": "Vinicius Junior",
        "position": "F",
        "team": "Real Madrid",
        "league": "La Liga",
        "nationality": "Brazil",
        "age": 24,
        "market_value": 170000000,
        "photo": "https://media.api-sports.io/football/players/188545.png",
        "goals": 21,
        "assists": 13,
        "appearances": 31,
        "rating": 8.2,
        "pace": 95,
        "shooting": 85,
        "passing": 79,
        "dribbling": 94,
        "defending": 35,
        "physical": 76,
    },

    {
        "id": 5,
        "name": "Bukayo Saka",
        "position": "F",
        "team": "Arsenal",
        "league": "Premier League",
        "nationality": "England",
        "age": 23,
        "market_value": 140000000,
        "photo": "https://media.api-sports.io/football/players/1460.png",
        "goals": 19,
        "assists": 14,
        "appearances": 36,
        "rating": 8.0,
        "pace": 88,
        "shooting": 84,
        "passing": 82,
        "dribbling": 89,
        "defending": 58,
        "physical": 75,
    },
]

_fake_names = [
    "Liam Carter",
    "Noah Hughes",
    "Ethan Walker",
    "Mason Turner",
    "Lucas Bell",
    "Oscar Reed",
    "Leo Ward",
    "Finn Brooks",
    "Theo Price",
    "Jack Cooper",
    "Nico Silva",
    "Marco Rossi",
    "Ivan Petrov",
    "Alex Morgan",
    "Daniel Costa",
    "Youssef El Amrani",
    "Sergio Lopez",
    "Pedro Gomes",
    "Hugo Martin",
    "Rayan Amine",
    "Adam Khan",
    "Bilal Rahimi",
    "Omar Farah",
    "Samir Haddad",
    "Karim Idrissi",
    "Elian Novak",
    "Milo Jensen",
    "Tobias Schmidt",
    "Enzo Laurent",
    "Ruben Dias",
    "Amir Benali",
    "Nabil Ait",
    "Zayd El Fassi",
    "Ayman Saadi",
    "Hamza Bouziane",
    "Aurelien Dubois",
    "Julian Meyer",
    "Marek Kowalski",
    "Andrei Popescu",
    "Dario Bianchi",
    "Ciro Ferri",
    "Tommy Clark",
    "Ryan Murphy",
    "Nathan Scott",
    "Ben Thomas",
    "Chris Evans",
    "Jake Allen",
    "Tyler Young",
    "Martin Fischer",
    "Sebastian Weber",
]

_fake_positions = ["F", "M", "D", "G"]

for i in range(6, 101):

    idx = i - 6

    position = _fake_positions[idx % len(_fake_positions)]

    # =========================================
    # REALISTIC STATS
    # =========================================

    if position == "F":

        goals = 10 + (idx % 25)
        assists = 3 + (idx % 12)

    elif position == "M":

        goals = 4 + (idx % 12)
        assists = 5 + (idx % 14)

    elif position == "D":

        goals = idx % 6
        assists = idx % 5

    else:

        goals = 0
        assists = idx % 2

    PLAYERS.append(
        {
            "id": i,
            "name": _fake_names[idx % len(_fake_names)],
            "position": position,
            "team": TEAMS[idx % len(TEAMS)],
            "league": LEAGUES[idx % len(LEAGUES)],
            "nationality": NATIONALITIES[idx % len(NATIONALITIES)],
            "age": 18 + (idx % 17),
            "market_value": (5 + (idx % 120)) * 1000000,
            "photo": "https://via.placeholder.com/150",

            "goals": goals,
            "assists": assists,

            "appearances": 15 + (idx % 24),
            "rating": round(6.0 + ((idx % 30) / 10), 1),

            "pace": 60 + (idx % 40),
            "shooting": 55 + (idx % 40),
            "passing": 58 + (idx % 40),
            "dribbling": 57 + (idx % 40),
            "defending": 50 + (idx % 40),
            "physical": 60 + (idx % 35),
        }
    )


# =========================================================
# HELPERS
# =========================================================

def format_market_value(value):

    if not value:
        return "N/A"

    if value >= 1_000_000:
        return f"€{value / 1_000_000:.1f}M"

    if value >= 1_000:
        return f"€{value / 1_000:.0f}K"

    return f"€{value}"


# =========================================================
# ENRICH PLAYER
# =========================================================

def enrich_player(player):

    player["market_value_fmt"] = format_market_value(
        player.get("market_value")
    )

    player["position_label"] = POSITION_LABELS.get(
        player.get("position", ""),
        player.get("position", "")
    )

    # =========================================
    # POSITION-BASED RADAR ATTRIBUTES
    # =========================================

    position = player.get("position")

    if position == "F":

        player["attributes"] = {

            "attacking": 85 + (player["id"] % 12),

            "technical": 75 + (player["id"] % 10),

            "tactical": 65 + (player["id"] % 10),

            "defending": 30 + (player["id"] % 15),

            "creativity": 78 + (player["id"] % 12),
        }

    elif position == "M":

        player["attributes"] = {

            "attacking": 68 + (player["id"] % 10),

            "technical": 82 + (player["id"] % 12),

            "tactical": 80 + (player["id"] % 10),

            "defending": 60 + (player["id"] % 12),

            "creativity": 84 + (player["id"] % 10),
        }

    elif position == "D":

        player["attributes"] = {

            "attacking": 35 + (player["id"] % 10),

            "technical": 62 + (player["id"] % 10),

            "tactical": 85 + (player["id"] % 10),

            "defending": 88 + (player["id"] % 10),

            "creativity": 52 + (player["id"] % 10),
        }

    else:  # Goalkeeper

        player["attributes"] = {

            "attacking": 10,

            "technical": 45 + (player["id"] % 10),

            "tactical": 82 + (player["id"] % 10),

            "defending": 92 + (player["id"] % 8),

            "creativity": 35 + (player["id"] % 10),
        }

    # =========================================
    # EXTRA DATA
    # =========================================

    player["availability"] = (
        "injured"
        if player["id"] % 7 == 0
        else "available"
    )

    player["preferred_foot"] = (
        "Left"
        if player["id"] % 5 == 0
        else "Right"
    )

    player["height"] = player.get(
        "height",
        175 + (player["id"] % 20)
    )

    player["contract_until"] = str(
        2026 + (player["id"] % 4)
    )

    player["transfers"] = [
        {
            "transfer_date": "2023-07-01",
            "from_team_name": "Old Club",
            "to_team_name": player["team"],
            "fee_description": f"€{20 + (player['id'] % 50)}M",
            "fee": (20 + (player["id"] % 50)) * 1000000,
        }
    ]

    strengths_pool = [
        "Pace",
        "Passing",
        "Vision",
        "Dribbling",
        "Finishing",
        "Crossing",
        "Leadership",
        "Tackling",
    ]

    weaknesses_pool = [
        "Heading",
        "Positioning",
        "Weak Foot",
        "Discipline",
        "Stamina",
    ]

    player["strengths"] = [
        strengths_pool[player["id"] % len(strengths_pool)],
        strengths_pool[(player["id"] + 2) % len(strengths_pool)],
    ]

    player["weaknesses"] = [
        weaknesses_pool[player["id"] % len(weaknesses_pool)]
    ]

    player["specific_position"] = {
        "F": "ST",
        "M": "CM",
        "D": "CB",
        "G": "GK",
    }.get(player["position"], "ST")

    player["current_team"] = {
        "name": player["team"]
    }

    return player


# =========================================================
# LEAGUES
# =========================================================

def get_leagues():

    return [
        {"id": 1, "name": "Premier League"},
        {"id": 2, "name": "La Liga"},
        {"id": 3, "name": "Serie A"},
        {"id": 4, "name": "Bundesliga"},
        {"id": 5, "name": "Ligue 1"},
    ]


# =========================================================
# GET PLAYERS
# =========================================================

def get_players(
    position=None,
    league_id=None,
    search=None,
    page=1,
    page_size=20
):

    players = PLAYERS.copy()

    if position:

        if position in POSITION_MAP:
            position = POSITION_MAP[position]

        players = [
            p for p in players
            if p["position"] == position
        ]

    if search:

        players = [
            p for p in players
            if search.lower() in p["name"].lower()
        ]

    for p in players:
        enrich_player(p)

    total = len(players)

    start = (page - 1) * page_size
    end = start + page_size

    paginated = players[start:end]

    return {
        "players": paginated,
        "count": total,
        "next": page + 1 if end < total else None,
        "previous": page - 1 if page > 1 else None,
    }


# =========================================================
# PROFILE
# =========================================================

def get_player_profile(player_id):

    for player in PLAYERS:

        if player["id"] == int(player_id):

            enrich_player(player)

            return player

    return None


# =========================================================
# SEARCH
# =========================================================

def search_players(query, page_size=20):

    players = [
        p for p in PLAYERS
        if query.lower() in p["name"].lower()
    ]

    for p in players:
        enrich_player(p)

    return {
        "players": players[:page_size],
        "count": len(players),
    }


# =========================================================
# STATS
# =========================================================

def get_player_stats(player_id):

    player = get_player_profile(player_id)

    if not player:
        return {}

    appearances = player["appearances"]

    shots_total = player["goals"] * 3 + 12
    shots_on = player["goals"] * 2

    key_passes = player["assists"] * 3

    dribbles = (
        player["dribbling"] // 2
    ) * appearances // 10

    dribbles_success = int(dribbles * 0.7)

    duels_total = appearances * 6

    duels_won = int(
        duels_total * (
            player["physical"] / 100
        )
    )

    tackles = (
        player["defending"] // 4
    ) * appearances // 10

    interceptions = tackles // 2

    minutes = appearances * 82

    yellow_cards = appearances // 7

    red_cards = 1 if player["position"] == "D" else 0

    return {

        "player": {
            "name": player["name"],
            "photo": player["photo"],
            "age": player["age"],
            "nationality": player["nationality"],
        },

        "statistics": [

            {
                "team": {
                    "name": player["team"]
                },

                "league": {
                    "name": player["league"]
                },

                "games": {
                    "appearences": appearances,
                    "rating": player["rating"],
                    "minutes": minutes,
                },

                "goals": {
                    "total": player["goals"],
                    "assists": player["assists"],
                },

                "shots": {
                    "total": shots_total,
                    "on": shots_on,
                },

                "passes": {
                    "key": key_passes,
                },

                "dribbles": {
                    "attempts": dribbles,
                    "success": dribbles_success,
                },

                "duels": {
                    "total": duels_total,
                    "won": duels_won,
                },

                "tackles": {
                    "total": tackles,
                    "interceptions": interceptions,
                },

                "cards": {
                    "yellow": yellow_cards,
                    "red": red_cards,
                },
            }
        ]
    }


def format_player_stats(player_data):

    if not player_data:
        return {}

    player = player_data["player"]

    stats = player_data["statistics"][0]

    shots_total = stats["shots"]["total"]
    shots_on = stats["shots"]["on"]

    duels_total = stats["duels"]["total"]
    duels_won = stats["duels"]["won"]

    dribbles_attempts = stats["dribbles"]["attempts"]
    dribbles_success = stats["dribbles"]["success"]

    return {

        "name": player["name"],
        "photo": player["photo"],
        "age": player["age"],
        "nationality": player["nationality"],

        "goals": stats["goals"]["total"],
        "assists": stats["goals"]["assists"],

        "appearances": stats["games"]["appearences"],

        "avg_rating": stats["games"]["rating"],

        "minutes": stats["games"]["minutes"],

        "shots_total": shots_total,
        "shots_on": shots_on,

        "passes_key": stats["passes"]["key"],

        "dribbles_attempts": dribbles_attempts,

        "dribbles_pct": round(
            (dribbles_success / dribbles_attempts) * 100,
            1
        ) if dribbles_attempts else 0,

        "duels_won": duels_won,

        "duels_won_pct": round(
            (duels_won / duels_total) * 100,
            1
        ) if duels_total else 0,

        "tackles": stats["tackles"]["total"],

        "interceptions": stats["tackles"]["interceptions"],

        "yellow_cards": stats["cards"]["yellow"],

        "red_cards": stats["cards"]["red"],

        "team": stats["team"]["name"],

        "league": stats["league"]["name"],
    }


# =========================================================
# MATCH STATS
# =========================================================

def get_player_match_stats(player_id, max_matches=10):

    player = get_player_profile(player_id)

    if not player:
        return {}

    return {
        "appearances": player["appearances"],
        "goals": player["goals"],
        "yellow_cards": player["appearances"] // 7,
        "red_cards": 1 if player["position"] == "D" else 0,
        "clean_sheets": (
            player["appearances"] // 3
            if player["position"] == "G"
            else 0
        ),
        "avg_rating": player["rating"],

        "recent_matches": [
            {
                "home_team": player["team"],
                "away_team": random.choice(TEAMS),
                "home_score": 2,
                "away_score": 1,
                "rating": player["rating"],
                "goals": 1 if i < player["goals"] else 0,
                "league": 'Super League',
                "date": f"2025-05-{10+i}",
            }

            for i in range(5)
        ]
    }
