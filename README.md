Lien du Site : https://projetrecipes-36cfv7jpjnkahmtdadbbc3.streamlit.app/
##Popotteexpress

#Description

Ce projet consiste en la construction d'un site web proposant des recettes variées et saines aux utilisateurs. Il intègre une base de données pour stocker les recettes et les préférences des utilisateurs, ainsi qu'un pipeline ETL pour collecter, transformer et charger les données. De plus, une newsletter hebdomadaire intelligente est envoyée aux utilisateurs grâce à l'utilisation de Mage AI et d'un trigger IA.

Fonctionnalités principales

Exploration de recettes : Les utilisateurs peuvent parcourir une large sélection de recettes saines.

Base de données : Stockage structuré des recettes et des préférences utilisateurs.

ETL (Extract, Transform, Load) : Un pipeline qui capte et traite les données avant de les stocker.

Newsletter automatisée : Une IA génère et envoie chaque semaine une newsletter pertinente contenant des suggestions personnalisées de recettes.

Technologies utilisées

Backend & API : Python (Flask ou FastAPI)

Frontend : Streamlit

Base de données : PostgreSQL / SQLite

ETL : Mage AI

Automatisation & Trigger : Mage AI + CronJob

Installation & Exécution

Prérequis

Python 3.x

PostgreSQL / SQLite

Mage AI

Installation

Clonez le projet :

git clone https://github.com/ton-github/healthy-recipes-hub.git
cd healthy-recipes-hub

Installez les dépendances :

pip install -r requirements.txt

Configurez la base de données :

python setup_db.py

Lancez l'application :

streamlit run app.py

Contribution

Les contributions sont les bienvenues ! N'hésitez pas à proposer des améliorations ou signaler des problèmes en ouvrant une issue.

Auteur
