# mlb-predictions
MLB win-loss predictions on a daily basis, by Fantasy Toolz.

## Contents
Predictions for the outcome of MLB games, scraped and processed from MLB and Baseball Savant daily.

- Files in `predictions/latest.csv` is our daily prediction for the next two weeks of game outcomes.
- Team-specific files in `data/teams` record the outcomes of daily games.

Tuning of estimated outcomes took place based on the first two months of the 2023 season.

We also perform cursory validation that our predictions are robust.

## Engines

- `rundiffscraper.py` executes daily queries of MLB statcast to get the outcome of each game.
- `outcomepredictions.py` uses the run differentials and future matchups to predict the outcome of the next few games. This file queries the MLB API to obtain planned game information.