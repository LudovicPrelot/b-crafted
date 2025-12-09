# B'Crafted

Jeu de crafting réaliste, dans le sens où aucune magie, aucun accélérateur, aucun objet ne peut intervenir ni exister, **B'Crafted** (parfois écrit **B'Craft'D**) permet d'interpréter une profession avec 2 spécialités. Le but: trouver des ressources, qui s'avéreront être de mieux en mieux en fonction des niveaux, créer de nouveaux éléments avec ces ressources selon vos classes.


# Contexte

Ce projet est un moyen d'apprendre de nouvelles méthodes de travail, ainsi que de nouveaux langages :
- **Python** pour la partie backend
- **React** pour la partie frontend
- **Prompts IA** pour le développement complet

Car oui, la spécificité du projet: tous les codes sont générés avec des agents IA ! Claude, Gemini, ChatGPT,... Tout le contenu est entièrement généré à partir de prompts et d'idées prédéfinies en amont.


## Création des architectures

L'architecture, ainsi que les langages, les modèles de données sont hors IA. Tout est défini avant l'exécution des prompts, et chaque brique du projet va s'inscrire dans un projet Jira qui sera alimenté au fur et à mesure, comme un véritable projet d'entreprise. Tous les codes, ensuite, passeront sur un repo Github, destiné à servir de base d'apprentissage.

## Création des contenus

Chaque fichier sera généré par IA, avec une revue de code permanente. N'oublions pas que l'idée principale est d'en faire un projet d'apprentissage, pas juste faire un jeu dans son coin sans intérêt.
Bien entendu, il se pourrait que ces codes soient de temps en temps, voire souvent, incomplets, ou mal structurés. C'est aussi tout l'intérêt du projet : apprendre en faisant des erreurs pour mieux les corriger.

# Système de jeu

Le système de jeu est on ne peut plus basique : l'utilisateur sélectionne une classe initiale, qui va devoir récolter des ressources relatives à son métier. Chaque collecte apporte de l'expérience, et avec cette expérience, on peut monter en compétences pour trouver des ressources plus rares et/ou plus précieuses. 
Les ressources pourront être mélangées entre elles pour créer d'autres éléments (*recettes*), introuvables à l'état naturel. Ces nouvelles ressources pourront, à leur tour, être combinées à d'autres ressources pour en créer de nouvelles, et ainsi de suite.
Plus le niveau est élevé, plus les recettes seront complexes.

## Métiers
Chaque métier dispose de ses aptitudes et compétences. De ces métiers, il sera possible de débloquer et choisir, en fonction de son niveau, des spécialités permettant de collecter des ressources et de crafter des recettes spécifiques.

## Ressources
Les ressources sont trouvées dans la nature. Elles peuvent être minérales, végétales, animales,... Chaque ressource dispose de classes personnages spécifiques, ce qui implique qu'une classe de personnage définie ne pourra collecter qu'un certain nombre de ressources prédéfinies.
> Pas de poudre de perlinpinpin, désolé :)

## Recettes
Comme pour les ressources, les recettes sont intrinsèquement liées aux classes de personnages ainsi qu'aux ressources récupérées. Elles se complexifient avec les niveaux, ainsi qu'avec les ressources nécessaires à leur fabrication.

# Autres objectifs

## Une portée éducative

La paternité ayant frappé il y a quelques années à la porte, et la curiosité des enfants étant un véritable terreau à questions, j'ai pris le parti d'essayer de rendre ce projet instructif. Aussi, il sera possible, lors de la récupération de ressources, de l'évolution d'un personnage ou lors de l'élaboration de recettes, d'accéder à un petit descriptif de l'entité. Sans être trop pompeux, l'idée est de donner des informations, des connaissances et/ou des anecdotes utiles dans chaque aspect du jeu.

## Une évolution continue

Même si le coté jeu peut être distractif, il ne faut pas oublier que l'objectif initial est de se former sur des langages et sur des méthodes.  C'est pourquoi tout au long du processus de création, le jeu va changer, s'améliorer, revenir peut-être parfois en arrière, au fur et à mesure des projets, des idées et des mécanismes à mettre en place.
> Vous aurez le droit de ronchonner, de toute façon, je n'ai pas prévu de boîte à questions :D