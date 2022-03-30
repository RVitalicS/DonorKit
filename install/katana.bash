#!/usr/bin/env bash
# Katana launcher script



# set DONOR_KIT environment variable
# that contains toolkit resources directory
# and append it to KATANA_RESOURCES
: <<'REQUIRED'

export DONOR_KIT="$(readlink -e "../toolbox/katana")"
export KATANA_RESOURCES=$KATANA_RESOURCES:$DONOR_KIT

REQUIRED



# export KATANA_HOME=...
# exec "${KATANA_HOME}/bin/katanaBin" "$@"
