# Spécifications générales du projet

## 1. Format des tickets (type Jira)

Pour **chaque action entraînant une modification de structure, de code ou de process**, un ticket doit être créé **avant l'affichage de la solution** au format **markdown**.

### Architecture du ticket

#### En-tête : Type
Valeurs possibles :
- **Bug** : Un problème à corriger
- **Migrate** : Action sur une base de données
- **Feature** : Nouvelle fonctionnalité
- **Refactor** : Mise à jour ou amélioration du code existant
- **Doc** : Documentation à produire
- **Test** : Création et/ou exécution de tests

#### Titre
- Description courte et explicite

#### Description
- Contexte
- Objectif du ticket

#### Tâches
- Liste de tâches sous forme de checkboxes

---

## 2. Projet d'apprentissage

**Technologies concernées :**
- Python
- React
- Prompt IA

### Règles générales pour le code produit

- La **première ligne de chaque fichier** doit contenir le **PATH du fichier**, sous forme de commentaire
- Le code doit être **commenté de manière concise** afin de faciliter la compréhension et l'apprentissage
- Utiliser **au maximum des variables d'environnement**, de manière intelligente, pour :
  - Factoriser le code
  - Paramétrer les applications
  - Améliorer la maintenabilité

---

## 3. Modèles et schémas Pydantic (Python)

### Règle obligatoire

Les schémas doivent respecter les règles de configuration de **Pydantic v2\***.

**Documentation de référence :**  
https://docs.pydantic.dev/2.8/concepts/config/

### Contraintes

- Adapter tous les modèles à la **version 2.x** de Pydantic
- Intégrer cette règle dans le **README récapitulatif du projet**

---

## 4. Processus de création lors de la génération

Lors de la création d'un ticket, le processus suivant doit être strictement respecté :

1. **CRÉER LE TICKET**
   ↓
2. **GÉNÉRER LES FICHIERS**
   ↓
3. **VALIDER LE TICKET**
   ↓
4. **CRÉER LE TICKET SUIVANT**

---

## 5. Approche méthodologique (DDD / SDD / TDD)

Les développements doivent répondre simultanément aux **trois problématiques suivantes**, utilisées de manière additive :

### 5.1 Phase de Conception – DDD (Domain Driven Design)

- Définition du **Langage Ubiquitaire**
- Définition des **Contextes Délimités**
- Résultat : plan et vision d'architecture

### 5.2 Phase d'Exigences – SDD (Security Driven Design)

- Analyse de menaces pour chaque composant critique issu du DDD
- Définition des exigences de sécurité

**Exemples :**
- Algorithme de hachage : **Argon2**
- Limitation du taux de connexion

### 5.3 Phase de Codage – TDD (Test Driven Development)

- Écriture des tests avant le code
- Validation du respect :
  - Des exigences fonctionnelles
  - Des exigences de sécurité

---

## 6. Patch critique SQLAlchemy

### Problème

```text
ObjectNotExecutableError: Not an executable object
```

### Solution permanente

Importer explicitement `text` depuis SQLAlchemy et l'utiliser pour toute requête SQL brute.

#### Exemple correct

```python
from sqlalchemy import text

# ✅ CORRECT
db.execute(text("SELECT 1"))
db.query(User).filter(text("level > 50")).all()
```

#### Exemple incorrect

```python
# ❌ INCORRECT
db.execute("SELECT 1")
```

---

## 7. Règle de conformité globale

Tout développement, ticket, schéma ou code généré doit :
- Respecter le **format de ticket défini**
- S'inscrire dans le **processus de génération**
- Être conforme aux principes **DDD / SDD / TDD**
- Être compatible avec les versions modernes des outils utilisés

