# Ajout au fichier principal GerbyTool
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, ttk
from PIL import Image, ImageTk
import os
import sys

# ==== Configuration du style Tkinter TTK ====
def set_style(root):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 10), padding=6, relief="flat", foreground="white", background="#68c2c8")
    style.map("TButton", background=[("active", "#cbcbcb"), ("!disabled", "#68c2c8")], foreground=[("active", "white"), ("!disabled", "white")])
    style.configure("Green.TButton", font=("Arial", 10), padding=6, relief="flat", foreground="white", background="#5db267")
    style.map("Green.TButton", background=[("active", "#43984d"), ("!disabled", "#5db267")], foreground=[("active", "white"), ("!disabled", "white")])
    root.configure(bg="#2E2E2E")

# ==== Fonction pour centrer une fenêtre ====
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# ==== Menu principal ====
def main_menu():
    main_root = tk.Tk()
    main_root.title("PolyTool - Menu Principal")
    center_window(main_root, 400, 550)
    set_style(main_root)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    main_root.iconbitmap(icon_path)

    tk.Label(main_root, text="Bienvenue sur PolyTool", font=("Arial", 16, "bold"), bg="#2E2E2E", fg="white").pack(pady=10)
    try:
        image_path = os.path.join(application_path, "logo.png")
        if os.path.exists(image_path):
            img = Image.open(image_path).resize((200, 200), Image.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            tk.Label(main_root, image=logo, bg="#2E2E2E").pack(pady=5)
        else:
            tk.Label(main_root, text="⚠️ Image non trouvée : logo.png", fg="red", bg="#2E2E2E").pack(pady=5)
    except Exception as e:
        print(f"Erreur image : {e}")
        tk.Label(main_root, text="⚠️ Erreur chargement image", fg="red", bg="#2E2E2E").pack(pady=5)

    # ttk.Button(main_root, text="GerbyTool", command=lambda: launch_gerbytool(main_root), width=30).pack(pady=5)
    ttk.Button(main_root, text="Traduction", command=lambda: launch_traduction(main_root), width=30).pack(pady=5)
    ttk.Button(main_root, text="Minage", command=lambda: launch_minage(main_root), width=30).pack(pady=5)
    ttk.Button(main_root, text="Salvage", command=lambda: launch_salvage(main_root), width=30).pack(pady=5)
    ttk.Button(main_root, text="Quitter", command=main_root.quit, width=30).pack(pady=10)
    main_root.mainloop()

# ==== GerbyTool ====
def launch_gerbytool(root):
    root.destroy()
    gerbytool_root = tk.Tk()
    gerbytool_root.title("GerbyTool - Comparateur de Global INI")
    center_window(gerbytool_root, 500, 450)
    set_style(gerbytool_root)
    

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    gerbytool_root.iconbitmap(icon_path)

    old_file_path = StringVar()
    new_file_path = StringVar()
    output_file_path = StringVar()
    progress = ttk.Progressbar(gerbytool_root, mode="indeterminate")

    def extract_keys(filename):
        keys, lines = set(), {}
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    stripped = line.strip()
                    if "=" in stripped and not stripped.startswith("#"):
                        key, value = stripped.split("=", 1)
                        keys.add(key.strip())
                        lines[key.strip()] = stripped
            return keys, lines
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire {filename} : {e}")
            return set(), {}

    def find_new_entries():
        if not old_file_path.get() or not new_file_path.get() or not output_file_path.get():
            messagebox.showwarning("Attention", "Veuillez sélectionner les trois fichiers.")
            return

        progress.pack(pady=5)
        progress.start()

        old_keys, _ = extract_keys(old_file_path.get())
        new_keys, new_lines = extract_keys(new_file_path.get())
        new_entries = [new_lines[key] for key in new_keys if key not in old_keys]

        progress.stop()
        progress.pack_forget()

        if new_entries:
            with open(output_file_path.get(), "w", encoding="utf-8") as file:
                file.write("\n".join(new_entries) + "\n")
            success_popup(len(new_entries))
        else:
            messagebox.showinfo("Résultat", "Aucune nouvelle entrée trouvée.")

    def success_popup(count):
        top = tk.Toplevel()
        top.title("Succès")
        top.geometry("300x150")
        set_style(top)
        icon_path = os.path.join(sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__), "icon.ico")
        top.iconbitmap(icon_path)
        top.configure(bg="#28a745")
        tk.Label(top, text=f"{count} nouvelles lignes ajoutées ✅", font=("Arial", 12), fg="white", bg="#28a745").pack(expand=True)
        ttk.Button(top, text="OK", command=top.destroy).pack(pady=10)

    for label, var in [("Ancien Global.ini :", old_file_path), ("Nouveau Global.ini :", new_file_path), ("Fichier de sortie :", output_file_path)]:
        ttk.Label(gerbytool_root, text=label, font=("Arial", 10, "bold"), foreground="white", background="#2E2E2E").pack(pady=5)
        ttk.Entry(gerbytool_root, textvariable=var, width=60).pack()
        ttk.Button(gerbytool_root, text="Parcourir", command=lambda v=var: v.set(filedialog.askopenfilename(filetypes=[("INI Files", "*.ini")]) if label != "Fichier de sortie :" else filedialog.asksaveasfilename(defaultextension=".ini", filetypes=[("INI Files", "*.ini")]))).pack(pady=2)

    ttk.Button(gerbytool_root, text="Comparer", command=find_new_entries, style="Green.TButton").pack(pady=10)
    ttk.Button(gerbytool_root, text="Retour au menu", command=lambda: return_to_main(gerbytool_root)).pack(pady=10)
    gerbytool_root.mainloop()

