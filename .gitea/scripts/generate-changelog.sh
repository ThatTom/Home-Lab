#!/usr/bin/env bash
# Prints hosted-services/CHANGELOG.md: one row per service, built from the image lines in docker-compose/.
# Run by .gitea/workflows/changelog.yaml daily at 12:00 UTC, or by hand:
#   .gitea/scripts/generate-changelog.sh > hosted-services/CHANGELOG.md
set -euo pipefail
cd "$(dirname "$0")/../.."

cat <<'EOF'
# Changelog

## Live Services

Generated from the image versions in the [docker compose files](/docker-compose/) by [generate-changelog.sh](/.gitea/scripts/generate-changelog.sh), don't edit by hand. Each version change is in the git history of its compose file.

| Stack | Service | Category | Image | Version |
| --- | --- | --- | --- | --- |
EOF

find docker-compose -type f \( -name '*.yaml' -o -name '*.yml' \) -not -path '*/configs/*' | LC_ALL=C sort |
while IFS= read -r file; do
    awk -v file="$file" '
        # Top level keys start or end the services section
        /^[^ #]/ { in_services = ($0 ~ /^services:[[:space:]]*$/); next }
        in_services && /^  [A-Za-z0-9_.-]+:[[:space:]]*$/ { service = $1; sub(/:$/, "", service); next }
        in_services && /^    image:/ {
            image = $0
            sub(/^    image:[[:space:]]*/, "", image)
            sub(/[[:space:]]+#.*$/, "", image)
            gsub(/["\047]/, "", image)

            digest = ""
            if ((at = index(image, "@")) > 0) { digest = " + digest"; image = substr(image, 1, at - 1) }

            # The tag is after the first ":" of the last path segment, so registry ports are left alone
            slash = 0
            for (i = length(image); i > 0; i--) if (substr(image, i, 1) == "/") { slash = i; break }
            last = substr(image, slash + 1)
            if ((colon = index(last, ":")) > 0) {
                name = substr(image, 1, slash) substr(last, 1, colon - 1)
                tag = substr(last, colon + 1)
            } else {
                name = image
                tag = "latest (untagged)"
            }

            # ${VAR:-default} tags are set when the stack is deployed
            if (tag ~ /^\$\{[A-Za-z0-9_]+:-.*\}$/) {
                var = tag; sub(/^\$\{/, "", var); sub(/:-.*$/, "", var)
                def = tag; sub(/^\$\{[A-Za-z0-9_]+:-/, "", def); sub(/\}$/, "", def)
                tag = def " (or `" var "`)"
            } else if (tag ~ /^\$\{/) {
                var = tag; gsub(/[${}]/, "", var)
                tag = "set by `" var "`"
            }
            # Full commit hash tags are cut down to the usual short form
            if (tag ~ /^[0-9a-f]+$/ && length(tag) == 40) tag = substr(tag, 1, 7)

            category = file; sub(/^docker-compose\//, "", category); sub(/\/[^\/]*$/, "", category)
            stack = file; sub(/^.*\//, "", stack); sub(/\.ya?ml$/, "", stack)

            printf "| [%s](/%s) | %s | %s | `%s` | %s%s |\n", stack, file, service, category, name, tag, digest
        }
    ' "$file"
done
