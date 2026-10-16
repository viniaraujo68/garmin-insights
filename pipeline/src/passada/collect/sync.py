from datetime import date, timedelta

from garminconnect import Garmin

from passada import config
from passada.collect.client import RawStore

DAILY_ENDPOINTS = {
    "sleep": lambda client, day: client.get_sleep_data(day),
    "hrv": lambda client, day: client.get_hrv_data(day),
    "readiness": lambda client, day: client.get_training_readiness(day),
    "stats": lambda client, day: client.get_stats(day),
    "heart_rate": lambda client, day: client.get_heart_rates(day),
    "stress": lambda client, day: client.get_stress_data(day),
    "steps": lambda client, day: client.get_steps_data(day),
}


def days_between(start: date, end: date) -> list[date]:
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def last_synced_day(store: RawStore) -> date | None:
    daily = store.path("daily")
    if not daily.exists():
        return None
    days = sorted(entry.name for entry in daily.iterdir() if entry.is_dir())
    return date.fromisoformat(days[-1]) if days else None


def refresh_window_start(store: RawStore, today: date) -> date:
    last = last_synced_day(store)
    if last is None:
        return config.HISTORY_START
    return max(config.HISTORY_START, min(last, today) - timedelta(days=config.LOOKBACK_DAYS))


def collect_activities(client: Garmin, store: RawStore, window_start: date, today: date) -> int:
    listing = store.fetch(
        f"activities/list/{window_start}_{today}.json",
        lambda: client.get_activities_by_date(str(window_start), str(today)),
        refresh=True,
    ) or []
    for item in listing:
        activity_id = str(item["activityId"])
        type_key = item["activityType"]["typeKey"]
        recent = item["startTimeLocal"][:10] >= str(window_start)
        prefix = f"activities/{activity_id}"
        store.fetch(f"{prefix}/summary.json", lambda: client.get_activity(activity_id), refresh=recent)
        store.fetch(f"{prefix}/hr_zones.json", lambda: client.get_activity_hr_in_timezones(activity_id))
        store.fetch(f"{prefix}/details.json", lambda: client.get_activity_details(activity_id, maxchart=config.DETAIL_POINTS, maxpoly=0))
        if item.get("startLatitude") is not None:
            store.fetch(f"{prefix}/weather.json", lambda: client.get_activity_weather(activity_id))
        if type_key in config.RUNNING_TYPES:
            store.fetch(f"{prefix}/splits.json", lambda: client.get_activity_splits(activity_id))
        if type_key in config.STRENGTH_TYPES:
            store.fetch(f"{prefix}/exercise_sets.json", lambda: client.get_activity_exercise_sets(activity_id), refresh=recent)
    return len(listing)


def collect_daily(client: Garmin, store: RawStore, window_start: date, today: date) -> None:
    for day in days_between(config.HISTORY_START, today):
        refresh = day >= window_start
        for name, endpoint in DAILY_ENDPOINTS.items():
            store.fetch(f"daily/{day}/{name}.json", lambda: endpoint(client, str(day)), refresh=refresh)


def collect_ranges(client: Garmin, store: RawStore, today: date) -> None:
    start = str(config.HISTORY_START)
    end = str(today)
    store.fetch("ranges/max_metrics.json", lambda: client.connectapi(f"{client.garmin_connect_metrics_url}/{start}/{end}"), refresh=True)
    store.fetch("ranges/race_predictions.json", lambda: client.get_race_predictions(start, end, "daily"), refresh=True)
    store.fetch("ranges/weekly_intensity.json", lambda: client.get_weekly_intensity_minutes(start, end), refresh=True)
    store.fetch("ranges/training_status_weekly.json", lambda: client.connectapi(f"/mobile-gateway/usersummary/trainingstatus/weekly/{start}/{end}"), refresh=True)
    store.fetch("ranges/lactate_threshold.json", lambda: client.get_lactate_threshold(latest=False, start_date=start, end_date=end), refresh=True)
    chunk_start = config.HISTORY_START
    while chunk_start <= today:
        chunk_end = min(chunk_start + timedelta(days=config.RANGE_CHUNK_DAYS - 1), today)
        store.fetch(
            f"ranges/body_battery/{chunk_start}.json",
            lambda: client.get_body_battery(str(chunk_start), str(chunk_end)),
            refresh=chunk_end >= today - timedelta(days=config.LOOKBACK_DAYS),
        )
        chunk_start = chunk_end + timedelta(days=1)


def collect_profile(client: Garmin, store: RawStore, today: date) -> None:
    store.fetch("profile/personal_records.json", client.get_personal_record, refresh=True)
    store.fetch("profile/fitness_age.json", lambda: client.get_fitnessage_data(str(today)), refresh=True)
    store.fetch("profile/hr_zones.json", lambda: client.connectapi("/biometric-service/heartRateZones"), refresh=True)
    store.fetch("profile/training_status.json", lambda: client.get_training_status(str(today)), refresh=True)
    store.fetch("profile/devices.json", lambda: [
        {key: device.get(key) for key in ("productDisplayName", "deviceTypePk", "currentFirmwareVersion")}
        for device in client.get_devices()
    ], refresh=True)
    store.fetch("profile/gear.json", lambda: client.get_gear(client.get_user_profile()["id"]), refresh=True)


def collect(client: Garmin, store: RawStore, today: date) -> dict[str, int]:
    window_start = refresh_window_start(store, today)
    print(f"collect: refreshing {window_start} → {today}", flush=True)
    activities = collect_activities(client, store, window_start, today)
    collect_daily(client, store, window_start, today)
    collect_ranges(client, store, today)
    collect_profile(client, store, today)
    print(f"collect: {activities} activities in window, {store.counters}", flush=True)
    return store.counters
