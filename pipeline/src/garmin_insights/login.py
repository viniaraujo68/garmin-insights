from getpass import getpass

from garminconnect import Garmin

from garmin_insights import config


def main() -> int:
    config.TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    email = input("Garmin Connect e-mail: ").strip()
    password = getpass("Garmin Connect password (hidden): ")
    client = Garmin(email=email, password=password, prompt_mfa=lambda: input("MFA code (e-mail or SMS): ").strip())
    client.login(str(config.TOKEN_DIR))
    print(f"logged in as {client.get_full_name()}; tokens saved in {config.TOKEN_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
