#!/bin/bash
# backend/run_tests.sh
# Script pour exécuter les tests avec différentes options

set -e  # Arrêt si erreur

echo "╔═══════════════════════════════════════════════════════╗"
echo "║         B'Craft'D - Exécution des Tests              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# FONCTIONS
# ============================================

run_all_tests() {
    echo -e "${BLUE}🧪 Exécution de TOUS les tests...${NC}"
    pytest -c config/pytest.ini tests/ -v
}

run_unit_tests() {
    echo -e "${BLUE}🧪 Exécution des tests UNITAIRES...${NC}"
    pytest -c config/pytest.ini tests/ -v -m unit
}

run_integration_tests() {
    echo -e "${BLUE}🧪 Exécution des tests D'INTÉGRATION...${NC}"
    pytest -c config/pytest.ini tests/ -v -m integration
}

run_with_coverage() {
    echo -e "${BLUE}📊 Exécution avec COUVERTURE DE CODE...${NC}"
    pytest -c config/pytest.ini tests/ -v --cov=. --cov-report=html --cov-report=term-missing
    echo ""
    echo -e "${GREEN}✅ Rapport de couverture généré dans: htmlcov/index.html${NC}"
}

run_specific_file() {
    if [ -z "$1" ]; then
        echo -e "${YELLOW}⚠️  Veuillez spécifier un fichier de test${NC}"
        echo "Exemple: $0 file test_security.py"
        exit 1
    fi
    echo -e "${BLUE}🧪 Exécution de: tests/$1${NC}"
    pytest -c config/pytest.ini tests/$1 -v
}

run_watch_mode() {
    echo -e "${BLUE}👀 Mode WATCH activé (re-test automatique)...${NC}"
    echo "Pressez Ctrl+C pour arrêter"
    pytest-watch -c config/pytest.ini tests/ -v
}

show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  all           Exécuter tous les tests (défaut)"
    echo "  unit          Exécuter uniquement les tests unitaires"
    echo "  integration   Exécuter uniquement les tests d'intégration"
    echo "  coverage      Exécuter avec rapport de couverture"
    echo "  file <name>   Exécuter un fichier spécifique"
    echo "  watch         Mode watch (re-test automatique)"
    echo "  help          Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 all"
    echo "  $0 coverage"
    echo "  $0 file test_security.py"
}

# ============================================
# TRAITEMENT DES ARGUMENTS
# ============================================

case "${1:-all}" in
    all)
        run_all_tests
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    coverage)
        run_with_coverage
        ;;
    file)
        run_specific_file "$2"
        ;;
    watch)
        run_watch_mode
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${YELLOW}⚠️  Option inconnue: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests terminés !${NC}"