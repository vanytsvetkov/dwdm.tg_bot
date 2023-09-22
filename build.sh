#!/bin/bash

join_with_newline() {
    local result=""
    local delimiter=$'\n'

    for line in "$@"; do
        result="$result$line$delimiter"
    done

    echo -n "$result"
}

generate_script() {
    local script_name="$1"
    local script_content=(
        "#!/bin/bash"
        ""
        "export PYTHONPATH=$BASE_DIR"
        "source $BASE_DIR/venv/bin/activate &&"
        "$BASE_DIR/venv/bin/python3 $BASE_DIR/scripts/$script_name/main.py \"\$@\" > /dev/null 2>&1 &"
      )
    local script_fn="$BASE_DIR/scripts/$script_name/run.sh"
    join_with_newline "${script_content[@]}" > "$script_fn"
    chmod +x "$script_fn"
}

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

generate_script "RouteComparator"
generate_script "ChannelChecker"
generate_script "CustomerSyncer"
generate_script "UpdateProcessor"

CRON_RULES=(
  "0 9 * * *     $BASE_DIR/scripts/RouteComparator/run.sh"
  "0 10 * * 1    $BASE_DIR/scripts/ChannelChecker/run.sh"
  "0 10 * * *    $BASE_DIR/scripts/CustomerSyncer/run.sh"
  "0 4 * * *     $BASE_DIR/scripts/UpdateProcessor/run.sh"
)

join_with_newline "${CRON_RULES[@]}" > "$BASE_DIR/scripts/cron.sh"

SERVICE_LISTENER=(
  "[Unit]"
  "Description=dwdm.tg_bot (Listener Instance)"
  "After=network.target"
  ""
  "[Service]"
  "Type=simple"
  "User=root"
  "WorkingDirectory=$BASE_DIR"
  "Environment=PYTHONPATH=$BASE_DIR"
  "ExecStart=$BASE_DIR/venv/bin/python3 $BASE_DIR/bot.py"
  "Restart=always"
  "RestartSec=10"
  ""
  "[Install]"
  "WantedBy=multi-user.target"
)

join_with_newline "${SERVICE_LISTENER[@]}" > "$BASE_DIR/dwdm.tg_bot.listen.service"

SERVICE_SENDER=(
  "[Unit]"
  "Description=dwdm.tg_bot (Sender Instance)"
  "After=network.target"
  ""
  "[Service]"
  "Type=simple"
  "User=root"
  "WorkingDirectory=$BASE_DIR"
  "Environment=PYTHONPATH=$BASE_DIR"
  "ExecStart=$BASE_DIR/venv/bin/python3 $BASE_DIR/main.py"
  "Restart=always"
  "RestartSec=10"
  ""
  "[Install]"
  "WantedBy=multi-user.target"
)

join_with_newline "${SERVICE_SENDER[@]}" > "$BASE_DIR/dwdm.tg_bot.send.service"
