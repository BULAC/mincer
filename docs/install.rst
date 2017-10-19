Guide d'installation
====================

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
