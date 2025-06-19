#!/usr/bin/env bash

# Placeholder for log and selecionar_site_por_numero if not available
# These would typically be sourced from core.sh
if [ -z "$(command -v log)" ]; then log() { echo "LOG: [$1] $2"; }; fi
if [ -z "$(command -v selecionar_site_por_numero)" ]; then selecionar_site_por_numero() { echo "test.com"; }; fi
BASE_DIR=${BASE_DIR:-/mnt/sites} # Mock BASE_DIR
LOG_FILE=${LOG_FILE:-/dev/null} # Mock LOG_FILE

backup_rapido() {
    clear
    log "INFO" "Iniciando backup rápido"

    local site
    site=$(selecionar_site_por_numero)

    if [[ -z "$site" ]]; then
        log "WARNING" "Nenhum site selecionado para backup."
        return 1
    fi

    local site_dir="$BASE_DIR/$site"
    # Use a more robust way to define backup_dir, perhaps from a config or ensure /backups exists
    local backup_base_dir="/backups"
    mkdir -p "$backup_base_dir" # Ensure base backup directory exists
    local backup_dir="$backup_base_dir/$(date +%Y%m%d_%H%M%S)_${site//[^a-zA-Z0-9_.-]/_}" # Sanitize site name for directory

    echo "💾 === Backup Rápido: $site ==="
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📁 Destino: $backup_dir"

    if ! mkdir -p "$backup_dir"; then
        log "ERROR" "Não foi possível criar o diretório de backup: $backup_dir"
        return 1
    fi

    if [[ -d "$site_dir/data/wp" ]]; then
        log "INFO" "Fazendo backup dos arquivos WordPress..."
        tar -czf "$backup_dir/wordpress_files.tar.gz" -C "$site_dir/data" wp/ 2>/dev/null
        if [[ $? -eq 0 ]]; then
            log "SUCCESS" "Backup dos arquivos WordPress concluído: wordpress_files.tar.gz"
        else
            log "ERROR" "Falha no backup dos arquivos WordPress"
        fi
    else
        log "WARNING" "Diretório WordPress não encontrado em $site_dir/data/wp. Nenhum arquivo WordPress para backup."
    fi

    local stack_name="${site%%.*}"
    local db_container
    # Mocked docker command for now, real environment would need docker
    db_container=$(docker ps --filter "label=com.docker.stack.namespace=$stack_name" \
                   --filter "name=mysql" --filter "name=mariadb" \
                   --format "{{.Names}}" | head -1 2>/dev/null)

    if [[ -n "$db_container" ]]; then
        log "INFO" "Tentando backup do banco de dados do container: $db_container..."
        # Adjust credentials as necessary, these are placeholders
        if docker exec "$db_container" sh -c 'mysqldump -u wordpress -pwordpress wordpress' > "$backup_dir/database.sql" 2>/dev/null; then
            log "SUCCESS" "Backup do banco de dados concluído: database.sql"
        else
            log "ERROR" "Falha no backup do banco de dados. Verifique as credenciais e se o mysqldump está disponível no container."
        fi
    else
        log "WARNING" "Nenhum container de banco de dados (MySQL/MariaDB) encontrado para o stack $stack_name."
    fi

    # Backup da configuração
    if [[ -f "$site_dir/stack.yml" ]]; then
        cp "$site_dir/stack.yml" "$backup_dir/"
        log "SUCCESS" "Configuração do stack copiada: stack.yml"
    else
        log "INFO" "Arquivo stack.yml não encontrado em $site_dir. Nenhuma configuração de stack para backup."
    fi

    # Criar arquivo de informações do backup
    echo "Backup of site '$site' created on $(date +'%Y-%m-%d %H:%M:%S')" > "$backup_dir/backup_info.txt"
        find "$site_dir/data/wp" -name ".DS_Store" -type f -delete 2>/dev/null || true
    log "INFO" "Arquivos temporários (.DS_Store) removidos de $site_dir/data/wp (se existiam)." # This log seems to refer to .DS_Store

    log "SUCCESS" "Backup rápido concluído para o site '$site' em: $backup_dir"
    echo -e "
Pressione Enter para continuar..."
    read -r
}

# --- Outras funções do menu de reparo (placeholders) ---
reiniciar_stack() {
    log "INFO" "Função reiniciar_stack chamada."
    # Add actual logic here
    echo "Reiniciar stack - Implementação pendente. Pressione Enter." && read -r
}

verificar_integridade() {
    log "INFO" "Função verificar_integridade chamada."
    # Add actual logic here
    echo "Verificar integridade - Implementação pendente. Pressione Enter." && read -r
}

limpeza_cache() {
    log "INFO" "Função limpeza_cache chamada."
    # Add actual logic here
    echo "Limpeza de cache - Implementação pendente. Pressione Enter." && read -r
}

reparar_permissoes() {
    log "INFO" "Função reparar_permissoes chamada."
    # Add actual logic here
    echo "Reparar permissões - Implementação pendente. Pressione Enter." && read -r
}

