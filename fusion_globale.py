import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# Sources EPG
SOURCES_EPG = {
    "Samsung_FR": "https://i.mjh.nz/SamsungTVPlus/fr.xml",
    "Samsung_US": "https://i.mjh.nz/SamsungTVPlus/us.xml",
    "Pluto_FR": "https://i.mjh.nz/PlutoTV/fr.xml"
}

M3U_FILENAME = "liste_finale.m3u8"
OUTPUT_EPG = "epg_unique.xml"

def run():
    print(f"Lancement de la mise à jour : {datetime.now()}")
    
    # 1. Lire le M3U
    try:
        with open(M3U_FILENAME, 'r', encoding='utf-8') as f:
            m3u_content = f.read()
        ids = set(re.findall(r'tvg-id="([^"]+)"', m3u_content))
    except FileNotFoundError:
        print("Erreur : liste_finale.m3u8 introuvable !")
        return

    # 2. Créer le nouvel EPG
    new_root = ET.Element("tv")
    # On ajoute un petit commentaire avec l'heure pour forcer GitHub à voir un changement
    new_root.append(ET.Comment(f"MAJ: {datetime.now()}"))

    for nom, url in SOURCES_EPG.items():
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                source_root = ET.fromstring(r.content)
                for c in source_root.findall('channel'):
                    if c.get('id') in ids:
                        new_root.append(c)
                for p in source_root.findall('programme'):
                    if p.get('channel') in ids:
                        new_root.append(p)
        except Exception as e:
            print(f"Erreur sur {nom}: {e}")

    # 3. Sauvegarder l'EPG
    ET.ElementTree(new_root).write(OUTPUT_EPG, encoding='utf-8', xml_declaration=True)
    
    # 4. FORCER LA MISE A JOUR DU M3U (En ajoutant un petit commentaire à la fin)
    with open(M3U_FILENAME, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
        f.write(f"\n# MAJ: {datetime.now()}") # Cette ligne change tout pour GitHub !
    
    print("Mise à jour terminée !")

if __name__ == "__main__":
    run()
    
