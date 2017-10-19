#####################################################
Mincer: stuff your websites with the best ingredients
#####################################################

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
	:target: https://www.gnu.org/licenses/agpl-3.0
	:alt: License: AGPL v3

Installation
============

Installation de python3 et pip3
-------------------------------

.. code-block:: bash

	sudo apt install python3 python3-pip

Récupération du code sur github
-------------------------------

TODO: a compléter

.. code-block:: bash

	git clone BLABLABLA
	cd mincer

Les outils de base : python3 et pip
-----------------------------------

.. code-block:: bash

	sudo apt install python3 python3-pip

Puis on lance l'initialisation du projet en mode dev ce qui récupérera toutes les dépendances du code et des outils automatiquement :

.. code-block:: bash

	make initdev

si ça ne marche pas on s'assure que ``~/.local/bin`` est bien dans le path car ce n'est pas le cas par défaut sur debian et ubuntu. Il faut ajouter ça dans ``~/.profile`` ou si vous utilisez **zsh** c'est directement dans ``~/.zshrc``.

Le make file utilise l'outil `pipenv <https://github.com/kennethreitz/pipenv>`_ pour gérer toutes les dépendances. Pour plus d'info là-dessus je conseil vivement `pipenv, solution moderne pour remplacer pip et virtualenv <http://sametmax.com/pipenv-solution-moderne-pour-remplacer-pip-et-virtualenv>`_ et bien sûr `la doc de pipenv <https://docs.pipenv.org/>`_.

Maintenant on a un environnement virtuel pour travailler.

Guide d'utilisation
===================

Sélectionner un ``div`` particulier
-----------------------------------

Pour sélectionner un ``div`` particulier dans la page de réponse d'un fournisseur de données on utilise la même syntaxe que pour les `sélecteurs JQuery <https://www.w3schools.com/jquery/jquery_ref_selectors.asp>`_. Cela permet :

*	de retrouver le même formalisme que lorsque l'on travaille sur les page web de KOHA.
*	de tester ces sélecteur très facilement car ils sont nativement supportés dans Firefox. Pour cela il suffit d'activer les ``Outils de développement`` :kbd:`Ctrl + Maj + i` puis dans l'onglet ``Inspecteur`` il y a un champ ``Rechercher dans le HTML`` qui permet de taper directement un sélecteur JQuery. Par exemple sur la page `<http://bulac.fr>`_ si on rentre le sélecteur ``#contenu .colonne-milieu-BULAC`` cela sélectionne dans l'inspecteur la colonne centrale de la page.

Ainsi il est possible de tester très facilement ses sélecteurs avant de les utiliser dans l'Adapter.

Todo list
=========

DONE
----

*	Page web de status basique à l'adresse ``GET /status``
*	Traitement des liste de lecture sur le serveur KOHA de la BULAC à l'adresse ``GET /koha/liste-de-lecture?param=123456789``
*	Traitement des recherches de document sur le serveur KOHA de la BULAC à l'adresse ``GET /koha/recherche?param=afrique``
*	Gérer le cas où il y a des réponses à la recherche
*	Gérer le cas où il n'y a pas de réponse à la recherche

TODO
----

*	rendre les lien fullpath pour permettre de les ouvrir depuis les partials
*	Pouvoir fixer l'origine dans les requêtes retournées pour permettre l'intégration dans une page externe (par exemple une iframe)
*	Gérer le cas où il y a une seule réponse à la recherche
*	Gérer le cas où la réponse du serveur n'a pas la forme attendue
*	Gérer le cas où le serveur ne répond pas
*	Gérer le cas où le serveur est OFFLINE
*	Afficher les différents cas d'erreur (via un affichage ok/problème) sur la page de status
*	Gestion des fournisseur de données via un fichier de configuration
*	Nettoyer (optionnellement) le HTML en supprimant les lignes vide et normalisant les indentations
*	Décorer (optionnellement) les résultats avec un lien vers la recherche chez le fournisseur
*	Décorer (optionnellement) les résultats avec le nombre de résultat
*	Modification des fournisseurs de donnée via une API REST standard à l'adresse `http://monserveur.net/providers`
*	Pages web de status détaillée pour chaque fournisseur de donnée à l'adresse ``GET /status/nom-du-fournisseur``
*	Accès aux pages de status détaillées depuis la page de status principale (selon la case ou l'on clique dans le tableau cela nous envoie vers la bonne page idéalement directement au bon endroit)
*	Login pour accéder à l'interface web
*	Ajouter un test de charge de traitement d'une page web complexe
*	Permettre le caching (pour 24h) des éléments de type liste de lecture qui évoluent peu (le cache peut être remis à zero depuis la page de configuration des fournisseurs)
*	Générer la documentation avec `Sphinx <http://www.sphinx-doc.org/en/stable/tutorial.html>`_ et `Napoleon <https://pypi.python.org/pypi/sphinxcontrib-napoleon>`_
*	Intégrer la doc utilisateur directement dans la page de status/ajout via des liens contextuels

Notes en vrac
=============

`Doc parfaite de packaging <https://docs.google.com/presentation/d/e/2PACX-1vTeyzfozmHZWU5uy6pbKZmpdiMIWLZPRfHuENkN1YoOX01F6gP9--74khbGd0thx9xeVPVmmfFnjDAY/embed?start=false&loop=false&delayms=60000#slide=id.p>`_

Sphinx est bloqué en version 1.5.6 en attendant la publication du fix pour `<https://bitbucket.org/birkenfeld/sphinx-contrib/pull-requests/152/fix-182-by-moving-around-initialization/diff>`_
