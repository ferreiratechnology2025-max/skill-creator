#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Skill Creator - Instalador Multi-Plataforma
# Instala skills em Claude Code, Codex e OpenCode
# Autor: Romel Ferreira
# ═══════════════════════════════════════════════════════════

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variáveis globais
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="criador-de-skills"
PLATFORMS_DETECTED=()
PLATFORMS_INSTALLED=()

# ───────────────────────────────────────────────────────────
# FUNÇÕES DE UTILIDADE
# ───────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Detecta se estamos no macOS, Linux ou Windows (WSL/Git Bash)
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# ───────────────────────────────────────────────────────────
# DETECÇÃO DE PLATAFORMAS
# ───────────────────────────────────────────────────────────

detect_claude_code() {
    if command -v claude &> /dev/null || [ -d "$HOME/.claude" ]; then
        return 0
    fi
    return 1
}

detect_codex() {
    if command -v codex &> /dev/null || [ -d "$HOME/.codex" ]; then
        return 0
    fi
    return 1
}

detect_opencode() {
    if command -v opencode &> /dev/null || [ -d "$HOME/.config/opencode" ] || [ -d "$HOME/.opencode" ]; then
        return 0
    fi
    return 1
}

detect_openclaw() {
    if [ -d "$HOME/.openclaw" ]; then
        return 0
    fi
    return 1
}

# ───────────────────────────────────────────────────────────
# INSTALAÇÃO POR PLATAFORMA
# ───────────────────────────────────────────────────────────

install_claude_code() {
    local target_dir="$HOME/.claude/skills/$SKILL_NAME"

    log_info "Instalando para Claude Code..."
    mkdir -p "$target_dir/evals"
    mkdir -p "$target_dir/references"

    # Copia arquivos
    cp "$SCRIPT_DIR/SKILL.md" "$target_dir/"
    cp "$SCRIPT_DIR/evals/evals.json" "$target_dir/evals/"

    # Copia referências se existirem
    if [ -d "$SCRIPT_DIR/references" ]; then
        cp -r "$SCRIPT_DIR/references/"* "$target_dir/references/" 2>/dev/null || true
    fi

    log_success "Claude Code: $target_dir"
    PLATFORMS_INSTALLED+=("Claude Code → $target_dir")
}

install_codex() {
    local target_dir="$HOME/.codex/skills/$SKILL_NAME"

    log_info "Instalando para Codex (OpenAI)..."
    mkdir -p "$target_dir/evals"
    mkdir -p "$target_dir/references"

    cp "$SCRIPT_DIR/SKILL.md" "$target_dir/"
    cp "$SCRIPT_DIR/evals/evals.json" "$target_dir/evals/"

    if [ -d "$SCRIPT_DIR/references" ]; then
        cp -r "$SCRIPT_DIR/references/"* "$target_dir/references/" 2>/dev/null || true
    fi

    # Codex também usa .agents/skills
    local agents_dir="$HOME/.agents/skills/$SKILL_NAME"
    if [ -d "$HOME/.agents" ] || [ -d "$HOME/.codex" ]; then
        mkdir -p "$agents_dir/evals"
        cp "$SCRIPT_DIR/SKILL.md" "$agents_dir/"
        cp "$SCRIPT_DIR/evals/evals.json" "$agents_dir/evals/"
        log_success "Codex (.agents): $agents_dir"
    fi

    log_success "Codex: $target_dir"
    PLATFORMS_INSTALLED+=("Codex → $target_dir")
}

install_opencode() {
    local target_dir="$HOME/.config/opencode/skills/$SKILL_NAME"
    local claude_compat="$HOME/.claude/skills/$SKILL_NAME"
    local agents_compat="$HOME/.agents/skills/$SKILL_NAME"

    log_info "Instalando para OpenCode..."

    # Instala no path nativo do OpenCode
    mkdir -p "$target_dir/evals"
    cp "$SCRIPT_DIR/SKILL.md" "$target_dir/"
    cp "$SCRIPT_DIR/evals/evals.json" "$target_dir/evals/"

    # Também instala nos paths compatíveis (Claude e .agents)
    if [ -d "$HOME/.claude" ] || detect_claude_code; then
        mkdir -p "$claude_compat/evals"
        cp "$SCRIPT_DIR/SKILL.md" "$claude_compat/"
        cp "$SCRIPT_DIR/evals/evals.json" "$claude_compat/evals/"
    fi

    if [ -d "$HOME/.agents" ] || detect_codex; then
        mkdir -p "$agents_compat/evals"
        cp "$SCRIPT_DIR/SKILL.md" "$agents_compat/"
        cp "$SCRIPT_DIR/evals/evals.json" "$agents_compat/evals/"
    fi

    log_success "OpenCode: $target_dir"
    PLATFORMS_INSTALLED+=("OpenCode → $target_dir")
}

