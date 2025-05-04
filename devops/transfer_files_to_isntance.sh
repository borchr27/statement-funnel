#!/usr/bin/env bash
set -uxe
cd "$(dirname "$0")/.."


rsync -av --delete -e ssh\
  --filter=":- **/.gitignore"\
  --exclude="**/.git/"\
  --exclude="**/__pycache__/"\
  --exclude=".idea/"\
  --exclude="**/tmp/"\
  ./ "ubuntu@merlin-local:~/statement-funnel/";

scp -r ~/secrets/statement-funnel/ merlin-local:~/secrets/