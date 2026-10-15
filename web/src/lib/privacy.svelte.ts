import { browser } from "$app/environment";

const STORAGE_KEY = "passada:hide-home";

const read = (): boolean => {
  if (!browser) return false;
  try {
    return localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
};

class PrivacySetting {
  hideHome = $state(read());

  toggle(value: boolean): void {
    this.hideHome = value;
    try {
      localStorage.setItem(STORAGE_KEY, value ? "1" : "0");
    } catch {
      return;
    }
  }
}

export const privacySetting = new PrivacySetting();