# ==== Traduction ==== 
def launch_traduction(root):
    root.destroy()
    try:
        from app_traduction import TraductionApp
    except ImportError:
        messagebox.showerror("Erreur", "Impossible de charger l'installateur de traduction.")
        return_to_main(root)
        return
    traduction_root = tk.Tk()
    traduction_root.title("TraductionTMN - Installateur de Traduction")
    traduction_root.geometry("750x600")
    app = TraductionApp(traduction_root)
    ttk.Button(traduction_root, text="Retour au menu", command=lambda: return_to_main(traduction_root)).pack(pady=10)
    traduction_root.mainloop()

# ==== Minage ====
def launch_minage(root):
    root.destroy()
    minage_root = tk.Tk()
    minage_root.title("PolyTool - Minage")
    center_window(minage_root, 400, 450)
    set_style(minage_root)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    minage_root.iconbitmap(icon_path)

    # Conteneur centré
    frame = tk.Frame(minage_root, bg="#2E2E2E")
    frame.pack(expand=True)

    ttk.Button(frame, text="Aaron Halo", command=lambda: launch_aaron(minage_root), width=30).pack(pady=5)
    ttk.Button(frame, text="Optimiseur Raffinerie", command=ouvrir_optimiseur_raffinerie, width=30).pack(pady=5)
    ttk.Button(frame, text="📄 Fiche Golem", command=ouvrir_fiche_golem, width=30).pack(pady=5)
    # ttk.Button(frame, text="📄 Fiche ATL Geo", command=ouvrir_fiche_atl_geo, width=30).pack(pady=5)
    ttk.Button(frame, text="📄 Fiche Prospector", command=ouvrir_fiche_prospector, width=30).pack(pady=5)
    ttk.Button(frame, text="📄 Fiche MOLE", command=ouvrir_fiche_mole, width=30).pack(pady=5)
    ttk.Button(frame, text="Retour au PolyTool", command=lambda: return_to_main(minage_root), width=30).pack(pady=5)



