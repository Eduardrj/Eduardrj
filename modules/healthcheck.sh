#!/usr/bin/env bash

verificar_healthcheck() {
    clear
    log "INFO" "Iniciando verificação de saúde dos sites"

    local site
    site=$(selecionar_site_por_numero)

    if [[ -z "$site" ]]; then
        log "WARNING" "Nenhum site selecionado"
        return 1
    fi

    local domain="$site"
    local stack_name="${site%%.*}"

    echo -e "
🏥 === Verificação de Saúde: $domain ==="
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 1. Verificar se o stack está rodando
    echo "🐳 Verificando Docker Stack..."
    if docker stack services "$stack_name" &>/dev/null; then
        local running_services
        running_services=$(docker stack services "$stack_name" --format '{{.Replicas}}' | grep -c "1/1" || echo "0")
        local total_services
        total_services=$(docker stack services "$stack_name" --format '{{.Name}}' | wc -l)

        if [[ "$running_services" -eq "$total_services" && "$total_services" -gt 0 ]]; then
            log "SUCCESS" "Stack ativo: $running_services/$total_services serviços rodando"
        else
            log "WARNING" "Stack parcialmente ativo: $running_services/$total_services serviços rodando"
        fi
    else
        log "ERROR" "Stack não encontrado: $stack_name"
        echo -e "
Pressione Enter para continuar..."
        read -r
        return 1
    fi

    # 2. Teste de conectividade HTTP
    echo -e "
🌐 Testando conectividade HTTP..."
    local urls=("https://$domain" "http://$domain")

    for url in "${urls[@]}"; do
        echo -n "   Testando $url... "

        local response
        response=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}|%{size_download}"                    --max-time 10 --connect-timeout 5 "$url" 2>/dev/null || echo "000|0|0")

        IFS='|' read -r http_code response_time size_download <<< "$response"

        # This part was not fully shown in the issue for the loop, but it's implied
        # For the sake of correction, we assume it logs based on http_code
        if [[ "$http_code" -eq 200 ]]; then
            log "SUCCESS" "URL $url acessível (HTTP $http_code, ${response_time}s, ${size_download} bytes)"
        elif [[ "$http_code" -eq 000 ]]; then
            log "ERROR" "URL $url inacessível (Timeout ou falha na conexão)"
        else
            log "WARNING" "URL $url retornou HTTP $http_code (${response_time}s)"
        fi
    done # End of for url in "${urls[@]}"

    # 3. Verificar Certificado SSL
    echo -e "
🔒 Verificando Certificado SSL..."
    local ssl_info
    ssl_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null |                openssl x509 -noout -dates 2>/dev/null || echo "")

    if [[ -n "$ssl_info" ]]; then
        local not_after
        not_after=$(echo "$ssl_info" | grep "notAfter" | cut -d= -f2)
        log "SUCCESS" "Certificado SSL válido até: $not_after"

        local expiry_timestamp
        expiry_timestamp=$(date -d "$not_after" +%s 2>/dev/null || echo "0")
        local current_timestamp
        current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))

        if [[ "$days_until_expiry" -lt 30 && "$days_until_expiry" -gt 0 ]]; then
            log "WARNING" "Certificado expira em $days_until_expiry dias!"
        elif [[ "$days_until_expiry" -le 0 ]]; then
            log "ERROR" "Certificado SSL expirado!"
        fi
    else
        log "WARNING" "Não foi possível verificar o certificado SSL"
    fi

    # 4. Verificar uso de recursos
    echo -e "
📊 Verificando uso de recursos..."
    local containers
    containers=$(docker ps --filter "label=com.docker.stack.namespace=$stack_name" --format "{{.Names}}")

    if [[ -n "$containers" ]]; then
        while IFS= read -r container; do
            local stats
            stats=$(docker stats --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}" "$container" 2>/dev/null || echo "0%|0B / 0B")
            IFS='|' read -r cpu_usage mem_usage <<< "$stats"
            log "INFO" "Container $container: CPU $cpu_usage, Memória $mem_usage"
        done <<< "$containers" # Corrected while loop input
    else
        log "WARNING" "Nenhum container ativo encontrado"
    fi

    # 5. Verificar espaço em disco
    echo -e "
💾 Verificando espaço em disco..."
    local site_dir="$BASE_DIR/$site"
    if [[ -d "$site_dir/data" ]]; then
        local disk_usage
        disk_usage=$(du -sh "$site_dir/data" 2>/dev/null | cut -f1 || echo "N/A")
        local available_space
        available_space=$(df -h "$site_dir" | awk 'NR==2 {print $4}' || echo "N/A")
        log "INFO" "Uso do site: $disk_usage | Espaço disponível: $available_space"
    fi

    # 6. Teste de banco de dados (se aplicável)
    echo -e "
🗄️ Testando conexão com banco de dados..."
    local db_container
    db_container=$(docker ps --filter "label=com.docker.stack.namespace=$stack_name"                    --filter "name=mysql" --format "{{.Names}}" | head -1)

    if [[ -n "$db_container" ]]; then
        if docker exec "$db_container" mysqladmin ping -h localhost -u wordpress -pwordpress &>/dev/null; then
            log "SUCCESS" "Banco de dados MySQL respondendo"

            local db_size
            db_size=$(docker exec "$db_container" mysql -u wordpress -pwordpress -e "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB' FROM information_schema.tables WHERE table_schema='wordpress';" 2>/dev/null | tail -1 || echo "N/A")
            log "INFO" "Tamanho do banco: ${db_size}MB"
        else
            log "ERROR" "Falha na conexão com o banco de dados"
        fi
    else
        log "INFO" "Nenhum container MySQL encontrado"
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "
✅ Verificação de saúde concluída para $domain"
    echo -e "
Pressione Enter para voltar ao menu..."
    read -r
}

# Need to simulate the log function if it's not part of healthcheck.sh
# For this subtask, assume log() is available or errors are acceptable if it's not.
# The main script sources core.sh which has log().
if [ -z "$(command -v log)" ]; then
    log() {
        echo "LOG: [$1] $2"
    }
fi
if [ -z "$(command -v selecionar_site_por_numero)" ]; then
    selecionar_site_por_numero() {
        echo "test.com"
    }
fi
BASE_DIR=${BASE_DIR:-/mnt/sites}
LOG_FILE=${LOG_FILE:-/dev/null}
