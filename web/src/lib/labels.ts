export const TRAINING_EFFECT: Record<string, string> = {
  RECOVERY: "Recuperação",
  AEROBIC_BASE: "Base aeróbica",
  TEMPO: "Ritmo",
  LACTATE_THRESHOLD: "Limiar",
  VO2MAX: "VO2max",
  ANAEROBIC_CAPACITY: "Anaeróbico",
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
  run: "Corrida",
  football: "Futebol",
  gym: "Academia",
  other: "Outro",
};

export const READINESS_LEVEL: Record<string, string> = {
  PRIME: "Excelente",
  HIGH: "Alta",
  MODERATE: "Moderada",
  LOW: "Baixa",
  POOR: "Muito baixa",
};

export const READINESS_FEEDBACK: Record<string, string> = {
  FOCUS_ON_ENERGY_LEVELS: "Cuide da energia hoje",
  FIND_TIME_TO_RELAX: "Encontre tempo para relaxar",
  READY_TO_TRAIN: "Pronto para treinar",
  RECOVER_WITH_EASY_ACTIVITY: "Recupere com algo leve",
  ENJOY_YOUR_DAY: "Aproveite o dia",
  RESTORE_WITH_SLEEP: "Recupere dormindo bem",
  TAKE_IT_EASY: "Pegue leve",
  GOOD_SLEEP_LAST_NIGHT_GO_TRAIN: "Dormiu bem: vá treinar",
  LET_YOUR_BODY_RECOVER: "Deixe o corpo se recuperar",
};

export const labelOf = (map: Record<string, string>, key: string | null | undefined): string =>
  key ? (map[key] ?? key.replaceAll("_", " ").toLowerCase()) : "—";
