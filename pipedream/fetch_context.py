def handler(pd: "pipedream"):
    import os
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import requests

    auth_key = next((key for key in pd.inputs if "spotify" in key.casefold()), None)
    if not auth_key:
        return {"ok": False, "error": "spotify_account_not_connected"}
    token = pd.inputs[auth_key]["$auth"]["oauth_access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    playback = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers=headers,
        timeout=10,
    )
    if playback.status_code == 204 or not playback.content:
        return {"ok": True, "playing": False, "message": "nothing_playing"}
    playback.raise_for_status()
    item = playback.json().get("item") or {}
    track_id = item.get("id")
    if not track_id:
        return {"ok": True, "playing": False, "message": "unsupported_playback_item"}

    features = requests.get(
        f"https://api.spotify.com/v1/audio-features/{track_id}",
        headers=headers,
        timeout=10,
    )
    feature_data = features.json() if features.ok else {}

    weather_key = os.environ["OPENWEATHER_API_KEY"]
    weather = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": 25.0330, "lon": 121.5654, "appid": weather_key, "units": "metric"},
        timeout=10,
    )
    weather.raise_for_status()
    weather_data = weather.json()

    artists = item.get("artists") or [{}]
    return {
        "ok": True,
        "playing": True,
        "timestamp": datetime.now(ZoneInfo("Asia/Taipei")).isoformat(),
        "song": item.get("name", "Unknown"),
        "artist": artists[0].get("name", "Unknown"),
        "valence": feature_data.get("valence", 0.5),
        "energy": feature_data.get("energy", 0.5),
        "danceability": feature_data.get("danceability"),
        "acousticness": feature_data.get("acousticness"),
        "tempo": feature_data.get("tempo"),
        "feature_status": "ok" if features.ok else f"unavailable_{features.status_code}",
        "Weather_Temp": weather_data.get("main", {}).get("temp"),
        "Weather_Main": (weather_data.get("weather") or [{}])[0].get("main"),
        "Weather_Humid": weather_data.get("main", {}).get("humidity"),
    }

