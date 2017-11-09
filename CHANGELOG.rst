=========
CHANGELOG
=========

Branche develop
===============

*	Meilleure modèle de page avec un lien vers la page d'accueil dans le logo
*	Avoir une page d'administration pour pouvoir mettre à jour les dépendance JS et CSS sans modifier le code (sans effet pour le moment)

Version 1.2.0
=============

*	Rendre les lien fullpath pour permettre de les ouvrir depuis les partials
*	Gestion des fournisseur de données via une base de donnée
*	Configuration de l'application compatible avec un déploiement en environnement de production (via flask.app.config)
*	Rationnalisation de l'architecture des tests

Version 1.1.0
=============

*	Gérer le cas où il n'y a pas de réponse à la recherche
*	Pouvoir fixer l'origine dans les requêtes retournées pour permettre l'intégration dans une page externe (par exemple une iframe)
*	Afficher les différents cas d'erreur (via un affichage ok/problème) sur la page de status
*	Pages web de status détaillée pour chaque fournisseur de donnée à l'adresse ``GET /status/nom-du-fournisseur``
*	Accès aux pages de status détaillées depuis la page de status principale (selon la case ou l'on clique dans le tableau cela nous envoie vers la bonne page idéalement directement au bon endroit)

Version 1.0.0
=============

*	Page web de status basique à l'adresse ``GET /status``
*	Traitement des liste de lecture sur le serveur KOHA de la BULAC à l'adresse ``GET /koha/liste-de-lecture?param=123456789``
*	Traitement des recherches de document sur le serveur KOHA de la BULAC à l'adresse ``GET /koha/recherche?param=afrique``
*	Gérer le cas où il y a des réponses à la recherche
*	Générer la documentation avec `Sphinx <http://www.sphinx-doc.org/en/stable/tutorial.html>`_ et `Napoleon <http://www.sphinx-doc.org/en/stable/ext/napoleon.html>`_

TODO
====

*	Modification des fournisseurs de donnée via une API REST standard à l'adresse `http://monserveur.net/providers`
*	Gérer le cas où il y a une seule réponse à la recherche
*	Gérer le cas où la réponse du serveur n'a pas la forme attendue
*	Gérer le cas où le serveur ne répond pas
*	Gérer le cas où le serveur est OFFLINE
*	Nettoyer (optionnellement) le HTML en supprimant les lignes vide et normalisant les indentations
*	Décorer (optionnellement) les résultats avec un lien vers la recherche chez le fournisseur
*	Décorer (optionnellement) les résultats avec le nombre de résultat
*	Login pour accéder à l'interface web
*	Ajouter un test de charge de traitement d'une page web complexe
*	Permettre le caching (pour 24h) des éléments de type liste de lecture qui évoluent peu (le cache peut être remis à zero depuis la page de configuration des fournisseurs)
*	Intégrer la doc utilisateur directement dans la page de status/ajout via des liens contextuels
