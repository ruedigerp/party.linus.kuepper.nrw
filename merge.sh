#!/bin/bash

#!/bin/bash

# Merge Script für verschiedene Branch-Kombinationen
# Usage: ./merge.sh <step>

STEP=$1

case $STEP in
  "dev-stage")
    echo "🚀 Merging dev -> stage"

    PR_OUTPUT=$(gh pr create \
      --base stage \
      --head dev \
      --title "Deploy dev to stage - $(date +%Y-%m-%d)" \
      --body "Deploy latest development changes to staging environment")
    
    # PR Number aus URL extrahieren (z.B. "https://github.com/user/repo/pull/123")
    PR_NUMBER=$(echo "$PR_OUTPUT" | grep -o '[0-9]\+$')
    
    gh pr merge $PR_NUMBER --merge --subject "Release stage" --auto

    ;;
    
  "dev-main")
    echo "🚀 Merging dev -> main"

    PR_OUTPUT=$(gh pr create \
      --base main \
      --head dev \
      --title "Deploy dev to main - $(date +%Y-%m-%d)" \
      --body "Deploy latest development changes to production environment")
    
    # PR Number aus URL extrahieren (z.B. "https://github.com/user/repo/pull/123")
    PR_NUMBER=$(echo "$PR_OUTPUT" | grep -o '[0-9]\+$')
    
    gh pr merge $PR_NUMBER --merge --subject "Release stage" --auto

    ;;

  "stage-main")
    echo "🚀 Merging stage -> main"

    PR_OUTPUT=$(gh pr create \
      --base main \
      --head stage \
      --title "Deploy stage to main - $(date +%Y-%m-%d)" \
      --body "Deploy latest development changes to production environment")

    PR_NUMBER=$(echo "$PR_OUTPUT" | grep -o '[0-9]\+$')

    gh pr merge $PR_NUMBER --merge --subject "Release production" --auto

    ;;
    
  "back-merge")
    echo "🔄 Back-merging after production release"
    git fetch origin
    git checkout main
    git pull origin main
    LATEST_TAG=$(git tag | grep -v "-" | sort -V | tail -1)
    echo "Latest tag: $LATEST_TAG"
    
    # main -> stage
    PR_OUTPUT=$(gh pr create \
      --base stage \
      --head main \
      --title "Back-merge release $LATEST_TAG to stage" \
      --body "Sync stage with latest production release" )

    PR_NUMBER=$(echo "$PR_OUTPUT" | grep -o '[0-9]\+$')
    echo "PR Number: ${PR_NUMBER}"
    
    gh pr merge $PR_NUMBER --merge --subject "Back-merge release ${LATEST_TAG} [skip ci]" --auto

    # Warten bis der erste PR wirklich gemerged ist
    echo "Waiting for stage merge to complete..."
    sleep 10
    
    # main -> dev  
    PR_OUTPUT=$(gh pr create \
      --base dev \
      --head main \
      --title "Back-merge release $LATEST_TAG to dev" \
      --body "Sync dev with latest production release")
    
    PR_NUMBER=$(echo "$PR_OUTPUT" | grep -o '[0-9]\+$')
    echo "PR Number: ${PR_NUMBER}"

    gh pr merge $PR_NUMBER --merge --subject "Back-merge release ${LATEST_TAG} [skip ci]" --auto
    git checkout dev 
    git pull
    ;;
    
  *)
    echo "❌ Unknown step: $STEP"
    echo ""
    echo "Usage: $0 <step>"
    echo ""
    echo "Available steps:"
    echo "  dev-stage   - Merge dev -> stage"
    echo "  dev-main   - Merge dev -> main"
    echo "  stage-main  - Merge stage -> main"  
    echo "  back-merge  - Back-merge main -> stage & dev after release"
    echo ""
    echo "Examples:"
    echo "  $0 dev-stage"
    echo "  $0 dev-main"
    echo "  $0 stage-main"
    echo "  $0 back-merge"
    exit 1
    ;;
esac

echo "✅ Done!"


# gh pr create --base stage --head dev --title "Merge dev to stage" -a ruedigerp -b ""

# gh pr merge 33 -m --auto

# gh pr create --base main --head stage --title "Merge stage to prod" -a ruedigerp -b ""
# gh pr merge 34 -m --auto


# git fetch origin
# git checkout main
# git pull origin main
# LATEST_TAG=$(git describe --tags --abbrev=0 main)

# gh pr create \
#   --base stage \
#   --head main \
#   --title "Back-merge release ${LATEST_TAG} to stage" \
#   --body "Sync stage with latest production release"

# gh pr merge 35 --merge --subject "Back-merge release ${LATEST_TAG} [skip ci]" --auto

# git fetch origin
# git checkout main
# git pull origin main
# LATEST_TAG=$(git describe --tags --abbrev=0 main)

# gh pr create \
#   --base dev \
#   --head main \
#   --title "Back-merge release ${LATEST_TAG} to dev" \
#   --body "Sync stage with latest production release"

# gh pr merge 36 --merge --subject "Back-merge release ${LATEST_TAG} [skip ci]" --auto
