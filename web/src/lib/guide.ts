export interface GuideItem {
  term: string;
  text: string;
  reference?: string;
}

export interface GuideSection {
  id: string;
  title: string;
  items: GuideItem[];
}

export const GUIDE: GuideSection[] = [
  {
    id: "ritmo",
    title: "Ritmo e eficiência",
    items: [
      {
        term: "Pace",
        text: "Minutos para correr 1 km. Menor é mais rápido. Sozinho diz pouco: o mesmo pace pode ser fácil num dia fresco e duro num dia quente.",
      },
      {
        term: "Pace ajustado pela inclinação",
        text: "O pace equivalente no plano: subidas descontam, descidas cobram.",
      },
      {
        term: "Pace sem calor",
        text: "O pace que você teria num dia fresco, pela regra de Hadley: soma temperatura e ponto de orvalho (em °F) e desconta a perda de ritmo esperada.",
        reference: "até 100: sem efeito · 130: ~2% · 150: ~4,5% · 170: ~8%",
      },
      {
        term: "Metros por batimento",
        text: "Velocidade média dividida pela FC média: quantos metros você anda a cada batida do coração. Subir é a melhor prova de evolução aeróbica; calor e cansaço puxam para baixo.",
      },
      {
        term: "Condição de desempenho",
        text: "Depois de 6 a 20 minutos, o relógio compara seu pace e sua FC com o seu nível médio.",
        reference: "+5 ou mais: dia ótimo · perto de 0: normal · −5 ou menos: algo pesando",
      },
      {
        term: "Potência",
        text: "Energia por segundo que você gera, estimada pelo relógio. Responde na hora a subidas e vento. No mesmo ritmo, menos potência é mais economia.",
      },
    ],
  },
  {
    id: "tecnica",
    title: "Técnica (dinâmica de corrida)",
    items: [
      {
        term: "Cadência",
        text: "Passos por minuto, contando os dois pés. Subir 5% de cada vez é o recomendado; o famoso 180 é referência de elite em ritmo de prova.",
        reference:
          "abaixo de 153 baixa · 153–163 abaixo da média · 164–173 média · 174–183 boa · acima de 183 elite",
      },
      {
        term: "Comprimento da passada",
        text: "Metros entre um passo e o seguinte. Velocidade = cadência × passada. Cresce com a velocidade e a força; forçar passos longos costuma piorar a técnica.",
      },
      {
        term: "Tempo de contato com o solo",
        text: "Milissegundos que o pé fica no chão em cada passo. Menos é melhor.",
        reference:
          "abaixo de 218 elite · 218–248 bom · 249–277 médio · 278–308 abaixo · acima de 308 baixo",
      },
      {
        term: "Oscilação vertical",
        text: "Quantos centímetros o tronco sobe e desce a cada passo. Menos é melhor.",
        reference:
          "abaixo de 6,4 elite · 6,4–8,1 bom · 8,2–9,7 médio · 9,8–11,5 abaixo · acima de 11,5 baixo",
      },
      {
        term: "Razão vertical",
        text: "Oscilação dividida pela passada: a métrica de técnica mais justa entre alturas diferentes.",
        reference:
          "abaixo de 6,1% elite · 6,1–7,4 bom · 7,5–8,6 médio · 8,7–10,1 abaixo · acima de 10,1 baixo",
      },
      {
        term: "Técnica no mesmo ritmo",
        text: "Como correr mais rápido melhora quase todas as métricas, a comparação entre períodos é feita depois de descontar o efeito da velocidade, por uma reta ajustada a todas as corridas.",
      },
    ],
  },
  {
    id: "carga",
    title: "Carga e efeito do treino",
    items: [
      {
        term: "Carga de treino",
        text: "O custo fisiológico de uma atividade, calculado pelo EPOC: o oxigênio extra que o corpo consome depois para se recuperar.",
      },
      {
        term: "Carga aguda, crônica e razão",
        text: "Aguda: últimos 7 dias. Crônica: últimas 4 semanas, o que o corpo está acostumado.",
        reference:
          "razão 0,8–1,3 evolução segura · abaixo de 0,8 destreinando · acima de 1,5 risco de lesão",
      },
      {
        term: "Condicionamento, fadiga e frescor",
        text: "Médias exponenciais da carga diária de todos os esportes: condicionamento (42 dias), fadiga (7 dias) e frescor, a diferença entre os dois.",
        reference:
          "frescor positivo: descansado · −10 a −30: cansaço que faz evoluir · abaixo de −30: excesso",
      },
      {
        term: "Foco da carga",
        text: "Divide as últimas 4 semanas em aeróbico leve, aeróbico forte e anaeróbico, comparando com o equilíbrio que a Garmin recomenda para você.",
      },
      {
        term: "Regra 80/20",
        text: "Cerca de 80% do tempo de treino em intensidade leve (zonas 1–2) e 20% moderada ou forte. Treinar sempre no meio-termo cansa sem fazer evoluir.",
      },
      {
        term: "Monotonia e tensão",
        text: "Monotonia é a carga média do dia dividida pela variação entre os dias da semana; tensão é a carga semanal vezes a monotonia. Treinar igual todo dia aumenta o risco de lesão e doença.",
        reference: "monotonia abaixo de 1,5 variado · acima de 2 muito repetitivo",
      },
      {
        term: "Efeito de treino",
        text: "De 0 a 5, o quanto a atividade melhora o condicionamento aeróbico e o anaeróbico.",
        reference:
          "0–0,9 nenhum · 1–1,9 pequeno · 2–2,9 mantém · 3–3,9 melhora · 4–4,9 melhora muito · 5 excessivo",
      },
      {
        term: "Zonas de FC",
        text: "Faixas de frequência cardíaca a partir da sua FC máxima.",
        reference: "Z1 muito leve · Z2 base aeróbica · Z3 moderado · Z4 limiar · Z5 máximo",
      },
      {
        term: "FC de recuperação",
        text: "Quanto a FC caiu nos 2 minutos depois que você parou. Quedas maiores indicam coração mais condicionado; compare com as suas próprias corridas.",
      },
    ],
  },
  {
    id: "recuperacao",
    title: "Recuperação e sono",
    items: [
      {
        term: "VFC",
        text: "A variação de tempo entre batimentos durante o sono. Coração descansado varia mais. Compare só com você mesmo: o número absoluto muda muito entre pessoas.",
      },
      {
        term: "FC de repouso",
        text: "Cai conforme o condicionamento melhora. Alta de 5 bpm ou mais por vários dias costuma vir antes de doença ou excesso de treino.",
      },
      {
        term: "Pontuação do sono",
        text: "Junta duração, fases, despertares e estresse durante o sono.",
        reference: "90+ excelente · 80–89 bom · 60–79 razoável · abaixo de 60 ruim",
      },
      {
        term: "Fases do sono",
        text: "Profundo: recuperação física. REM: memória e aprendizado, concentrado no fim da noite. Leve: transição. Dormir tarde costuma cortar REM.",
      },
      {
        term: "Prontidão",
        text: "0 a 100, combinando sono da noite, sono dos últimos dias, tempo de recuperação, carga aguda, estresse e VFC. Abaixo de 50, prefira treino leve.",
      },
      {
        term: "Alerta de doença",
        text: "Compara FC de repouso, VFC e respiração da noite com a mediana das noites entre 30 e 3 dias atrás. Um sinal sozinho é comum; dois juntos merecem atenção. Não é diagnóstico.",
      },
      {
        term: "Body Battery",
        text: "Bateria de energia de 0 a 100, estimada por VFC, estresse, sono e atividade. Acordar abaixo de 50 com frequência indica recuperação insuficiente.",
      },
      {
        term: "Estresse",
        text: "0 a 100, estimado pela VFC quando você está parado. Inclui estresse físico como digestão, calor e álcool.",
        reference: "0–25 descanso · 26–50 baixo · 51–75 médio · 76–100 alto",
      },
    ],
  },
  {
    id: "prova",
    title: "Prova e perfil",
    items: [
      {
        term: "VO2max",
        text: "O máximo de oxigênio, em ml por kg por minuto, que o corpo consegue usar: o tamanho do motor. O relógio estima pelo pace e pela FC; corridas no calor podem subestimar.",
      },
      {
        term: "Previsões de prova",
        text: "Tempo estimado hoje em 5K, 10K, meia e maratona. Assumem preparo específico: sem treinos longos, meia e maratona são otimistas.",
      },
      {
        term: "Fórmula de Riegel",
        text: "Estima o tempo numa distância a partir de outra: T2 = T1 × (D2 ÷ D1)^1,06. Comparar com a previsão mostra quanto você ainda não testou em prova.",
      },
      {
        term: "Idade fitness",
        text: "A idade média de quem tem o seu condicionamento, pelo VO2max, FC de repouso e atividade vigorosa semanal.",
      },
      {
        term: "Projeções",
        text: "Tendência robusta (Theil-Sen), amortecida pela metade. Só aparecem com 8 semanas de histórico, para não extrapolar ruído.",
      },
    ],
  },
];
