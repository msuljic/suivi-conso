# Suivi Conso EDF

[README in English is here.](README-EN.md)

Ceci est un programme simple qui affiche les données de consommation d'électricité et de gaz EDF de manière plus analytique que ce qui est proposé sur le site web et l'application EDF.

## Démarrage rapide

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Télécharger les données

Rendez-vous sur <https://suiviconso.edf.fr/>, connectez-vous, sélectionnez `ÉLEC`, puis cliquez sur "Télécharger mes données." Répétez l'opération pour `GAZ` et décompressez les fichiers téléchargés.

### 3. Configurer le fichier de configuration

Copiez [`examples/basic-config.toml`](examples/basic-config.toml) dans le répertoire racine :

```bash
cp ./examples/basic-config.toml ./my-config.toml
```

Modifiez `my-config.toml` afin que les paramètres `dir_path` pointent vers les répertoires que vous avez téléchargés à l'étape précédente.

Vous pouvez voir tous les paramètres disponibles dans le fichier de configuration ainsi que des exemples d'utilisation dans [`examples/full-config.toml`](examples/full-config.toml).

### 4. Exécution

Exécutez la commande suivante :

```bash
python run.py my-config.toml
```

Pour plus d'options, voir :

```bash
python run.py -h
```

## Description

Il s'agit d'un programme Python simple qui utilise `pandas` et `matplotlib` pour traiter et afficher les données. Bien qu'il ait été initialement conçu pour afficher uniquement les données EDF "suivi conso", il peut également lire des fichiers CSV génériques et des fichiers au format `influxdb line protocol`.

La lecture, le traitement et l'affichage des données sont contrôlés par un fichier de configuration `TOML`. Chaque `[HEADER]` dans le fichier de configuration instancie un module qui peut lire, filtrer ou afficher les données. Consultez les fichiers de configuration dans le répertoire [`examples/`](examples/) pour plus d'informations.

### Modules de lecture

1. `edf_elec_reader` : Lit les données du répertoire de suivi de consommation d'électricité d'EDF.
2. `edf_gaz_reader` : Lit les données du répertoire de suivi de consommation de gaz d'EDF.
3. `csv_reader` : Lit les données d'un fichier CSV.
4. `influxdb_lp_reader` : Lit les données d'un fichier au format `influxdb line protocol`.

### Modules de filtrage

1. `basic_filter` : Offre des fonctionnalités de filtrage de base, telles que le découpage temporel et le rééchantillonnage.

### Modules d'affichage

1. `info_printer` : Affiche quelques informations sur les données dans le terminal, sans produire de graphiques.
2. `daily_plotter` : Affiche la tendance journalière au cours de l'année.
3. `hourly_plotter` : Affiche la tendance horaire moyenne sur 24 heures.
4. `weekly_plotter` : Affiche la tendance sur une semaine.
5. `correlation_plotter` : Affiche la corrélation entre les variables.

Le style des graphiques peut être ajusté en modifiant le fichier [`suiviconso.mplstyle`](suiviconso.mplstyle).

## Exemples de graphiques

### Tendance journalière sur l'année (`daily_plotter`)

Comment la consommation de gaz change jour après jour au cours de l'année :

<img src="examples/plots/Gas (m3) - Daily sum over the year.png" alt="Gas (m3) - Daily sum over the year" width=700>

Comment la température change jour après jour au cours de l'année :

<img src="examples/plots/T (°C) - Daily mean over the year.png" alt="T (°C) - Daily mean over the year" width=700>

### Tendance hebdomadaire (`weekly_plotter`)

Vous pouvez observer une consommation de gaz légèrement plus élevée le dimanche, c'est le jour où j'aime prendre un bain :

<img src="examples/plots/Gas (m3) - Trend over the week.png" alt="Gas (m3) - Trend over the week" width=700>

### Tendance horaire sur la journée (`hourly_plotter`)

Vous pouvez remarquer une structure plus régulière pendant les jours de semaine, avec des pics lors de la préparation du déjeuner et du dîner :

<img src="examples/plots/Electricity (kWh) - Hourly mean over the day.png" alt="Electricity (kWh) - Hourly mean over the day" width=700>

### Corrélation entre les variables

Comme on pouvait s'y attendre, la consommation de gaz et la température sont anticorrélées :

<img src="examples/plots/Gas (m3) vs T (°C).png" alt="Gas (m3) vs T (°C)" width=700>
