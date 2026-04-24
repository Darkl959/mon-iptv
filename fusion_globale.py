import requests
import xml.etree.ElementTree as ET
import re

# On récupère les EPG de Samsung FR, US et Pluto FR
SOURCES_EPG = {
    "Samsung_FR": "https://i.mjh.nz/SamsungTVPlus/fr.xml",
    "Samsung_US": "https://i.mjh.nz/SamsungTVPlus/us.xml",
    "Pluto_FR": "https://i.mjh.nz/PlutoTV/fr.xml"
}

M3U_FILENAME = "liste_finale.m3u8"
OUTPUT_EPG = "epg_unique.xml"

def run():
    print("Ouverture du fichier M3U...")
    try:
        with open(M3U_FILENAME, 'r', encoding='utf-8') as f:
            m3u_content = f.read()
        
        # On cherche tous les tvg-id dans ton fichier
        ids = set(re.findall(r'tvg-id="([^"]+)"', m3u_content))
    except FileNotFoundError:
        print("Erreur : liste_finale.m3u8 introuvable !")
        return

    new_root = ET.Element("tv")
    
    for nom, url in SOURCES_EPG.items():
        print(f"Téléchargement de {nom}...")
        r = requests.get(url)
        if r.status_code == 200:
            source_root = ET.fromstring(r.content)
            
            # On ajoute les chaînes si elles sont dans ton M3U
            for c in source_root.findall('channel'):
                if c.get('id') in ids:
                    new_root.append(c)
            
            # On ajoute les programmes si la chaîne est dans ton M3U
            for p in source_root.findall('programme'):
                if p.get('channel') in ids:
                    new_root.append(p)

    # Sauvegarde de l'EPG
    ET.ElementTree(new_root).write(OUTPUT_EPG, encoding='utf-8', xml_declaration=True)
    print(f"Succès : {OUTPUT_EPG} généré !")

    # --- LE TRUC EN PLUS POUR FORCER LA MISE A JOUR DU M3U ---
    # On réécrit le fichier M3U pour que GitHub voie qu'il est "neuf"
    with open(M3U_FILENAME, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    print(f"Succès : {M3U_FILENAME} actualisé !")

if __name__ == "__main__":
    run()
    
