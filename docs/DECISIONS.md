# Decisions

## Raw JSON as the source of truth, rebuildable SQLite

Each Garmin response is written to `data/raw/` and the database is rebuilt from scratch on every
run (it takes under a second). Fixing a calculation or adding a field never requires fetching
from Garmin again, which rate-limits requests and has broken login more than once in 2026.

## SQLite instead of Parquet

The volume is small (tens of thousands of rows per year) and the database is queried directly
when the analysis is done with Claude. The site does not read the database: it reads the
published JSON files.

## Site reading JSON on every request (adapter-node)

After a sync, reloading the page is enough, with no rebuild.

## Local only (2026-10-16)

The site runs on localhost and the data is updated whenever the user wants, by running the
pipeline. It does not go on a VPS: no login, no multi-user and no scheduled sync.

## Technique ranges and reference limits

The ranges for cadence, ground contact time, oscillation and vertical ratio follow Garmin's
colours and are approximate. "Cardiac drift" is not shown: it only makes sense on runs of 60
minutes or more.

## Heat acclimation

Garmin returns `heatAltitudeAcclimation` empty for this account's Forerunner 265S, so the
dashboard uses each run's weather (temperature and dew point) to correct the pace.

## Maps and privacy

The site uses OpenStreetMap tiles (CARTO started requiring a key). The privacy zone is detected
from the point where the most runs start or end (at least three, within a 300 m radius) and
hides 400 m around it when enabled.

## Projections

VO2max and race predictions only get a projection with 8 weeks of history, using the Theil-Sen
trend damped by half. With less data the extrapolation would be noise.

## Parameterised routes and the plinth menu

plinth's `AppShell` does not list routes with a parameter. That is why `/recovery` exists as its
own route (in the menu) and each night lives at `/recovery/[night]`, sharing the same component.

## The day in detail

Three extra calls per day in the collection: HR every 2 min, stress and Body Battery every 3 min
and steps every 15 min. Stress comes with negative codes: -1 means no reading and -2 means too
much movement to measure. Both break the line; the -2 stretches become the "moving" band.
Activities take up elapsed time (including pauses), not moving time. Today only has data up to
the last sync of the watch with Garmin and of the pipeline.

Minutes per sport and the training calendar were removed from Load (2026-10-16): with no
football or gym recorded on the watch, they said nothing. The fields remain in `load.json` for
when they come back.

## Simplified load and technique (2026-10-16)

Load became an answer: a text verdict from Garmin's acute load against the recommended range,
with how many typical runs (median load of the runs over 8 weeks) are needed to get back to it.
Fitness/fatigue/freshness and monotony/strain left the screen because they do not stabilise
with 2–3 workouts per week; Garmin's load focus left because it contradicted the % easy
calculation (Garmin classifies by training effect, not by zones). The fields remain in
`load.json`.

Technique stopped being a chart against speed. Each run is adjusted to the median pace (rounded
to 0.5 km/h) using the speed line and plotted over time, with the direction of what is better
and the average runner band from Garmin in the background. Cadence now counts as "higher is
better"; stride length still has no better or worse.
