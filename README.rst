.. image:: mincer/static/mincer_logo_200px.png
	:target: https://www.gnu.org/licenses/agpl-3.0
	:alt: License: AGPL v3

#####################################################
Mincer: stuff your websites with the best ingredients
#####################################################

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
	:target: https://www.gnu.org/licenses/agpl-3.0
	:alt: License: AGPL v3

Licence and copying
===================

Mincer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Mincer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Mincer.  If not, see `GNU licences <http://www.gnu.org/licenses/>`_.

Installation
============

Cette documentation est disponible à cette adresse: <https://github.com/BULAC/mincer>

Installation de python3 et pip3
-------------------------------

.. code-block:: bash

	sudo apt install python3 python3-pip

Récupération du code sur github
-------------------------------

.. code-block:: bash

	git clone https://github.com/BULAC/mincer.git
	cd mincer

Les outils de base : python3 et pip
-----------------------------------

.. code-block:: bash

	sudo apt install python3 python3-pip

Il est important que l'utilisateur qui lancera ou developpera mincer ait dans son path ``$HOME/.local/bin``. Pour cela on s'assure que ``$HOME/.local/bin`` est bien dans le path l'utilisateur qui lancera ou developpera Mincer car ce n'est pas le cas par défaut sur debian et ubuntu. Il faut ajouter à la fin de ``~/.profile`` (ou de ``~/.bashrc`` ça revient au même) ou si vous utilisez **zsh** c'est directement dans ``~/.zshrc`` :

.. code-block:: bash

	PATH=$PATH:$HOME/.local/bin

Pour valider ce changement il faut sourcer le fichier en question (n'exécuter que la commande correspondant au fichier que vous avez modifié) :

.. code-block:: bash

	source ~/.profile
	source ~/.bashrc
	source ~/.zshrc

Puis on lance l'initialisation du projet en mode dev ce qui récupérera toutes les dépendances du code et des outils automatiquement :

.. code-block:: bash

	make initdev

Le make file utilise l'outil `pipenv <https://github.com/kennethreitz/pipenv>`_ pour gérer toutes les dépendances. Pour plus d'info là-dessus je conseil vivement `pipenv, solution moderne pour remplacer pip et virtualenv <http://sametmax.com/pipenv-solution-moderne-pour-remplacer-pip-et-virtualenv>`_ et bien sûr `la doc de pipenv <https://docs.pipenv.org/>`_.

Maintenant on a un environnement virtuel pour travailler.


Activer l'environnement virtuel
-------------------------------

**Ceci doit être fait une et une seule fois à chaque fois que l'on veut travailler sur le projet ou qu'on veut le lancer.** Je renvoie à la doc de pipenv pour comprendre pourquoi exactement. Mais basiquement cela active toute les dépendances du projet dans un environnement virtuel.

.. code-block:: bash

	pipenv shell

(si tout se passe bien le prompt doit changer)

Initialiser la base de données (permet aussi de remettre a zero)
------------------------------

Il faut commencer par initialiser la base de donnée (creation des schema et chargement de la configuration de base :

.. code-block:: bash

	make initdb

Puis si besoin on peut charger quelques providers d'exemple:

.. code-block:: bash

	make loadbulacdb

Ces 2 commandes permettent aussi de remettre à zéro la baser de donnée si jamais elle est rendue inutilisable d'une façon ou d'une autre.

Si on souhaite sauvegarder ou restaurer la base de données, celle-ci est en fait contenu dans un seul fichier ``instance/mincer.db`` qu'il suffit de copier/coller. C'est ce fichier que les 2 commandes précédentes crée et remplissent.

Lancer le serveur Mincer
------------------------

On peut alors lancer le serveur Mincer :

.. code-block:: bash

	make prodrun

On l'arrête par un simple Ctrl+C.

On peut aussi le lancer en mode debug pendant le développement (celà permet de lancer une console python directement depuis le navigateur web en cas de problème ou de plantage) :

.. code-block:: bash

	make debugrun

La lecture du fichier **Makefile** peut être très instructive pour voir les différentes possibilités offertes par Mincer ;)

Guide d'utilisation
===================

Sélectionner un ``div`` particulier
-----------------------------------

Pour sélectionner un ``div`` particulier dans la page de réponse d'un fournisseur de données on utilise la même syntaxe que pour les `sélecteurs JQuery <https://www.w3schools.com/jquery/jquery_ref_selectors.asp>`_. Cela permet :

*	de retrouver le même formalisme que lorsque l'on travaille sur les page web de KOHA.
*	de tester ces sélecteur très facilement car ils sont nativement supportés dans Firefox. Pour cela il suffit d'activer les ``Outils de développement`` :kbd:`Ctrl + Maj + i` puis dans l'onglet ``Inspecteur`` il y a un champ ``Rechercher dans le HTML`` qui permet de taper directement un sélecteur JQuery. Par exemple sur la page `<http://bulac.fr>`_ si on rentre le sélecteur ``#contenu .colonne-milieu-BULAC`` cela sélectionne dans l'inspecteur la colonne centrale de la page.

Ainsi il est possible de tester très facilement ses sélecteurs avant de les utiliser dans l'Adapter.

Notes en vrac
=============

`Doc parfaite de packaging <https://docs.google.com/presentation/d/e/2PACX-1vTeyzfozmHZWU5uy6pbKZmpdiMIWLZPRfHuENkN1YoOX01F6gP9--74khbGd0thx9xeVPVmmfFnjDAY/embed?start=false&loop=false&delayms=60000#slide=id.p>`_

Sphinx est bloqué en version 1.5.6 en attendant la publication du fix pour `<https://bitbucket.org/birkenfeld/sphinx-contrib/pull-requests/152/fix-182-by-moving-around-initialization/diff>`_
