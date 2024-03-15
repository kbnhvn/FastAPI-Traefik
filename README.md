# FastAPI-Traefik

## Cahier des charges :
https://1drv.ms/w/s!ArK3W0SU4bw29gz5Em1yGjNG07H8?e=N2dZ83


## Notes et instructions de dev :

### Pour commencer :
- Créer un dossier projet
- Cloner le repo dans ce dossier :
  ```https://github.com/kbnhvn/FastAPI-Traefik.git .```

### Répartition du travail :
Les différentes tâches et leur avancement sont visibles sur Jira : https://dst-fastapi-traefik.atlassian.net/jira/software/projects/KAN/boards/1
**Chaque tâche est liée à une branche** !

Pour afficher le nom de la branche liée à une tâche :
  - Cliquer sur la carte d'une tâche
  - Passer la souris sur ```1 branche``` sur le panneau de droite, le nom de la branche s'affiche

Remarques: 
  - Si la branche n'existe pas, il est possible de la créer via ce même menu (et choisir : Branch from : develop )
  - Eviter de travailler à plusieur sur la même branche pour éviter les conflits

- Vérifier sur quelle branche on se trouve: ```git status```
- Récupérer les branches: ```git fetch```
- Changer de branche: ```git checkout```

(Voir le module complémentaire Git/Github, notebook 3 : Github - First steps pour les principales commandes git)

### Lorsqu'une tâche liée à une branche est terminée :
Ouvrir une pull request :
**Vérifier la branche** (en haut à gauche de la capture d'écran), cliquer sur **contribute** puis **open pull request**

![Capture d'écran 2024-03-13 103535](https://github.com/kbnhvn/FastAPI-Traefik/assets/22301011/fc596a2d-7070-4404-bb11-64021c738e29)

S'assurer ensuite qu'il y ai bien **base: develop** en haut à gauche, et ajouter une description des tâches effectuées.
Ajouter les membres du groupe en **reviewer** en cliquant sur l'icône en haut à droite. 
Cliquer ensuite sur **Open pull request**

![Capture d'écran 2024-03-13 103608](https://github.com/kbnhvn/FastAPI-Traefik/assets/22301011/9e9658d3-8246-4f42-9a3c-fd4655250338)


### Règles de nommage des fichiers
Pour les manifests yaml :
- ```micro service```-```ressource``` par exemple web-service ou db-secret

