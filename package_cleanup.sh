#!/bin/bash

set -e
        
PACKAGE_NAME="ink-blog.kuepper.nrw"

# Berechne Cutoff-Datum (kompatibel mit macOS und Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS/BSD date
  CUTOFF_DATE=$(date -v-21d -u +"%Y-%m-%dT%H:%M:%SZ")
else
  # Linux date
  CUTOFF_DATE=$(date -d '21 days ago' -u +"%Y-%m-%dT%H:%M:%SZ")
fi

MIN_VERSIONS_TO_KEEP=3

echo "Bereinige Package: $PACKAGE_NAME"
echo "Cutoff-Datum: $CUTOFF_DATE"
echo "Mindestens zu behaltende Versionen: $MIN_VERSIONS_TO_KEEP"

# Hole alle Versionen sortiert nach Erstellungsdatum (neueste zuerst)
echo "Hole Package-Versionen..."
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /user/packages/container/$PACKAGE_NAME/versions \
  --paginate > /tmp/versions.json || {
  echo "Fehler beim Abrufen der Versionen. Möglicherweise ist das Package nicht vorhanden."
  exit 1
}

# Debug: Schaue dir die Struktur der ersten Version an
echo "Analysiere JSON-Struktur..."
echo "Erste Version:"
jq '.[0]' /tmp/versions.json
echo ""
echo "Anzahl Versionen insgesamt: $(jq 'length' /tmp/versions.json)"
echo ""

# Erstelle eine Liste der zu löschenden Versionen
echo "Filtere Versionen..."

# Erstelle temporäre Dateien für die Verarbeitung
old_versions_file="/tmp/old_versions.json"

# Filtere alte Versionen (älter als Cutoff-Datum)
echo "Filtere Versionen älter als $CUTOFF_DATE..."
jq --arg cutoff "$CUTOFF_DATE" '[.[] | select(.created_at < $cutoff)]' /tmp/versions.json > "$old_versions_file"
echo "Gefundene alte Versionen: $(jq 'length' "$old_versions_file")"

# Prüfe die Struktur einer alten Version
echo "Struktur einer alten Version:"
jq '.[0] // empty' "$old_versions_file"
echo ""

# Einfachere Filterung ohne metadata (da das Problem verursacht)
echo "Erstelle finale Liste zum Löschen (ohne Tag-Filterung)..."
versions_to_delete=$(jq -r --argjson keep "$MIN_VERSIONS_TO_KEEP" '
  sort_by(.created_at) | reverse | .[$keep:] | .[].id
' "$old_versions_file")

# Aufräumen
rm -f /tmp/versions.json "$old_versions_file"

if [ -z "$versions_to_delete" ]; then
  echo "Keine Versionen zum Löschen gefunden."
  exit 0
fi

echo "Gefundene Versionen zum Löschen:"
echo "$versions_to_delete" | wc -l

# Lösche Versionen einzeln mit Fehlerbehandlung
deleted_count=0
failed_count=0

echo "$versions_to_delete" | while read -r version_id; do
  if [ -n "$version_id" ]; then
    echo "Versuche Version ID $version_id zu löschen..."
    
    if gh api \
      --method DELETE \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      /user/packages/container/$PACKAGE_NAME/versions/$version_id \
      --silent; then
      echo "✓ Version $version_id erfolgreich gelöscht"
      deleted_count=$((deleted_count + 1))
    else
      echo "✗ Fehler beim Löschen von Version $version_id (möglicherweise bereits gelöscht)"
      failed_count=$((failed_count + 1))
    fi
    
    # Kurze Pause zwischen Löschungen um Rate-Limits zu vermeiden
    sleep 1
  fi
done

echo "Bereinigung abgeschlossen:"
echo "- Erfolgreich gelöscht: $deleted_count"
echo "- Fehlgeschlagen: $failed_count"
