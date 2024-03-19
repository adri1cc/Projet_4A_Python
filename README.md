# Bot de Trading Automatisé

Ce répertoire git présente le travail réalisé au cours de notre quatrième année à POLYTECH Dijon sur la création d’un bot de trading, avec pour objectif d’automatiser des transactions sur des exchanges centralisés (CEX).

## Objectif du Projet
Le projet vise à développer un bot de trading capable de réaliser des transactions sur les paires de devises suivantes : BTC/USDT, ETH/USDT et SOL/USDT. Au cours du semestre précédent, nous avions déjà réalisé les tâches suivantes :

- Création d'une interface graphique à l’aide de la librairie Dash
- Fonctionnalité pour lancer et arrêter des trades
- Implémentation d’une première stratégie basée sur le SMA (Simple Moving Average)
- Programmation d’une fonction pour réaliser un backtest à partir d’anciennes données
- Affichage du portefeuille
- Affichage des logs

## Nouvelles Fonctionnalités
Au cours de ce semestre, notre objectif était de développer de nouvelles stratégies efficaces en se concentrant sur deux approches principales :

1. **Utilisation d'indicateurs existants :** Nous avons ajouté deux nouveaux indicateurs dans le fichier `strategies.py` en plus du SMA :
   - RSI (Relative Strength Index) : Donne une indication du surachat et de la survente d’une valeur.
   - MACD (Moving Average Convergence Divergence) : Calcule la différence entre deux moyennes mobiles établies sur différentes échelles de temps.

2. **Deep Reinforcement Learning (DRL) :** Nous avons exploré cette branche du machine learning pour développer des stratégies plus avancées.

## Base de Données
Nous avons également travaillé sur la création d’une base de données à l’aide de la librairie SQLite. Cela nous permet d’avoir un accès complet aux logs générés lors de l’utilisation du bot.

## Auteurs
Ce projet a été réalisé par l'équipe de développement de POLYTECH Dijon :
- JACQUET CRETIDES Adrien
- VALAYE Paulin 

