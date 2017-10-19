Guide d'utilisation
===================

Sélectionner un ``div`` particulier
-----------------------------------

Pour sélectionner un ``div`` particulier dans la page de réponse d'un fournisseur de données on utilise la même syntaxe que pour les `sélecteurs JQuery <https://www.w3schools.com/jquery/jquery_ref_selectors.asp>`_. Cela permet :

*	de retrouver le même formalisme que lorsque l'on travaille sur les page web de KOHA.
*	de tester ces sélecteur très facilement car ils sont nativement supportés dans Firefox. Pour cela il suffit d'activer les ``Outils de développement`` :kbd:`Ctrl + Maj + i` puis dans l'onglet ``Inspecteur`` il y a un champ ``Rechercher dans le HTML`` qui permet de taper directement un sélecteur JQuery. Par exemple sur la page `<http://bulac.fr>`_ si on rentre le sélecteur ``#contenu .colonne-milieu-BULAC`` cela sélectionne dans l'inspecteur la colonne centrale de la page.

Ainsi il est possible de tester très facilement ses sélecteurs avant de les utiliser dans l'Adapter.
