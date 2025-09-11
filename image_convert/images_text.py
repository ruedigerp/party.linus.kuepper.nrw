#!/usr/bin/env python3
"""
Automatische Freisteller für Mannschaftsfotos
Verarbeitet alle Spielerbilder und fügt sie auf neue Hintergründe ein
"""

import os
import sys
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from rembg import remove
import argparse
from pathlib import Path
import re

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
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
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

def extract_player_info(filename):
    """
    Extrahiert Spielername und Nummer aus dem Dateinamen
    Erwartet Format: "36_Moritz_Breves.jpg" oder "Mueller_Max_7.jpg"
    """
    stem = Path(filename).stem.replace('_cutout', '').replace('_final', '')
    
    print(f"  🔍 Debug: Dateiname '{filename}' → Stamm: '{stem}'")
    
    # Verschiedene Namensformate unterstützen
    parts = stem.split('_')
    print(f"  🔍 Debug: Aufgeteilte Teile: {parts}")
    
    if len(parts) >= 3:
        # Format: Nummer_Vorname_Nachname oder Nachname_Vorname_Nummer
        if parts[0].isdigit():
            # Format: 36_Moritz_Breves
            number = parts[0]
            firstname = parts[1] if len(parts) > 1 else ""
            lastname = parts[2] if len(parts) > 2 else ""
            full_name = f"{firstname} {lastname}".strip()
        else:
            # Format: Nachname_Vorname_Nummer
            lastname = parts[0]
            firstname = parts[1] 
            number = parts[-1]  # Letzte Teil als Nummer
            full_name = f"{firstname} {lastname}"
    elif len(parts) == 2:
        # Format: Name_Nummer oder Vorname_Nachname
        if parts[1].isdigit():
            full_name = parts[0]
            number = parts[1]
        elif parts[0].isdigit():
            number = parts[0]
            full_name = parts[1]
        else:
            full_name = f"{parts[0]} {parts[1]}"
            number = "?"
    else:
        # Nur ein Name
        full_name = stem
        number = "?"
    
    print(f"  🔍 Debug: Ergebnis → Name: '{full_name}', Nummer: '{number}'")
    return full_name, number

