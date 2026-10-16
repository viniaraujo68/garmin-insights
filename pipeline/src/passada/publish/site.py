import json
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path

from pydantic import BaseModel, TypeAdapter

from passada import config
from passada.calc.activities import activity_details, activity_summaries, routes_document, samples_by_activity
from passada.calc.load import load_document
from passada.calc.performance import performance_document
from passada.calc.recovery import recovery_document, sleep_nights
from passada.calc.sports import sports_document
from passada.calc.today import day_documents
from passada.publish.contract import DOCUMENTS, Contract, Meta


def open_database(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def write_document(site_dir: Path, name: str, payload: Contract | list[Contract]) -> None:
    target = site_dir / f"{name}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, list):
        target.write_text(json.dumps([item.model_dump(mode="json") for item in payload], ensure_ascii=False, separators=(",", ":")))
    else:
        target.write_text(payload.model_dump_json())


def build_meta(connection: sqlite3.Connection, today: date, activity_count: int) -> Meta:
    first_day, last_day = connection.execute("SELECT min(date), max(date) FROM daily").fetchone()
    last_activity = connection.execute("SELECT max(date) FROM activities").fetchone()[0]
    device = connection.execute("SELECT value FROM profile WHERE key = 'device'").fetchone()
    return Meta(
        generated_at=datetime.now(config.TIMEZONE).isoformat(timespec="seconds"),
        today=str(today),
        first_day=first_day,
        last_day=last_day,
        last_activity_date=last_activity,
        activity_count=activity_count,
        device=json.loads(device[0]) if device and device[0] else None,
        days=[row[0] for row in connection.execute("SELECT date FROM daily ORDER BY date")],
    )


def document_names(site_dir: Path) -> set[str]:
    return {path.relative_to(site_dir).with_suffix("").as_posix() for path in site_dir.rglob("*.json") if path.name != "schema.json"}


def model_for(name: str) -> type[Contract]:
    return DOCUMENTS[name.split("/")[0]]


def verify_site(site_dir: Path) -> None:
    for name in sorted(document_names(site_dir)):
        model = model_for(name)
        text = (site_dir / f"{name}.json").read_text()
        if text.lstrip().startswith("["):
            TypeAdapter(list[model]).validate_json(text)
        else:
            model.model_validate_json(text)
    meta = Meta.model_validate_json((site_dir / "meta.json").read_text())
    activities = json.loads((site_dir / "activities.json").read_text())
    if meta.activity_count != len(activities):
        raise ValueError(f"meta.activity_count={meta.activity_count} but activities.json has {len(activities)}")
    missing = [item["activity_id"] for item in activities if not (site_dir / "activity" / f"{item['activity_id']}.json").exists()]
    if missing:
        raise ValueError(f"activities without a detail file: {missing}")
    missing_days = [day for day in meta.days if not (site_dir / "day" / f"{day}.json").exists()]
    if missing_days:
        raise ValueError(f"days without a briefing file: {missing_days}")
    if (site_dir / "recovery.json").exists():
        nights = json.loads((site_dir / "recovery.json").read_text())["nights"]
        lost = [night["date"] for night in nights if not (site_dir / "sleep" / f"{night['date']}.json").exists()]
        if lost:
            raise ValueError(f"nights without a sleep file: {lost}")


def write_schema(site_dir: Path) -> None:
    schema = {name: model.model_json_schema() for name, model in DOCUMENTS.items()}
    (site_dir / "schema.json").write_text(json.dumps(schema, indent=1, ensure_ascii=False))


def publish_site(db_path: Path, site_dir: Path, today: date) -> dict[str, int]:
    staging = site_dir.with_name(site_dir.name + ".part")
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    connection = open_database(db_path)
    try:
        samples = samples_by_activity(connection)
        activities = activity_summaries(connection, samples)
        documents: dict[str, BaseModel | list] = {
            "meta": build_meta(connection, today, len(activities)),
            "activities": activities,
            "routes": routes_document(activities, samples),
            "performance": performance_document(connection, activities, today),
            "load": load_document(connection, activities, today),
            "recovery": recovery_document(connection),
            "sports": sports_document(connection, activities, samples, today),
        }
        for activity_id, detail in activity_details(connection, activities, samples).items():
            documents[f"activity/{activity_id}"] = detail
        for day, briefing in day_documents(connection, activities).items():
            documents[f"day/{day}"] = briefing
        for night_date, night in sleep_nights(connection).items():
            documents[f"sleep/{night_date}"] = night
    finally:
        connection.close()
    for name, payload in documents.items():
        write_document(staging, name, payload)
    write_schema(staging)
    verify_site(staging)
    shutil.rmtree(site_dir, ignore_errors=True)
    staging.replace(site_dir)
    counts: dict[str, int] = {}
    for name, payload in documents.items():
        key = name.split("/")[0]
        counts[key] = counts.get(key, 0) + (len(payload) if isinstance(payload, list) else 1)
    return counts
