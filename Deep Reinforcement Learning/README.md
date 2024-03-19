# Apprentissage par Renforcement profond pour la prédiction de marché financiers

Ce projet implémente un algorithme d'apprentissage par renforcement profond conçu pour prédire des séries temporelles financières. Il utilise l'apprentissage profond par renforcement pour définir l'achat, la vente et la conservation des actions/monnaies sur le marché boursier.

## Pour Commencer

### Installation des différentes librairies
Pour ce projet, les bibliothèques suivantes sont nécessaires : 
- collections
- datetime
- io
- logging
- math
- mplfinance
- numpy
- os
- pandas
- pathlib
- pylab import
- random
- re
- scipy
- sklearn
- sys
- talib
- tensorflow
- urllib
- zipfile


### Exemple d'utilisation

`demo.ipynb` sert d'exemple de l'application de l'algorithme d'apprentissage par renforcement.

### Données et Caractéristiques

- **Actifs**: Le programme prend en charge des actifs différents. Les cryptomonnaie sont téléchargées depuis Binance. Assurez-vous que l'actif (crypto-monnaie) existe et est inclus dans la liste `self.crypto_currencies` de l'environnement Finance. Tout autre actif, comme les actions, est téléchargé depuis Yahoo Finance. Vous pouvez également générer une série temporelle artificielle. L'actif `sinus_noise_std_1` est basé sur un signal sinusoïdal bruité avec 5 degrès de libertés (Cette partie n'a pas été modifié par rapport au code source).

- **Preprocessing des données**: L'algorithme permet l'expérimentation avec de nombreuses combinaisons de caractéristiques. Les caractéristiques doivent être définies sous forme d'une liste de tuples, où le premier élément est la caractéristique (par exemple, un indicateur technique) et le deuxième élément est la méthode de mise à l'échelle (par exemple, z-score, mise à l'échelle min-max). Cette partie a été entièrement reconstruite pour utiliser TA-lib qui permet plus de possibilités. et plus de lisibilité dans le code (selon nous).

-  **Architecture du Réseau**: Le cœur de ce modèle est un réseau LSTM (Long Short-Term Memory), qui est particulièrement bien adapté pour apprendre à partir de séquences de données, le rendant idéal pour la prédiction de séries temporelles. Le modèle utilise également l'apprentissage par lots pour un entraînement efficace sur de grands ensembles de données.

## Copyright

Ce travail est basé sur le travail de https://github.com/hommedesbois/DRLTradeBot. La structure du programme et certaines parties du code ont été réutilisées.