# ==== Aaron Halo ====
def launch_aaron(root):
    root.destroy()
    aaron_root = tk.Tk()
    aaron_root.title("Aaron Halo")
    center_window(aaron_root, 600, 400)
    set_style(aaron_root)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    aaron_root.iconbitmap(icon_path)

    data = [
    ("CRU-L1", "ARC-L5", 13252000, 11158000),
    ("ARC-L5", "CRU-L1", 14635000, 12541000),
    ("ARC-L1", "MICROTECH", 49996000, 47695000),
    ("ARC-L1", "CRU-L4", 16368000, 14103000),
    ("ARC-L1", "CRU-L3", 14879000, 13235000),
    ("ARC-L1", "CRUSADER", 34347000, 33097000),
    ("ARC-L1", "CRU-L5", 40438000, 39351000),
    ("HUR-L1", "ARC-L3", 9352000, 8296000),
    ("HUR-L1", "ARC-L5", 9837000, 8797000),
    ("HUR-L1", "DELAMAR", 1329000, 170),
    ("HUR-L1", "MICROTECH", 25582000, 24210000),
    ("HUR-L1", "ARC-L4", 9303000, 8253000),
    ("HUR-L2", "ARCCORP", 10230000, 8769000),
    ("HUR-L2", "DELAMAR", 1502000, 170),
    ("HUR-L2", "ARC-L5", 11208000, 9935000),
    ("HUR-L2", "MICROTECH", 26965000, 25404000),
    ("HUR-L2", "ARC-L4", 9282000, 8321000),
    ("MIC-L1", "CRUSADER", 33573000, 32847000),
    ("MIC-L1", "ARCCORP", 29828000, 26933000),
    ("MIC-L1", "DELAMAR", 3516000, 170),
    ("MIC-L1", "CRU-L3", 5772000, 4005000),
    ("MIC-L1", "HURSTON", 14010000, 12990000),
    ("MIC-L1", "HUR-L4", 8114000, 7402000),
    ("CRU-L4", "ARC-L1", 9898000, 7634000),
    ("CRUSADER", "ARC-L1", 6554000, 5304000),
    ("CRU-L5", "ARC-L1", 5816000, 4730000),
    ("ARC-L1", "HURSTON", 14708000, 13393000),
    ("HURSTON", "ARC-L1", 6917000, 5602000),
    ("MICROTECH", "ARC-L1", 9718000, 7419000),
    ("CRU-L3", "ARC-L1", 9477000, 7833000),
    ("ARC-L3", "HUR-L1", 31064000, 30009000),
    ("DELAMAR", "HUR-L1", 28653000, 27324000),
    ("MICROTECH", "HUR-L1", 14539000, 13168000),
    ("ARC-L4", "HUR-L1", 9389000, 8340000),
    ("HUR-L1", "ARCCORP", 10439000, 8893000),
    ("ARCCORP", "HUR-L1", 14346000, 12800000),
    ("ARC-L5", "HUR-L1", 25826000, 24786000),
    ("DELAMAR", "HUR-L2", 30679000, 29177000),
    ("MICROTECH", "HUR-L2", 12703000, 11141000),
    ("ARC-L4", "HUR-L2", 6875000, 5915000),
    ("ARCCORP", "HUR-L2", 12539000, 12075650),
    ("ARC-L5", "HUR-L2", 12660000, 11387000),
    ("ARCCORP", "MIC-L1", 28710000, 25815000),
    ("CRU-L3", "MIC-L1", 28823000, 25055000),
    ("HURSTON", "MIC-L1", 21278000, 20258000),
    ("HUR-L4", "MIC-L1", 18850000, 18138000),
    ("CRUSADER", "MIC-L1", 20449000, 19723000),
    ("DELAMAR", "MIC-L1", 34311000, 30795000),
]
    
    point_depart = StringVar()
    result_label = tk.Label(aaron_root, text="", font=("Arial", 10), fg="white", bg="#2E2E2E")

    def update_arrivees(event=None):
        arrivees = [(d[1], d[2], d[3]) for d in data if d[0] == point_depart.get()]
        result = "\n".join([f"Vers {arr} : {min_km:,} km → {max_km:,} km" for arr, min_km, max_km in arrivees])
        result_label.config(text=result or "Aucun itinéraire trouvé.")

    ttk.Label(aaron_root, text="Point de départ :", foreground="white", background="#2E2E2E").pack(pady=5)
    combo = ttk.Combobox(aaron_root, textvariable=point_depart, values=sorted(set(d[0] for d in data)), state="readonly")
    combo.pack()
    combo.bind("<<ComboboxSelected>>", update_arrivees)

    result_label.pack(pady=15)
    ttk.Button(aaron_root, text="Retour au PolyTool", command=lambda: return_to_main(aaron_root)).pack(pady=10)

