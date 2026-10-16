export const icons: Record<string, string[]> = {
  today: [
    "M12 3v2",
    "M12 19v2",
    "M5.6 5.6l1.4 1.4",
    "M17 17l1.4 1.4",
    "M3 12h2",
    "M19 12h2",
    "M5.6 18.4 7 17",
    "M17 7l1.4-1.4",
    "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z",
  ],
  runs: [
    "M13 4a1.5 1.5 0 1 0 3 0 1.5 1.5 0 0 0-3 0",
    "M7 21l3-6 3 2v5",
    "M10 15l1-5 4 2 3-1",
    "M11 10 8 9l-3 3",
  ],
  trend: ["M3 17l6-6 4 4 8-8", "M15 7h6v6"],
  load: ["M4 20V10", "M10 20V4", "M16 20v-7", "M22 20H2"],
  recovery: [
    "M12 21s-7-4.5-9-9.5C1.6 7.8 4 4.5 7.5 4.5c2 0 3.4 1 4.5 2.5 1.1-1.5 2.5-2.5 4.5-2.5 3.5 0 5.9 3.3 4.5 7-2 5-9 9.5-9 9.5Z",
    "M7 12h3l1.5-2.5 2 5L15 12h2",
  ],
  map: ["M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z", "M9 4v14", "M15 6v14"],
};

export const iconPaths = (name: string | undefined): string[] =>
  name === undefined ? [] : (icons[name] ?? []);
