#!/usr/bin/env python3
"""
Automatische Freisteller für Mannschaftsfotos
Verarbeitet alle Spielerbilder und fügt sie auf neue Hintergründe ein
"""

import os
import sys
from PIL import Image, ImageEnhance
from rembg import remove
import argparse
from pathlib import Path

def setup_directories():
    """Erstellt die benötigten Ordnerstrukturen"""
    directories = ['input_players', 'output_cutouts', 'backgrounds', 'final_results']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Ordner '{dir_name}' bereit")

def remove_background_batch(input_folder, output_folder):
    """
    Entfernt Hintergrund von allen Bildern im input_folder
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Unterstützte Bildformate
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Alle Bilddateien finden
    image_files = [f for f in input_path.iterdir() 
                   if f.suffix.lower() in supported_formats]
    
    print(f"Gefunden: {len(image_files)} Bilder zum Verarbeiten")
    
    for i, image_file in enumerate(image_files, 1):
        try:
            print(f"Verarbeite ({i}/{len(image_files)}): {image_file.name}")
            
            # Bild laden
            with open(image_file, 'rb') as input_file:
                input_data = input_file.read()
            
            # Hintergrund entfernen
            output_data = remove(input_data)
            
            # Ausgabedatei (immer als PNG für Transparenz)
            output_file = output_path / f"{image_file.stem}_cutout.png"
            
            # Speichern
            with open(output_file, 'wb') as out_file:
                out_file.write(output_data)
                
            print(f"  ✓ Gespeichert: {output_file.name}")
            
        except Exception as e:
            print(f"  ✗ Fehler bei {image_file.name}: {e}")
            continue
    
    print(f"\n🎉 Freisteller abgeschlossen! {len(image_files)} Bilder verarbeitet.")

def resize_player(player_img, max_height=1300):
    """
    Größe des Spielerbildes anpassen (proportional)
    """
    if player_img.height > max_height:
        ratio = max_height / player_img.height
        new_width = int(player_img.width * ratio)
        player_img = player_img.resize((new_width, max_height), Image.Resampling.LANCZOS)
    return player_img

def combine_with_background(cutout_folder, bg_folder, output_folder, player_position='center'):
    """
    Kombiniert freigestellte Spieler mit Hintergründen
    """
    cutout_path = Path(cutout_folder)
    bg_path = Path(bg_folder)
    output_path = Path(output_folder)
    
    print(f"bg_path: {bg_path}")
    # print(f"bg_path: ")
    # Hintergrundbilder finden
    bg_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
    bg_files = []
    for ext in bg_extensions:
        bg_files.extend(bg_path.glob(ext))
    
    print(f"Gefundene Hintergrundbilder: {[f.name for f in bg_files]}")
    
    if not bg_files:
        print("❌ Keine Hintergrundbilder gefunden!")
        print(f"Gesucht in: {bg_path.absolute()}")
        print("Unterstützte Formate: jpg, jpeg, png, bmp")
        return
    
    # Erstes Hintergrundbild als Standard verwenden
    bg_file = bg_files[0]
    print(f"Verwende Hintergrund: {bg_file.name}")    
    # Freigestellte Spieler finden
    cutout_files = list(cutout_path.glob('*_cutout.png'))
    
    print(f"Kombiniere {len(cutout_files)} Spieler mit Hintergrund...")
    
    for i, cutout_file in enumerate(cutout_files, 1):
        try:
            print(f"Kombiniere ({i}/{len(cutout_files)}): {cutout_file.name}")
            
            # Hintergrund laden
            background = Image.open(bg_file).convert('RGB')
            
            # Spieler laden (mit Transparenz)
            player = Image.open(cutout_file).convert('RGBA')
            
            # Spielergröße anpassen
            player = resize_player(player)
            
            # Position berechnen
            bg_width, bg_height = background.size
            player_width, player_height = player.size
            
            if player_position == 'center':
                x = (bg_width - player_width) // 2
                y = (bg_height - player_height) // 2
            elif player_position == 'bottom':
                x = (bg_width - player_width) // 2
                y = bg_height - player_height - 50  # 50px Abstand vom Rand
            else:  # top
                x = (bg_width - player_width) // 2
                y = 50  # 50px Abstand vom oberen Rand
            
            # Spieler auf Hintergrund setzen
            background.paste(player, (x, y), player)
            
            # Ausgabename generieren
            player_name = cutout_file.stem.replace('_cutout', '')
            output_file = output_path / f"{player_name}_final.jpg"
            
            # Speichern
            background.save(output_file, 'JPEG', quality=95)
            print(f"  ✓ Gespeichert: {output_file.name}")
            
        except Exception as e:
            print(f"  ✗ Fehler bei {cutout_file.name}: {e}")
            continue
    
    print(f"\n🎉 Kombinierung abgeschlossen! {len(cutout_files)} finale Bilder erstellt.")

def create_sample_background():
    """
    Erstellt ein Beispiel-Hintergrundbild falls keines vorhanden
    """
    bg_path = Path('backgrounds')
    if not any(bg_path.glob('*')):
        print("Erstelle Beispiel-Hintergrund...")
        
        # Einfacher Gradient-Hintergrund
        img = Image.new('RGB', (1200, 1600), color='#1e3a8a')  # Dunkelblau
        
        # Gradient-Effekt (vereinfacht)
        for y in range(img.height):
            color_value = int(30 + (y / img.height) * 50)  # 30-80
            for x in range(img.width):
                img.putpixel((x, y), (color_value, color_value, color_value + 100))
        
        sample_bg = bg_path / 'sample_background.png'
        img.save(sample_bg, 'JPEG')
        print(f"✓ Beispiel-Hintergrund erstellt: {sample_bg}")

def main():
    parser = argparse.ArgumentParser(description='Automatische Mannschaftsfoto-Verarbeitung')
    parser.add_argument('--setup', action='store_true', help='Nur Ordner erstellen')
    parser.add_argument('--cutout-only', action='store_true', help='Nur Freisteller erstellen')
    parser.add_argument('--combine-only', action='store_true', help='Nur kombinieren')
    parser.add_argument('--position', choices=['center', 'bottom', 'top'], 
                       default='center', help='Position des Spielers')
    
    args = parser.parse_args()
    
    print("🏆 Mannschaftsfoto-Prozessor gestartet!")
    print("=" * 50)
    
    # Ordner erstellen
    setup_directories()
    
    if args.setup:
        print("\n📁 Ordner-Setup abgeschlossen!")
        print("\nNächste Schritte:")
        print("1. Spielerbilder in 'input_players/' kopieren")
        print("2. Hintergrundbilder in 'backgrounds/' kopieren")
        print("3. Script ohne --setup nochmal ausführen")
        return
    
    # Beispiel-Hintergrund erstellen falls nötig
    create_sample_background()
    
    if not args.combine_only:
        # Schritt 1: Freisteller erstellen
        print("\n🎯 Schritt 1: Hintergrund entfernen...")
        remove_background_batch('input_players', 'output_cutouts')
    
    if not args.cutout_only:
        # Schritt 2: Mit Hintergrund kombinieren
        print(f"\n🖼️ Schritt 2: Mit Hintergrund kombinieren (Position: {args.position})...")
        combine_with_background('output_cutouts', 'backgrounds', 'final_results', args.position)
    
    print("\n✨ Alle Schritte abgeschlossen!")
    print("\nErgebnisse:")
    print("- Freigestellte Spieler: output_cutouts/")
    print("- Finale Mannschaftsbilder: final_results/")

if __name__ == "__main__":
    main()