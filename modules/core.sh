#!/bin/bash

# Placeholder for BASE_DIR, replace with actual path if needed
BASE_DIR="./sites"

# Função de log
log() {
    local type="$1"
    local message="$2"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$type] $message"
}

# Validação de domínio
validate_domain() {
    local domain="$1"
    if [[ "$domain" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Criação de estrutura de diretórios e arquivos básicos
criar_estrutura_site() {
    if [[ "$(id -u)" -ne 0 ]]; then
        log "ERROR" "Esta função requer privilégios de root para modificar /etc/fstab e montar volumes."
        log "ERROR" "Execute o script como root ou com sudo."
        return 1
    fi

    local domain="$1" # Changed site_name to domain to match the provided snippet
    local site_dir="$BASE_DIR/$domain"

    log "INFO" "Criando estrutura para $domain em $site_dir"
    mkdir -p "$site_dir/data/wp" # Matches snippet

    # Criar volume persistente (exemplo com arquivo de loop)
    log "INFO" "Criando volume de 1GB em $site_dir/volume.img..."
    truncate -s 1G "$site_dir/volume.img"
    mkfs.ext4 "$site_dir/volume.img" # This command might require root

    # Adicionar ao /etc/fstab para montagem automática
    # Note: Operations below typically require root privileges
    if ! grep -q "$site_dir/volume.img" /etc/fstab; then
        log "WARNING" "Atenção: Será adicionada uma entrada em /etc/fstab para a montagem automática de $site_dir/volume.img."
        log "WARNING" "Certifique-se de que isso é desejado e que você tem um backup do seu /etc/fstab."
        # The echo to /etc/fstab and mount command will require root
        echo "$site_dir/volume.img $site_dir/data ext4 defaults,loop 0 0" >> /etc/fstab
        mount "$site_dir/data"
    fi

    # Definir permissões (chown typically requires root)
    chown -R www-data:www-data "$site_dir/data/wp"
    chmod -R 755 "$site_dir/data/wp"

    log "INFO" "Estrutura criada para $domain" # Changed log message to use INFO
    return 0
}

# Seleção de site com melhor UX
selecionar_site_por_numero() {
    local sites_dir="${1:-$BASE_DIR}"

    if [[ ! -d "$sites_dir" ]]; then
        log "ERROR" "Diretório de sites não encontrado: $sites_dir"
        return 1
    fi

    mapfile -t site_list < <(find "$sites_dir" -maxdepth 1 -mindepth 1 -type d -printf "%f\n" | sort)

    if [[ ${#site_list[@]} -eq 0 ]]; then
        log "WARNING" "Nenhum site encontrado em $sites_dir"
        return 1
    fi

    echo "📂 Sites disponíveis em $sites_dir:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local i
    for i in "${!site_list[@]}"; do
        local site_name="${site_list[$i]}"
        local stack_name="${site_name%%.*}" # Basic way to get stack name
        local status="❌ Inativo" # Default status

        # Attempt to check Docker stack status (simplified)
        # Ensure docker is installed before running docker commands
        if command -v docker &> /dev/null && docker stack ps "$stack_name" &>/dev/null; then
            # Check if at least one service in the stack is running
            if docker stack services "$stack_name" --format '{{.Replicas}}' | grep -q '1/1'; then
                status="✅ Ativo"
            else
                status="⚠️ Parcial" # Some services might not be 1/1
            fi
        fi
        printf "%3s. %-40s %s
" "$((i+1))" "$site_name" "$status"
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -ne "
🎯 Digite o número do site (0 para cancelar): "

    read -r escolha

    if [[ "$escolha" == "0" ]]; then
        log "INFO" "Operação cancelada pelo usuário"
        return 1
    fi

    if [[ "$escolha" =~ ^[0-9]+$ ]] && (( escolha >= 1 && escolha <= ${#site_list[@]} )); then
        echo "${site_list[$((escolha-1))]}" # Return the selected site name
        return 0
    else
        log "ERROR" "Seleção inválida: $escolha"
        return 1
    fi
}
