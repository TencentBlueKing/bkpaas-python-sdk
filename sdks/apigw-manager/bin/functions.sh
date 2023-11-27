#!/bin/bash

# 本文定义与业务逻辑无关的通用函数

log() {
    NOW=$(date +"%Y-%m-%d %H:%M:%S")
    echo "${NOW} [$1] $2"
}

log_info() {
    log "INFO" "$1"
}

log_warn() {
    log "WARN" "$1"
}

log_error() {
    log "ERROR" "$1"
}

title() {
    echo "====== $1 ======"
}

call_command() {
    command=$1
    shift

    log_info "Running command ${command}"

    apigw-manager.sh "${command}" "$@"
    status=$?

    if [ ${status} -ne 0 ]; then
        log_warn "Command ${command} failed with status ${status}"
        return ${status}
    fi
    
    return 0
}

call_definition_command() {
    command=$1
    definition=$2
    shift 2
    
    # check definition exists
    if [ ! -f "${definition}" ]; then
        log_warn "Definition file ${definition} does not exist, skipped"
        return 0
    fi

    call_command "${command}" -f "${definition}" "$@"
    status=$?
    
    if [ ${status} -ne 0 ]; then
        log_warn "Command ${command} failed with status ${status}"
        return ${status}
    fi
    
    return 0
}

must_call_definition_command() {
    command=$1
    definition=$2
    shift 2

    call_definition_command "${command}" "${definition}" "$@"
    status=$?

    if [ ${status} -ne 0 ]; then
        log_error "Crash during command ${command}"
        exit ${status}
    fi

    return 0
}