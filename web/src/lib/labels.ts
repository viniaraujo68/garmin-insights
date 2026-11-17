export const TRAINING_EFFECT: Record<string, string> = {
  RECOVERY: "Recovery",
  AEROBIC_BASE: "Aerobic Base",
  TEMPO: "Tempo",
  LACTATE_THRESHOLD: "Lactate Threshold",
  VO2MAX: "VO2max",
  ANAEROBIC_CAPACITY: "Anaerobic Capacity",
  SPRINT: "Sprint",
};

export const TRAINING_EFFECT_ORDER = [
  "RECOVERY",
  "AEROBIC_BASE",
  "TEMPO",
  "LACTATE_THRESHOLD",
  "VO2MAX",
  "ANAEROBIC_CAPACITY",
  "SPRINT",
];

export const SPORT: Record<string, string> = {
  run: "Run",
  football: "Football",
  gym: "Gym",
  other: "Other",
};

export const READINESS_LEVEL: Record<string, string> = {
  PRIME: "Prime",
  HIGH: "High",
  MODERATE: "Moderate",
  LOW: "Low",
  POOR: "Poor",
};

export const READINESS_FEEDBACK: Record<string, string> = {
  FOCUS_ON_ENERGY_LEVELS: "Focus on your energy levels today",
  FIND_TIME_TO_RELAX: "Find time to relax",
  READY_TO_TRAIN: "Ready to train",
  RECOVER_WITH_EASY_ACTIVITY: "Recover with easy activity",
  ENJOY_YOUR_DAY: "Enjoy your day",
  RESTORE_WITH_SLEEP: "Restore with sleep",
  TAKE_IT_EASY: "Take it easy",
  GOOD_SLEEP_LAST_NIGHT_GO_TRAIN: "Good sleep last night: go train",
  LET_YOUR_BODY_RECOVER: "Let your body recover",
  BOOSTED_BY_GOOD_SLEEP: "Boosted by good sleep",
  BOOSTED_BY_LIGHTER_TRAINING: "Boosted by lighter training",
  BOOSTED_BY_NAPPING: "Boosted by napping",
  ENERGIZED_BY_GOOD_SLEEP: "Energised by good sleep",
  EXCELLENT_RECOVERY: "Excellent recovery",
  GOOD_SLEEP_HISTORY: "Good sleep history",
  GOOD_SLEEP_LAST_NIGHT: "Good sleep last night",
  HIGH_RECOVERY_NEEDS: "High recovery needs",
  LOW_RECOVERY_NEEDS: "Low recovery needs",
  LISTEN_TO_YOUR_BODY: "Listen to your body",
  PRIMED_AND_READY: "Primed and ready",
  READY_FOR_ACTION: "Ready for action",
  READY_TO_GO: "Ready to go",
  RECOVERED_AND_READY: "Recovered and ready",
  RECOVERY_IN_PROGRESS: "Recovery in progress",
  RESTED_AND_READY: "Rested and ready",
  TIME_TO_SLOW_DOWN: "Time to slow down",
  WELL_RECOVERED: "Well recovered",
  WELL_RESTED: "Well rested",
  WELL_RESTED_AND_RECOVERED: "Rested and recovered",
};

export const labelOf = (map: Record<string, string>, key: string | null | undefined): string =>
  key ? (map[key] ?? key.replaceAll("_", " ").toLowerCase()) : "—";
