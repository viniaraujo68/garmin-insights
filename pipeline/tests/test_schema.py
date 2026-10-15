from passada.publish.schema import SCHEMA_FILE, current_schema


def test_web_schema_matches_the_contract():
    assert SCHEMA_FILE.read_text() == current_schema(), (
        "web/src/lib/data/schema.json is stale: run `uv run --frozen python -m passada.publish.schema` "
        "then `npm run types` in web/"
    )