# ==== Retour au menu ====
def return_to_main(current_root):
    current_root.destroy()
    main_menu()

# ==== Fiche Prospector ====
def ouvrir_fiche_prospector():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - Prospector")
    center_window(fiche_win, 600, 700)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """\
🛠️ Fiche Pratique — Minage en Prospector

⚙️ Loadout recommandé
• Laser : Helix 1
• Modules actifs :
  - Surge
  - Stampede
  (Alternative : Riger C3 + Stampede pour plus de stabilité)

🎒 Modules supplémentaires :
• Riger C3
• Focus 3
• Surge (supplémentaire)
• Stampede (supplémentaire)

🧪 Gadgets :
• Sabir – Réduit la résistance des roches
• Wave Shift – Élargit la fenêtre de minage
• Bormax – Réduit l’instabilité et améliore le clustering
• OptiMax – (optionnel) clustering ++

🧍‍♂️ Équipement personnel :
• Armure lourde
• Sac à dos large
• (Optionnel) Boîte 1 SCU dans la soute

📈 Performances :
• Casse roches jusqu’à 30K
• Setup avancé, efficace et agressif
"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)


# ==== Fiche Mole ====
def ouvrir_fiche_mole():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - MOLE")
    center_window(fiche_win, 600, 750)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """\
🛠️ Fiche Pratique — Minage en MOLE (solo)

⚙️ Configuration des lasers :
• Avant : Impact 2
  - Modules : Riger C3, Surge, Stampede
• Droite : Hofstad S2
  - Modules : Riger C3, Stampede
• Gauche : Helix 2
  - Modules : Riger C3, Surge, Stampede

🎯 Objectif des lasers :
• Helix 2 : pour casser les plus gros blocs
• Hofstad : polyvalent, petites et moyennes roches
• Impact 2 : excellent pour extraction et portée

🎒 Modules dans le sac :
• 5 x Surge
• 3 x Stampede
• 1 x Focus 3
• 1 x Riger C2 (pour remplacer un Surge si la fenêtre devient trop petite)

🧪 Gadgets :
• Bormax – Pour réduire l’instabilité et améliorer le clustering
• 2 x Sabir – Pour réduire la résistance et élargir la fenêtre de minage

🧍‍♂️ Équipement personnel :
• Armure lourde
• Sac à dos large
• (Optionnel) Boîte 1 SCU dans le vaisseau pour stock de secours

💡 Astuce :
• Les modules ne se cumulent pas (pas 2x Riger C3)
• Le Hofstad a un large green zone, idéal pour casser rapidement

📈 Performances :
• Capable de casser tous types de roches seul
• Setup très agressif, modulable selon la résistance
"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# ==== Fiche Golem ====
def ouvrir_fiche_golem():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - Drake Golem")
    center_window(fiche_win, 600, 750)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """
🛠️ Fiche Pratique — Minage en Drake Golem

⚙️ Laser : Pitman (exclusif)
• Puissance : 3150 (comme Helix 1)
• Puissance min : 20%
• Portée optimale : 40m
• +25% résistance du rocher
• +35% instabilité
• +40% green zone
• -40% vitesse de charge
• Slots de module : 2

🔧 Modules recommandés :
• 2 x Riger C3 (pour compenser la résistance accrue)
• Stampede (pour stabiliser l’instabilité accrue)
• Focus (agrandit la fenêtre de minage)

💡 Idéal pour casser des gros rochers avec un bon setup et une bonne gestion de l’instabilité.
"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# ==== Fiche ATL GEO ====
def ouvrir_fiche_atl_geo():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - ATL Geo")
    center_window(fiche_win, 600, 750)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """
