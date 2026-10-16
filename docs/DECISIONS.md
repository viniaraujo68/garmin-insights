# Decisões

## JSON bruto como fonte da verdade, SQLite reconstruível

Cada resposta da Garmin é gravada em `data/raw/` e o banco é refeito do zero a cada execução
(leva menos de um segundo). Corrigir um cálculo ou adicionar um campo nunca exige buscar de novo
na Garmin, que limita requisições e já quebrou o login mais de uma vez em 2026.

## SQLite em vez de Parquet

O volume é pequeno (dezenas de milhares de linhas por ano) e o banco é consultado diretamente
quando a análise é feita com o Claude. O site não lê o banco: lê os JSON publicados.

## Site lendo JSON a cada requisição (adapter-node)

Depois de um sync basta recarregar a página, sem rebuild. Também é o caminho para rodar num VPS
com login no futuro.

## Faixas de técnica e limites de referência

As faixas de cadência, contato com o solo, oscilação e razão vertical seguem as cores da Garmin e
são aproximadas. O "drift cardíaco" não é mostrado: só faz sentido em corridas de 60 minutos ou
mais.

## Aclimatação ao calor

A Garmin devolve `heatAltitudeAcclimation` vazio para o Forerunner 265S desta conta, então o painel
usa o clima de cada corrida (temperatura e ponto de orvalho) para corrigir o pace.

## Mapas e privacidade

O site usa os blocos do OpenStreetMap (a CARTO passou a exigir chave). A zona de privacidade é
detectada pelo ponto onde mais corridas começam ou terminam (pelo menos três, num raio de 300 m)
e esconde 400 m em volta dele quando ligada.

## Projeções

VO2max e previsões de prova só ganham projeção com 8 semanas de histórico, pela tendência de
Theil-Sen amortecida pela metade. Com menos dados a extrapolação seria ruído.

## Rotas com parâmetro e o menu do plinth

O `AppShell` do plinth não lista rotas com parâmetro. Por isso `/recuperacao` existe como rota
própria (no menu) e cada noite fica em `/recuperacao/[noite]`, compartilhando o mesmo componente.

## O dia em detalhe

Três chamadas a mais por dia na coleta: FC a cada 2 min, estresse e Body Battery a cada 3 min e
passos a cada 15 min. O estresse vem com códigos negativos: -1 é sem leitura e -2 é movimento
demais para medir. Os dois quebram a linha; os trechos de -2 viram a faixa "em movimento". As
atividades ocupam o tempo decorrido (com pausas), não o tempo em movimento. O dia de hoje só tem
dados até a última sincronização do relógio com o Garmin e do pipeline.

Minutos por esporte e calendário de treinos saíram da Carga (2026-10-16): sem futebol e academia
gravados no relógio, não diziam nada. Os campos continuam no `load.json` para quando voltarem.