mostrar_logs() {
    clear
    log "INFO" "Iniciando visualização de logs..."
    local site
    site=$(selecionar_site_por_numero)
    if [[ -z "$site" ]]; then
        log "WARNING" "Nenhum site selecionado."
        return 1
    fi
    local domain="$site"
    local stack_name="${site%%.*}"
    local site_dir="$BASE_DIR/$site"

    echo "📋 === Logs Detalhados do Site: $domain ==="
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Qual tipo de log você gostaria de ver?"
    echo "1. WordPress (debug.log, error.log)"
    echo "2. MySQL (error.log, slow-query.log)"
    echo "3. Docker (logs de todos os containers da stack)"
    echo "4. Logs do sistema (syslog, auth.log relacionados ao site - se configurado)"
    echo "0. Voltar"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -rp "Escolha o tipo de log: " tipo_log

    case "$tipo_log" in
        1) # WordPress logs
            echo -e "\n📜 Logs do WordPress:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            local wp_log_files=("$site_dir/data/wp/wp-content/debug.log" "$site_dir/data/wp/wp-content/error.log")
            local found_wp_log=false
            for log_file in "${wp_log_files[@]}"; do
                if [[ -f "$log_file" ]]; then
                    echo -e "\n--- Conteúdo de $(basename "$log_file") (últimas 50 linhas) ---"
                    tail -n 50 "$log_file"
                    found_wp_log=true
                else
                    echo -e "\n--- Arquivo $(basename "$log_file") não encontrado ---"
                fi
            done
            [[ "$found_wp_log" == false ]] && log "INFO" "Nenhum arquivo de log padrão do WordPress encontrado."
            ;;
        2) # MySQL logs
            echo -e "\n🐘 Logs do MySQL:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            local db_container
            db_container=$(docker ps --filter "label=com.docker.stack.namespace=$stack_name" \
                                   --filter "name=mysql" --filter "name=mariadb" \
                                   --format "{{.Names}}" | head -1 2>/dev/null)
            if [[ -n "$db_container" ]]; then
                echo "Tentando acessar logs dentro do container $db_container..."
                echo -e "\n--- MySQL error.log (últimas 50 linhas) ---"
                docker exec "$db_container" sh -c "tail -n 50 /var/log/mysql/error.log 2>/dev/null || echo 'Arquivo não encontrado ou erro ao ler.'"
                echo -e "\n--- MySQL slow-query.log (últimas 50 linhas) ---"
                docker exec "$db_container" sh -c "tail -n 50 /var/log/mysql/slow-query.log 2>/dev/null || echo 'Arquivo não encontrado ou erro ao ler.'"
            else
                log "WARNING" "Container MySQL/MariaDB não encontrado para a stack $stack_name."
            fi
            ;;
        3) # Docker container logs
            echo -e "\n🐳 Logs de todos os containers:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            local containers
            containers=$(docker ps --filter "label=com.docker.stack.namespace=$stack_name" --format "{{.Names}}")

            if [[ -n "$containers" ]]; then
                local all_logs_output
                all_logs_output=$(while IFS= read -r container; do
                    echo -e "\n--- Logs do $container (últimas 20 linhas) ---"
                    docker logs "$container" --tail 20
                done <<< "$containers") # Pass containers via here-string

                echo "$all_logs_output" # Display all logs first

                local error_count
                error_count=$(echo "$all_logs_output" | grep -Eci "error|fatal|critical" || true)

                if [[ "$error_count" -gt 0 ]]; then
                    log "WARNING" "Total de $error_count erros (error/fatal/critical) encontrados nos logs combinados dos containers."
                else
                    log "SUCCESS" "Nenhum erro crítico (error/fatal/critical) encontrado nos logs combinados dos containers."
                fi
            else
                log "WARNING" "Nenhum container encontrado para a stack $stack_name"
            fi
            ;;
        4) # System logs (Placeholder for actual implementation)
            echo -e "\n🐧 Logs do Sistema (Exemplo: syslog filtrado por nome do site - requer configuração):"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            log "INFO" "Verificando syslog para menções de '$domain' (últimas 50 linhas)..."
            sudo journalctl -u docker -n 50 --no-pager | grep -E "$domain|$stack_name" || echo "Nenhuma entrada relevante encontrada ou erro ao buscar."
            # Add more specific system log checks if applicable and configured
            ;;
        0)
            log "INFO" "Retornando ao menu de reparos..."
            return
            ;;
        *)
            log "ERROR" "Opção inválida: $tipo_log"
            sleep 1
            ;;
    esac
    echo -e "\nPressione Enter para voltar ao menu de reparos..."
    read -r
}

restaurar_backup() {
    log "INFO" "Função restaurar_backup chamada."
    # Add actual logic here
    echo "Restaurar backup - Implementação pendente. Pressione Enter." && read -r
}

diagnostico_completo() {
    log "INFO" "Função diagnostico_completo chamada."
    # Add actual logic here
    echo "Diagnóstico completo - Implementação pendente. Pressione Enter." && read -r
}

menu_reparo() {
    while true; do
        clear
        echo "🛠️ === Reparo e Diagnóstico ==="
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "1. 🔄 Reiniciar stack do site"
        echo "2. 🗂️ Backup rápido de site"
        echo "3. 🔍 Verificar integridade dos arquivos"
        echo "4. 🧹 Limpeza de cache do WordPress"
        echo "5. 🔒 Reparar permissões de arquivos"
        echo "6. 📜 Mostrar logs recentes do site"
        echo "7. 🔙 Restaurar backup"
        echo "8. 🩺 Diagnóstico completo do site"
        echo "0. ⬅️ Voltar ao menu principal"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        read -rp "Escolha uma opção: " opcao_reparo
        case "$opcao_reparo" in
            1) reiniciar_stack ;;
            2) backup_rapido ;;
            3) verificar_integridade ;;
            4) limpeza_cache ;;
            5) reparar_permissoes ;;
            6) mostrar_logs ;;
            7) restaurar_backup ;;
            8) diagnostico_completo ;;
            0) log "INFO" "Retornando ao menu principal..."; return ;;
            *) log "ERROR" "Opção inválida: $opcao_reparo"; sleep 1 ;;
        esac
        [[ "$opcao_reparo" != "0" ]] && echo -e "\nPressione Enter para voltar ao menu de reparos..." && read -r
    done
}