🛠️ Fiche Pratique — Minage en ATL Geo

⚠️ En attente d'informations officielles détaillées.

Le ATL Geo est un vaisseau de minage prévu pour offrir une alternative avancée et modulaire au MOLE.
Dès que les spécificités techniques (lasers, slots, comportements) seront connues, cette fiche sera mise à jour.

"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# ==== Salvage ====
def launch_salvage(root):
    root.destroy()
    salvage_root = tk.Tk()
    salvage_root.title("PolyTool - Salvage")
    center_window(salvage_root, 400, 400)
    set_style(salvage_root)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    salvage_root.iconbitmap(icon_path)

    frame = tk.Frame(salvage_root, bg="#2E2E2E")
    frame.pack(expand=True)

    ttk.Button(frame, text="Aaron Halo", command=lambda: launch_aaron(salvage_root), width=30).pack(pady=5)
    ttk.Button(frame, text="Estimation du prix", command=lambda: estimation_prix_window(salvage_root), width=30).pack(pady=5)
    ttk.Button(frame, text="📄 Fiche Misc Fortune", command=ouvrir_fiche_misc_fortune, width=30).pack(pady=5)
    ttk.Button(frame, text="📄 Fiche Vulture", command=ouvrir_fiche_vulture, width=30).pack(pady=5)
    ttk.Button(frame, text="📄 Fiche Reclaimer", command=ouvrir_fiche_reclaimer, width=30).pack(pady=5)
    ttk.Button(frame, text="Retour au PolyTool", command=lambda: return_to_main(salvage_root), width=30).pack(pady=10)

def ouvrir_fiche_misc_fortune():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - Misc Fortune")
    center_window(fiche_win, 600, 750)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """\
🛠️ Fiche Pratique — Salvage en Misc Fortune

🔧 Module recommandé :
• Roller Scraper – Accélère le décapage (utile car le Fortune n’a qu’un seul scraper).

📦 Builds recommandés :

⚙️ **Stealth Build (furtivité)**
• Objectif : Signature la plus basse possible
• Résultat : IR ~6.8km / EM ~8.3km (vs 15.2km / 22.4km par défaut)
• Boucliers : 3x Shimmer (Grade C, stealth)
• Réacteur : Circuit (Grade C stealth)
• Refroidissement : Icebox (Grade B stealth)
• QDrive : Firefox (Grade B competition) – pour sa vitesse de spool
→ Idéal pour rester invisible en champ d’astéroïdes.

⚙️ **Shield Tank Build**
• Objectif : Tenir sous feu laser
• Boucliers : 3x Targa (Grade C competition) – très bonne résistance
• Réacteur : Genoa (Grade A industriel)
• Refroidissement : IceDrive (Grade C competition)
• QDrive : Goliath (Grade C, fiable et robuste)

⚙️ **Résilience Build**
• Objectif : Encaisser les dégâts balistiques (HP composants)
• Boucliers : 3x Palace (Grade A industriel) – excellent HP composant
• Réacteur : Genoa (Grade A industriel)
• Refroidissement : SnowPack (Grade A industriel)
• QDrive : Colossus (Grade B industriel)

💡 Tous ces builds peuvent être mixés selon tes besoins !
"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# ==== Fiche Vulture ====
def ouvrir_fiche_vulture():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - Drake Vulture")
    center_window(fiche_win, 600, 750)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """
🛠️ Fiche Pratique — Salvage en Drake Vulture

🌌 Spot de farm : Asteroid belt entre CRU-L4 et CRU-L5 (coupe le quantum à ~11.0GM)

🔧 Modules recommandés :
• Abrade Gripen module (Platinum Bay)

