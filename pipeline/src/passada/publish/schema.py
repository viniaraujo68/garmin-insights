import json

from passada import config
from passada.publish.contract import DOCUMENTS

SCHEMA_FILE = config.REPO_ROOT / "web" / "src" / "lib" / "data" / "schema.json"


def current_schema() -> str:
    schema = {name: model.model_json_schema() for name, model in DOCUMENTS.items()}
    return json.dumps(schema, indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> None:
    SCHEMA_FILE.write_text(current_schema())
    print(f"wrote {SCHEMA_FILE}")


if __name__ == "__main__":
    main()
