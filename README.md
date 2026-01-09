# TomatoCycle 🌱

Application de gestion de la rotation des variétés de tomates anciennes.

Projet fil rouge – Master Ingénieur en Sciences des Données  
Année universitaire 2025–2026  
Étudiante : Aurélie

---

## 📌 Présentation

**TomatoCycle** est une application développée en Python dont l’objectif est d’aider une association de conservation de tomates anciennes à gérer la rotation annuelle de ses variétés.

L’association dispose d’un grand nombre de variétés, mais ne peut en cultiver qu’une partie chaque année. Les graines ayant une durée de vie limitée, l’application vise à identifier les variétés prioritaires à remettre en culture afin d’éviter leur disparition.

---

## 🎯 Objectifs principaux

- Gérer un catalogue de variétés de tomates
- Planifier les campagnes annuelles de culture
- Identifier les variétés urgentes à semer
- Suivre les résultats de germination
- Produire des documents de synthèse (PDF)

---

## 🧱 Architecture du projet

Le projet est structuré afin de **séparer clairement les responsabilités** :

- **models/** : entités métier, référentiels et paramètres globaux  
- **data_access/** : accès aux données (base SQLite, scraping, API)  
- **services/** : logique métier et traitements  
- **ui/** : interface utilisateur Streamlit  

Cette organisation vise à améliorer la lisibilité, la maintenabilité et l’évolutivité du code.


---
## 🛠️ Technologies utilisées

- Python
- Streamlit
- SQLite
- Pandas / NumPy
- Matplotlib / Seaborn