install_openclaw() {
    local target_dir="$HOME/.openclaw/skills/$SKILL_NAME"

    log_info "Instalando para OpenClaw..."
    mkdir -p "$target_dir/evals"
    cp "$SCRIPT_DIR/SKILL.md" "$target_dir/"
    cp "$SCRIPT_DIR/evals/evals.json" "$target_dir/evals/"

    log_success "OpenClaw: $target_dir"
    PLATFORMS_INSTALLED+=("OpenClaw → $target_dir")
}

# ───────────────────────────────────────────────────────────
# INSTALAÇÃO MANUAL (quando nenhuma plataforma é detectada)
# ───────────────────────────────────────────────────────────

install_manual() {
    log_warn "Nenhuma plataforma detectada automaticamente."
    echo ""
    echo "Escolha onde instalar:"
    echo "  1) Claude Code (~/.claude/skills/)"
    echo "  2) Codex (~/.codex/skills/)"
    echo "  3) OpenCode (~/.config/opencode/skills/)"
    echo "  4) OpenClaw (~/.openclaw/skills/)"
    echo "  5) Todos os paths compatíveis"
    echo "  6) Path customizado"
    echo ""
    read -p "Opção (1-6): " choice

    case $choice in
        1)
            install_claude_code
            ;;
        2)
            install_codex
            ;;
        3)
            install_opencode
            ;;
        4)
            install_openclaw
            ;;
        5)
            install_claude_code
            install_codex
            install_opencode
            ;;
        6)
            read -p "Digite o path completo: " custom_path
            mkdir -p "$custom_path/$SKILL_NAME/evals"
            cp "$SCRIPT_DIR/SKILL.md" "$custom_path/$SKILL_NAME/"
            cp "$SCRIPT_DIR/evals/evals.json" "$custom_path/$SKILL_NAME/evals/"
            log_success "Custom: $custom_path/$SKILL_NAME"
            PLATFORMS_INSTALLED+=("Custom → $custom_path/$SKILL_NAME")
            ;;
        *)
            log_error "Opção inválida. Instalação cancelada."
            exit 1
            ;;
    esac
}

# ───────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL
# ───────────────────────────────────────────────────────────

main() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Skill Creator - Instalador Multi-Plataforma          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    OS=$(detect_os)
    log_info "Sistema operacional detectado: $OS"

    # Verifica arquivos necessários
    if [ ! -f "$SCRIPT_DIR/SKILL.md" ]; then
        log_error "SKILL.md não encontrado em $SCRIPT_DIR"
        log_info "Certifique-se de executar o install.sh na pasta raiz do skill-creator"
        exit 1
    fi

    if [ ! -f "$SCRIPT_DIR/evals/evals.json" ]; then
        log_warn "evals.json não encontrado. Criando evals básico..."
        mkdir -p "$SCRIPT_DIR/evals"
        echo '[]' > "$SCRIPT_DIR/evals/evals.json"
    fi

    # Detecta plataformas
    log_info "Detectando plataformas..."

    if detect_claude_code; then
        PLATFORMS_DETECTED+=("Claude Code")
    fi

    if detect_codex; then
        PLATFORMS_DETECTED+=("Codex")
    fi

    if detect_opencode; then
        PLATFORMS_DETECTED+=("OpenCode")
    fi

    if detect_openclaw; then
        PLATFORMS_DETECTED+=("OpenClaw")
    fi

    echo ""
    if [ ${#PLATFORMS_DETECTED[@]} -eq 0 ]; then
        log_warn "Nenhuma plataforma detectada."
        install_manual
    else
        log_info "Plataformas detectadas: ${PLATFORMS_DETECTED[*]}"
        echo ""

        # Instala em todas as plataformas detectadas
        if detect_claude_code; then
            install_claude_code
        fi

        if detect_codex; then
            install_codex
        fi

        if detect_opencode; then
            install_opencode
        fi

        if detect_openclaw; then
            install_openclaw
        fi
    fi

    # Resumo
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              INSTALAÇÃO CONCLUÍDA                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ ${#PLATFORMS_INSTALLED[@]} -eq 0 ]; then
        log_error "Nenhuma plataforma foi instalada."
        exit 1
    fi

    for platform in "${PLATFORMS_INSTALLED[@]}"; do
        echo -e "  ${GREEN}✓${NC} $platform"
    done

    echo ""
    log_info "Como usar:"
    echo "  1. Abra seu agente (Claude Code, Codex ou OpenCode)"
    echo "  2. Digite: /criar-skill"
    echo "  3. Ou descreva o processo que quer automatizar"
    echo ""
    log_info "Para abrir o wizard visual:"
    echo "  open $SCRIPT_DIR/wizard.html"
    echo ""
    log_info "Para testar a skill:"
    echo "  Use o evals.json em cada pasta de instalação"
    echo ""

    # Abre wizard se possível
    if command -v open &> /dev/null && [ -f "$SCRIPT_DIR/wizard.html" ]; then
        read -p "Deseja abrir o wizard visual agora? (s/n): " open_wizard
        if [[ "$open_wizard" =~ ^[Ss]$ ]]; then
            open "$SCRIPT_DIR/wizard.html"
        fi
    fi

    log_success "Skill Creator pronto para usar!"
}

# Executa
main "$@"
