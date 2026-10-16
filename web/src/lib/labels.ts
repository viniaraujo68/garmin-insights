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
  BOOSTED_BY_GOOD_SLEEP: "Impulsionado por um bom sono",
  BOOSTED_BY_LIGHTER_TRAINING: "Impulsionado por treinos mais leves",
  BOOSTED_BY_NAPPING: "Impulsionado pelo cochilo",
  ENERGIZED_BY_GOOD_SLEEP: "Energizado por um bom sono",
  EXCELLENT_RECOVERY: "Recuperação excelente",
  GOOD_SLEEP_HISTORY: "Bom histórico de sono",
  GOOD_SLEEP_LAST_NIGHT: "Dormiu bem esta noite",
  HIGH_RECOVERY_NEEDS: "Precisa de bastante recuperação",
  LOW_RECOVERY_NEEDS: "Pouca recuperação pendente",
  LISTEN_TO_YOUR_BODY: "Escute o seu corpo",
  PRIMED_AND_READY: "Preparado e pronto",
  READY_FOR_ACTION: "Pronto para a ação",
  READY_TO_GO: "Pronto para ir",
  RECOVERED_AND_READY: "Recuperado e pronto",
  RECOVERY_IN_PROGRESS: "Recuperação em andamento",
  RESTED_AND_READY: "Descansado e pronto",
  TIME_TO_SLOW_DOWN: "Hora de desacelerar",
  WELL_RECOVERED: "Bem recuperado",
  WELL_RESTED: "Bem descansado",
  WELL_RESTED_AND_RECOVERED: "Descansado e recuperado",
};

export const labelOf = (map: Record<string, string>, key: string | null | undefined): string =>
  key ? (map[key] ?? key.replaceAll("_", " ").toLowerCase()) : "—";