def add_player_text(image, player_name, player_number, font_path=None, number_size=120, name_size=60):
    """
    Fügt Spielername (rotiert) und Nummer auf der linken Seite hinzu
    number_size: Schriftgröße für die Nummer (Standard: 120)
    name_size: Schriftgröße für den Namen (Standard: 60)
    """
    draw = ImageDraw.Draw(image)
    img_width, img_height = image.size
    
    print(f"    🎨 Füge Text hinzu: Name='{player_name}', Nummer='{player_number}'")
    print(f"    📏 Schriftgrößen: Nummer={number_size}, Name={name_size}")
    
    # Schriftarten laden
    try:
        if font_path and Path(font_path).exists():
            font_name = ImageFont.truetype(font_path, name_size)
            font_number = ImageFont.truetype(font_path, number_size)
            print(f"    📝 Verwende eigene Schrift: {font_path}")
        else:
            # Standardschrift versuchen (macOS)
            try:
                font_name = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", name_size)
                font_number = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", number_size)
                print(f"    📝 Verwende Arial (macOS)")
            except:
                try:
                    # Linux
                    font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", name_size)
                    font_number = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", number_size)
                    print(f"    📝 Verwende DejaVu (Linux)")
                except:
                    # Fallback zu Standardschrift
                    font_name = ImageFont.load_default()
                    font_number = ImageFont.load_default()
                    print(f"    📝 Verwende Default-Schrift")
    except Exception as e:
        font_name = ImageFont.load_default()
        font_number = ImageFont.load_default()
        print(f"    ⚠️ Schriftfehler, verwende Default: {e}")
    
    # Position für Text auf der linken Seite
    left_margin = 50
    
    # 1. Nummer oben links
    number_y = 260
    
    # Weißer Text mit schwarzem Rand für bessere Lesbarkeit
    # Schwarzer Rand (Outline-Effekt)
    for adj_x in range(-2, 3):
        for adj_y in range(-2, 3):
            draw.text((left_margin + adj_x, number_y + adj_y), 
                     player_number, font=font_number, fill='black')
    
    # Weißer Haupttext
    draw.text((left_margin, number_y), player_number, font=font_number, fill='white')
    print(f"    ✓ Nummer '{player_number}' hinzugefügt bei Position ({left_margin}, {number_y})")
    
    # 2. Name rotiert (90 Grad) unter der Nummer
    name_start_y = number_y + 200
    
    # Text für Rotation vorbereiten
    # Temporäres Bild für rotierten Text erstellen
    temp_img = Image.new('RGBA', (500, 100), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Text auf temporäres Bild schreiben
    # Schwarzer Rand
    for adj_x in range(-1, 2):
        for adj_y in range(-1, 2):
            temp_draw.text((10 + adj_x, 20 + adj_y), player_name, 
                          font=font_name, fill='black')
    
    # Weißer Haupttext
    temp_draw.text((10, 20), player_name, font=font_name, fill='white')
    
    # Text um 90 Grad rotieren
    rotated_text = temp_img.rotate(90, expand=True)
    
    # Rotierten Text auf Hauptbild einfügen
    # Position berechnen
    text_width, text_height = rotated_text.size
    paste_x = left_margin - 50
    paste_y = min(name_start_y, img_height - text_height - 25)
    
    # Nur den nicht-transparenten Teil einfügen
    image.paste(rotated_text, (paste_x, paste_y), rotated_text)
    print(f"    ✓ Name '{player_name}' (rotiert) hinzugefügt bei Position ({paste_x}, {paste_y})")
    
    return image

def resize_player(player_img, max_height=800):
    """
    Größe des Spielerbildes anpassen (proportional)
    """
    if player_img.height > max_height:
        ratio = max_height / player_img.height
        new_width = int(player_img.width * ratio)
        player_img = player_img.resize((new_width, max_height), Image.Resampling.LANCZOS)
    return player_img

def combine_with_background(cutout_folder, bg_folder, output_folder, player_position='center', add_text=True, font_path=None, number_size=120, name_size=60):
    """
    Kombiniert freigestellte Spieler mit Hintergründen und fügt Text hinzu
    """
    cutout_path = Path(cutout_folder)
    bg_path = Path(bg_folder)
    output_path = Path(output_folder)
    
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
    print(f"Text hinzufügen: {'JA' if add_text else 'NEIN'}")
    
    for i, cutout_file in enumerate(cutout_files, 1):
        try:
            print(f"Kombiniere ({i}/{len(cutout_files)}): {cutout_file.name}")
            
            # Hintergrund laden
            background = Image.open(bg_file).convert('RGB')
            
            # Spieler laden (mit Transparenz)
            player = Image.open(cutout_file).convert('RGBA')
            
            # Spielergröße anpassen
            player = resize_player(player)
            
            # Position berechnen (etwas nach rechts verschieben für Text)
            bg_width, bg_height = background.size
            player_width, player_height = player.size
            
            # Platz für Text auf der linken Seite lassen
            text_space = 150 if add_text else 0
            
            if player_position == 'center':
                x = (bg_width - player_width) // 2 + text_space // 2
                y = (bg_height - player_height) // 2
            elif player_position == 'bottom':
                x = (bg_width - player_width) // 2 + text_space // 2
                y = bg_height - player_height - 50
            else:  # top
                x = (bg_width - player_width) // 2 + text_space // 2
                y = 50
            
            # Spieler auf Hintergrund setzen
            background.paste(player, (x, y), player)
            print(f"  ✓ Spieler eingefügt bei Position ({x}, {y})")
            
            # Text hinzufügen
            if add_text:
                player_name, player_number = extract_player_info(cutout_file.name)
                print(f"  📝 Füge Text hinzu: '{player_name}' #{player_number}")
                
                if player_name and player_number and player_name.strip() and player_number.strip():
                    background = add_player_text(background, player_name, player_number, font_path, number_size, name_size)
                    print(f"  ✅ Text erfolgreich hinzugefügt")
                else:
                    print(f"  ⚠️ Konnte Name/Nummer nicht extrahieren")
            
            # Ausgabename generieren
            player_name_clean = cutout_file.stem.replace('_cutout', '')
            output_file = output_path / f"{player_name_clean}_final.jpg"
            
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
        
        sample_bg = bg_path / 'sample_background.jpg'
        img.save(sample_bg, 'JPEG')
        print(f"✓ Beispiel-Hintergrund erstellt: {sample_bg}")

def main():
    parser = argparse.ArgumentParser(description='Automatische Mannschaftsfoto-Verarbeitung')
    parser.add_argument('--setup', action='store_true', help='Nur Ordner erstellen')
    parser.add_argument('--cutout-only', action='store_true', help='Nur Freisteller erstellen')
    parser.add_argument('--combine-only', action='store_true', help='Nur kombinieren')
    parser.add_argument('--position', choices=['center', 'bottom', 'top'], 
                       default='center', help='Position des Spielers')
    parser.add_argument('--no-text', action='store_true', help='Keinen Text hinzufügen')
    parser.add_argument('--font', type=str, help='Pfad zu einer TTF-Schriftdatei')
    parser.add_argument('--number-size', type=int, default=120, help='Schriftgröße für Nummer (Standard: 120)')
    parser.add_argument('--name-size', type=int, default=60, help='Schriftgröße für Namen (Standard: 60)')
    
    args = parser.parse_args()
    
    print("🏆 Mannschaftsfoto-Prozessor gestartet!")
    print("=" * 50)
    
    # Ordner erstellen
    setup_directories()
    
    if args.setup:
        print("\n📁 Ordner-Setup abgeschlossen!")
        print("\nNächste Schritte:")
        print("1. Spielerbilder in 'input_players/' kopieren")
        print("   Format: 'Nummer_Vorname_Nachname.jpg' (z.B. '36_Moritz_Breves.jpg')")
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
        add_text = not args.no_text
        text_info = "mit Text" if add_text else "ohne Text"
        print(f"\n🖼️ Schritt 2: Mit Hintergrund kombinieren ({text_info}, Position: {args.position})...")
        combine_with_background('output_cutouts', 'backgrounds', 'final_results', 
                               args.position, add_text, args.font, args.number_size, args.name_size)
    
    print("\n✨ Alle Schritte abgeschlossen!")
    print("\nErgebnisse:")
    print("- Freigestellte Spieler: output_cutouts/")
    print("- Finale Mannschaftsbilder: final_results/")
    if not args.no_text:
        print("\n💡 Tipp: Dateinamen sollten Format 'Nummer_Vorname_Nachname.jpg' haben")
        print("   Beispiel: '36_Moritz_Breves.jpg' → Name: 'Moritz Breves', Nummer: '36'")

if __name__ == "__main__":
    main()