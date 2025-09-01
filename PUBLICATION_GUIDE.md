# Guide de Publication pour LlamaKeeper

## 🚀 Processus de Publication

### Prérequis

- Python 3.10+
- Git
- Compte PyPI
- Compte GitHub
- Droits de publication sur le dépôt

### Étapes de Publication

1. **Préparation Initiale**
   ```bash
   ./setup_dev_env.sh
   ```
   - Configure l'environnement de développement
   - Installe les dépendances
   - Prépare l'environnement de test

2. **Vérifications Pré-Publication**
   ```bash
   ./pre_publish_check.sh
   ```
   - Exécute les tests unitaires
   - Vérifie la couverture de code
   - Contrôle la qualité du code
   - Valide les configurations

3. **Finalisation de la Release**
   ```bash
   ./finalize_release.sh
   ```
   - Met à jour le CHANGELOG
   - Prépare les métadonnées
   - Crée un commit et un tag de release

4. **Publication**
   ```bash
   ./release_and_publish.sh
   ```
   - Vérifie les prérequis finaux
   - Publie sur PyPI
   - Pousse les tags sur GitHub

### Gestion des Versions

- Suivez le [Semantic Versioning](https://semver.org/)
- Mettez à jour le fichier `VERSION`
- Documentez les changements dans `CHANGELOG.md`

### Exemples de Versionnage

- Correctifs : 0.1.0 → 0.1.1
- Nouvelles fonctionnalités : 0.1.0 → 0.2.0
- Changements majeurs : 0.1.0 → 1.0.0

## 🛡️ Bonnes Pratiques

- Exécutez toujours les tests avant publication
- Vérifiez la documentation
- Assurez-vous que tous les scripts de vérification passent
- Documentez chaque changement

## 🚨 Dépannage

- Vérifiez les logs en cas d'échec
- Assurez-vous que tous les prérequis sont installés
- Contactez l'équipe de maintenance en cas de problème

## 📋 Liste de Vérification Finale

- [ ] Tests passent
- [ ] Code formaté
- [ ] `CHANGELOG.md` mis à jour
- [ ] Version incrémentée
- [ ] Credentials configurés
- [ ] Scripts de vérification exécutés
- [ ] Publication sur PyPI
- [ ] Tags Git poussés

## 🤝 Contribution

Merci de suivre ces étapes pour maintenir la qualité et la cohérence du projet.