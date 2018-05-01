# veturilo
Scraper for your rentals of Veturilo - Warsaw's Public Bike

# How to run

1. Configure

```sh
export VETURILO_USER="+48123456789"
export VETURILO_PASS="123456"
```

2. Run

```sh
pipenv run tests
pipenv run scraper
```

3. Analyse

```sh
open rentals.csv
```

# Todo

1. Dump data into sqlite database
2. Send notifications (by email?) whenever rentals are changed

# Author

[michal@papierski.net](Michał Papierski)