🎮 Contrôles utiles :
• ALT+A / ALT+T : Sélection des modules gauche/droite
• ALT+S : Activation des 2 modules
• ALT + molette : Écartement des lasers
• G : Mode gimbal

📊 Astuces :
• Utilise le module de grappin pour rapprocher les panneaux
• Les slivers (petits débris) donnent peu mais peuvent aider à finir le cargo
• Tirer sur les panneaux après épuisement pour qu’ils ne polluent pas les scans (optionnel)

💭 Conseil : Utilise le multi-tool avec module tractor pour placer les caisses sur la grille
"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# ==== Fiche Reclaimer ====
def ouvrir_fiche_reclaimer():
    fiche_win = tk.Toplevel()
    fiche_win.title("Fiche Pratique - Aegis Reclaimer")
    center_window(fiche_win, 600, 850)
    set_style(fiche_win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    fiche_win.iconbitmap(icon_path)

    text = tk.Text(fiche_win, wrap=tk.WORD, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
    fiche = """
🛠️ Fiche Pratique — Salvage en Aegis Reclaimer

💪 Vaisseau robuste mais lent, à utiliser en groupe ou pour de longues sessions.

🔧 Modules :
• Abrade 
• Modules tracteur

🔁 Optimisation :
• Passer en mode VTOL, train rentré, boost activé pour monter rapidement
• Mettre la puissance au maximum sur les moteurs
• Possibilité de changer le quantum drive (attention à bien remettre le jump drive ensuite)

🚨 Astuces maniement :
• Utiliser la section médiane de la vitre pour estimer les 40-50m de portée optimale
• Le grapping du Reclaimer est à droite, bien aligner les panneaux
• Passer du mode scraping au tracteur sans éteindre le module actif

🏛️ Traitement :
• Bien positionner les débris devant la trappe à environ 43m
• Ajuster en hauteur pour rester dans la zone verte (max 20% rendement)
• Trop proche ou mal aligné = pertes de matériaux

💼 Stockage & Vente :
• Utiliser le bouton "Open All Doors" pour accélérer les déplacements internes
• Utiliser la trappe arrière pour déposer les caisses directement en hangar
• Stocker le vaisseau pour transférer automatiquement les caisses si elles sont bien placées sur la grille

🎟️ Recyclage :
• Auto-eject active pour sortir les caisses tant qu'il y a de la matière
• Matériaux obtenus : construction mats, composites, etc. peu chers mais utiles parfois

⚠️ Attention :
• Éviter de cogner les panneaux contre la pince
• Ne pas perdre les modules de tracteur exclusifs !
"""
    text.insert(tk.END, fiche)
    text.config(state=tk.DISABLED)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)


# ==== Fenêtre Estimation du Prix ====
def estimation_prix_window(root):
    root.destroy()
    win = tk.Tk()
    win.title("Estimation du prix")
    center_window(win, 400, 300)
    set_style(win)

    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    win.iconbitmap(icon_path)

    uex_prices = {
        "Matériaux de construction": 2133,
        "Matériaux de recyclage": 10800
    }

    qty_construction = tk.StringVar()
    qty_recyclage = tk.StringVar()
    result_label = tk.Label(win, text="", font=("Arial", 10), fg="white", bg="#2E2E2E")

    def calculer():
        try:
            q1 = float(qty_construction.get() or 0)
            q2 = float(qty_recyclage.get() or 0)
            total = q1 * uex_prices["Matériaux de construction"] + q2 * uex_prices["Matériaux de recyclage"]
            result_label.config(text=f"Estimation totale : {total:,.2f} aUEC")
        except:
            messagebox.showerror("Erreur", "Veuillez entrer des quantités valides")

    def reset():
        qty_construction.set("")
        qty_recyclage.set("")
        result_label.config(text="")

    ttk.Label(win, text="Matériaux de construction", background="#2E2E2E", foreground="white").pack(pady=5)
    ttk.Entry(win, textvariable=qty_construction).pack()
    ttk.Label(win, text="Matériaux de recyclage", background="#2E2E2E", foreground="white").pack(pady=5)
    ttk.Entry(win, textvariable=qty_recyclage).pack()

    ttk.Button(win, text="Calculer", command=calculer).pack(pady=5)
    ttk.Button(win, text="Remise à zéro", command=reset).pack(pady=5)
    result_label.pack(pady=10)
    ttk.Button(win, text="Retour au PolyTool", command=lambda: return_to_main(win)).pack(pady=10)

# ==== Optimiseur Raffinerie ====

def ouvrir_optimiseur_raffinerie():
    import tkinter as tk
    from tkinter import ttk, messagebox
    import os, sys
    from data_raffinerie import bonus_malus_dict, all_stations

    minerais = sorted(bonus_malus_dict.keys())  # tri alphabétique

    def calculer_rendement(minerais_quantites):
        resultats = []
        for station in all_stations:
            total_valeur = 0
            for minerai, quantite in minerais_quantites.items():
                data = bonus_malus_dict.get(minerai, {})
                prix = data.get("Refined", 0)
                bonus = data.get(station, 0)
                total_valeur += prix * (1 + bonus) * quantite
            resultats.append((station, round(total_valeur, 2)))
        return sorted(resultats, key=lambda x: x[1], reverse=True)[:3]

    win = tk.Toplevel()
    win.title("Optimiseur de Raffinerie")
    set_style(win)

    # Icône + centrage
    application_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    win.iconbitmap(icon_path)
    center_window(win, 500, 630)

    scrollable_width = 150
    frame = ttk.Frame(win)
    frame.pack(pady=10)

    entries = {}

    # Frame contenant les deux colonnes
    form_frame = ttk.Frame(frame, width=scrollable_width * 2 + 40)
    form_frame.pack(anchor="center", pady=10)

    # Répartition en 2 colonnes
    milieu = len(minerais) // 2
    col1 = minerais[:milieu]
    col2 = minerais[milieu:]

    colonnes_frame = ttk.Frame(form_frame)
    colonnes_frame.pack()

    col_frame_1 = ttk.Frame(colonnes_frame)
    col_frame_1.pack(side="left", padx=10)

    col_frame_2 = ttk.Frame(colonnes_frame)
    col_frame_2.pack(side="left", padx=10)

    # Ajout des champs dans chaque colonne
    for minerai in col1:
        row = ttk.Frame(col_frame_1)
        ttk.Label(row, text=minerai, width=14).pack(side="left", padx=2)
        ent = ttk.Entry(row, width=6)
        ent.pack(side="left")
        entries[minerai] = ent
        row.pack(anchor="w", pady=1)

    for minerai in col2:
        row = ttk.Frame(col_frame_2)
        ttk.Label(row, text=minerai, width=14).pack(side="left", padx=2)
        ent = ttk.Entry(row, width=6)
        ent.pack(side="left")
        entries[minerai] = ent
        row.pack(anchor="w", pady=1)

    result_label = ttk.Label(win, text="", font=("Arial", 12), justify="left")
    result_label.pack(pady=10)

    # Actions
    def on_calcul():
        try:
            minerais_quantites = {
                minerai: float(entry.get())
                for minerai, entry in entries.items()
                if entry.get().strip() != "" and float(entry.get()) > 0
            }
            if not minerais_quantites:
                raise ValueError("Aucun minerai valide saisi")

            top3 = calculer_rendement(minerais_quantites)
            texte = "Top 3 des raffineries les plus rentables :\n"
            for i, (station, valeur) in enumerate(top3, start=1):
                texte += f"{i}. {station} : {valeur:,.2f} aUEC\n"
            result_label.config(text=texte)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def reset_champs():
        for entry in entries.values():
            entry.delete(0, tk.END)

    ttk.Button(win, text="Calculer", command=on_calcul).pack(pady=5)
    ttk.Button(win, text="🧹 Réinitialiser les champs", command=reset_champs).pack(pady=(0, 10))


# ==== Lancement ====
if __name__ == "__main__":
    main_menu()
