#!/bin/bash

source $(dirname "$0")/functions.sh

definition_file="${definition_file:-definition.yaml}"
resources_file="${resources_file:-resources.yaml}"

title "begin to db migrate"
call_command_or_warning migrate apigw

title "syncing apigateway"
call_definition_command_or_exit sync_apigw_config "${definition_file}" ${SYNC_APIGW_CONFIG_ARGS}
call_definition_command_or_exit sync_apigw_stage "${definition_file}" ${SYNC_APIGW_STAGE_ARGS}
call_definition_command_or_exit grant_apigw_permissions "${definition_file}" ${GRANT_APIGW_PERMISSIONS_ARGS}
call_definition_command_or_exit sync_apigw_resources "${resources_file}" ${SYNC_APIGW_RESOURCES_ARGS:-"--delete"}
call_definition_command_or_exit sync_resource_docs_by_archive "${definition_file}" ${SYNC_RESOURCE_DOCS_BY_ARCHIVE_ARGS:-"--safe-mode"}

title "fetch apigateway public key"
apigw-manager.sh fetch_apigw_public_key --print > "${APIGW_PUBLIC_KEY_PATH:-apigateway.pub}"

title "fetch esb public key"
call_command_or_warning fetch_esb_public_key ${FETCH_ESB_PUBLIC_KEY_ARGS}

title "releasing"
call_definition_command_or_exit create_version_and_release_apigw "${definition_file}" ${CREATE_VERSION_AND_RELEASE_APIGW_ARGS:-"--generate-sdks"}

log_info "done"

title "syncing stage MCP Servers"
call_definition_command_or_exit sync_apigw_stage_mcp_servers "${definition_file}" ${SYNC_APIGW_STAGE_MCP_SERVERS_ARGS}

log_info "done"
