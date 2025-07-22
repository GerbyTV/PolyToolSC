import os
import sys
import requests
import hashlib
import shutil
import time
import re
import winreg
from tkinter import Tk, filedialog, StringVar, messagebox, ttk, Frame, Entry
from PIL import Image, ImageTk

# ==== Configuration du style Tkinter TTK ====
def set_style(root):
    style = ttk.Style()
    style.theme_use("clam")

    # 🔹 Style des boutons BLEUS
    style.configure("TButton", font=("Arial", 10), padding=6, relief="flat", foreground="white", background="#68c2c8")
    style.map("TButton",
              background=[("active", "#cbcbcb"), ("!disabled", "#68c2c8"), ("disabled", "#cbcbcb")],
              foreground=[("active", "white"), ("!disabled", "white"), ("disabled", "black")])  

    # 🔹 Style du bouton "Mettre à jour" (VERT)
    style.configure("Update.TButton", font=("Arial", 10), padding=6, relief="flat", foreground="white", background="#5db267")
    style.map("Update.TButton",
              background=[("active", "#43984d"), ("!disabled", "#5db267"), ("disabled", "#cbcbcb")], 
              foreground=[("active", "white"), ("!disabled", "white"), ("disabled", "black")])  

    # 🔹 Style du bouton "Supprimer" (ROUGE)
    style.configure("Delete.TButton", font=("Arial", 10), padding=6, relief="flat", foreground="white", background="#b45959")
    style.map("Delete.TButton",
              background=[("active", "#874545"), ("!disabled", "#b45959"), ("disabled", "#cbcbcb")],  
              foreground=[("active", "white"), ("!disabled", "white"), ("disabled", "black")])  

    root.configure(bg="#2E2E2E")  

class TraductionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Installeur de Traduction - Star Citizen")

        # Obtenez les dimensions de l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Définissez la taille de la fenêtre
        window_width = 750
        window_height = 700

        # Calculez la position x, y pour centrer la fenêtre
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Définissez la géométrie de la fenêtre
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        set_style(self.root)

        # Gestion du chemin pour PyInstaller
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(__file__)

        # Définir l'icône de la fenêtre
        icon_path = os.path.join(application_path, "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"⚠️ Icône non trouvée : {icon_path}")

        # Variables
        self.folder_path = StringVar()
        self.version_text = StringVar(value="Aucune version détectée")

        # URLs des fichiers hébergés sur GitHub
        self.global_ini_url = "https://raw.githubusercontent.com/GerbyTV/PolyToolSC/main/global.ini"
        self.user_cfg_url = "https://raw.githubusercontent.com/GerbyTV/PolyToolSC/main/user.cfg"

        # 📌 **Cadre principal**
        main_frame = Frame(self.root, bg="#2E2E2E")
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 📌 **Sélection du dossier**
        ttk.Label(main_frame, text="Choisissez le dossier cible : (Live, PTU, EPTU)", foreground="white", background="#2E2E2E").pack(pady=5)
        ttk.Button(main_frame, text="Parcourir", command=self.select_folder).pack(pady=5)
        ttk.Label(main_frame, textvariable=self.folder_path, foreground="white", background="#2E2E2E").pack(pady=5)

        # 📌 **Affichage de la version détectée**
        # ttk.Label(main_frame, text="Version détectée :", foreground="white", background="#2E2E2E").pack(pady=5)
        self.version_label = ttk.Label(main_frame, textvariable=self.version_text, foreground="white", background="#2E2E2E")
        self.version_label.pack(pady=5)

        # 📌 **Boutons principaux**
        button_frame = Frame(main_frame, bg="#2E2E2E")
        button_frame.pack(pady=10)

        self.install_button = ttk.Button(button_frame, text="Installer", command=self.install_files, state="disabled")
        self.install_button.pack(side="left", padx=5)

        self.update_button = ttk.Button(button_frame, text="Mettre à jour", command=self.update_global_ini, state="disabled", style="Update.TButton")
        self.update_button.pack(side="left", padx=5)

        self.delete_button = ttk.Button(button_frame, text="Supprimer la traduction", command=self.delete_translation, state="disabled", style="Delete.TButton")
        self.delete_button.pack(side="left", padx=5)

        # 📌 **Champ ID Terminal**
        ttk.Label(main_frame, text="ID du Terminal :", foreground="white", background="#2E2E2E").pack(pady=5)
        self.terminal_id_entry = ttk.Entry(main_frame, width=10)
        self.terminal_id_entry.pack(pady=5)

        # 📌 Sélection du système stellaire
        ttk.Label(main_frame, text="Système stellaire :", foreground="white", background="#2E2E2E").pack(pady=5)
        self.star_systems = StringVar()
        self.star_systems_combobox = ttk.Combobox(main_frame, textvariable=self.star_systems, state="readonly")
        self.star_systems_combobox.pack(pady=5)
        self.star_systems_combobox.bind("<<ComboboxSelected>>", self.update_terminals_list)

        # 📌 Barre de recherche pour les terminaux
        ttk.Label(main_frame, text="Rechercher un terminal :", foreground="white", background="#2E2E2E").pack(pady=5)
        self.search_var = StringVar()
        self.search_entry = ttk.Entry(main_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(pady=5)
        self.search_var.trace("w", self.filter_terminals_list)

        # 📌 Sélection du terminal
        ttk.Label(main_frame, text="Terminal :", foreground="white", background="#2E2E2E").pack(pady=5)
        self.terminals = StringVar()
        self.terminals_combobox = ttk.Combobox(main_frame, textvariable=self.terminals, state="readonly")
        self.terminals_combobox.pack(pady=5)
        self.terminals_combobox.bind("<<ComboboxSelected>>", self.set_terminal_id)

        # 📌 **Bouton de mise à jour des prix**
        self.update_prices_button = ttk.Button(main_frame, text="Mise à jour des prix", command=self.update_prices, state="disabled")
        self.update_prices_button.pack(pady=10)

        # 📌 **Bouton Quitter et Retour Menu**
        button_frame = Frame(main_frame, bg="#2E2E2E")
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Quitter", command=self.root.quit).pack(side="left", padx=10)

        self.root.update()

        # Charger les données des terminaux
        self.load_terminals_data()

        # Charger le chemin du dossier depuis le registre
        self.load_folder_path_from_registry()
        self.check_version_by_hash()

    def select_folder(self):
        """Permet à l'utilisateur de sélectionner un dossier."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.save_folder_path_to_registry(folder_selected)
            self.check_installation_status()
            self.check_version_by_hash()

    def save_folder_path_to_registry(self, folder_path):
        """Enregistre le chemin du dossier dans le registre Windows."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\StarCitizenTraduction", 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\StarCitizenTraduction")

        winreg.SetValueEx(key, "FolderPath", 0, winreg.REG_SZ, folder_path)
        winreg.CloseKey(key)

    def load_folder_path_from_registry(self):
        """Charge le chemin du dossier depuis le registre Windows."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\StarCitizenTraduction", 0, winreg.KEY_READ)
            folder_path = winreg.QueryValueEx(key, "FolderPath")[0]
            winreg.CloseKey(key)
            self.folder_path.set(folder_path)
            self.check_installation_status()
        except FileNotFoundError:
            pass

    def install_files(self):
        """Installe les fichiers global.ini et user.cfg dans les dossiers LIVE et/ou PTU."""
        base_path = self.folder_path.get()
        if not base_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier.")
            return

        # Détection des branches disponibles
        branches = []
        basename = os.path.basename(base_path).upper()
        if basename in ["LIVE", "PTU"]:
            branches.append(basename)
            # Ajouter le dossier frère si présent
            sibling = "PTU" if basename == "LIVE" else "LIVE"
            sibling_path = os.path.join(os.path.dirname(base_path), sibling)
            if os.path.isdir(sibling_path):
                branches.append(sibling)
            base_folder = os.path.dirname(base_path)
        else:
            base_folder = base_path
            for branch in ["LIVE", "PTU"]:
                if os.path.isdir(os.path.join(base_path, branch)):
                    branches.append(branch)

        if not branches:
            messagebox.showwarning("Erreur", "Aucun dossier LIVE ou PTU trouvé.")
            return

        for branch in branches:
            install_path = os.path.join(base_folder, branch)
            french_path = self.create_directories(install_path)

            global_ini_path = os.path.join(french_path, "global.ini")
            self.download_file(self.global_ini_url, global_ini_path)

            user_cfg_path = os.path.join(install_path, "user.cfg")
            self.download_file(self.user_cfg_url, user_cfg_path)

        self.show_success_popup("Installation dans LIVE/PTU terminée avec succès. ✅")
        self.check_installation_status()
        self.check_version_by_hash()


    def update_global_ini(self):
        """Met à jour le fichier global.ini dans les dossiers LIVE et/ou PTU s'ils sont installés."""
        base_path = self.folder_path.get()
        if not base_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier.")
            return

        # Détection des branches disponibles
        branches = []
        basename = os.path.basename(base_path).upper()
        if basename in ["LIVE", "PTU"]:
            branches.append(basename)
            # Ajouter le dossier frère si présent
            sibling = "PTU" if basename == "LIVE" else "LIVE"
            sibling_path = os.path.join(os.path.dirname(base_path), sibling)
            if os.path.isdir(sibling_path):
                branches.append(sibling)
            base_folder = os.path.dirname(base_path)
        else:
            base_folder = base_path
            for branch in ["LIVE", "PTU"]:
                if os.path.isdir(os.path.join(base_path, branch)):
                    branches.append(branch)

        if not branches:
            messagebox.showwarning("Erreur", "Aucun dossier LIVE ou PTU trouvé.")
            return

        for branch in branches:
            install_path = os.path.join(base_folder, branch)
            french_path = os.path.join(install_path, "data", "Localization", "french_(france)")
            if not os.path.exists(french_path):
                continue  

            global_ini_path = os.path.join(french_path, "global.ini")
            self.download_file(self.global_ini_url, global_ini_path)

        self.show_success_popup("Mise à jour réussie pour LIVE et PTU ✅")
        self.check_version_by_hash()


    def update_prices(self):
        """Met à jour les prix dans global.ini en utilisant les données raffinées et brutes de l'API UEX."""
        import re, requests, os
        from tkinter import messagebox

        base_path = self.folder_path.get()
        if not base_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier.")
            return

        global_ini_path = os.path.join(base_path, "data", "Localization", "french_(france)", "global.ini")
        if not os.path.exists(global_ini_path):
            messagebox.showwarning("Erreur", "Le fichier global.ini n'a pas été trouvé. Installez-le d'abord.")
            return

        id_terminal = self.terminal_id_entry.get()
        if not id_terminal.isdigit():
            self.show_error_popup("L'ID du terminal doit être un nombre.")
            return
        id_terminal = int(id_terminal)

        access_token = "***"
        headers = {"Authorization": f"Bearer {access_token}"}

        prix_ressources = {}

        # 📡 1. Produits raffinés
        try:
            url_standard = "https://api.uexcorp.space/2.0/commodities_prices"
            response = requests.get(url_standard, headers=headers, params={"id_terminal": id_terminal})
            response.raise_for_status()
            data_standard = response.json()['data']
            for item in data_standard:
                slug = item['commodity_slug']
                prix = item['price_sell']
                if prix > 0:
                    prix_ressources[f"items_commodities_{slug}"] = prix
        except requests.exceptions.RequestException as e:
            self.show_error_popup(f"Erreur API (commodities_prices) : {e}")
            return

        # 📡 2. Produits bruts (ore, raw, etc.) via API globale
        try:
            url_raw = "https://api.uexcorp.space/2.0/commodities_raw_prices_all"
            response = requests.get(url_raw)
            response.raise_for_status()
            data_raw = response.json().get('data', [])
            for item in data_raw:
                if (
                    item.get('id_terminal') == id_terminal
                    and 'commodity_name' in item
                    and isinstance(item.get('price_sell'), (int, float))
                ):
                    slug = (
                        item['commodity_name']
                        .lower()
                        .replace(' (', '_')
                        .replace(')', '')
                        .replace(' ', '_')
                    )
                    prix = item['price_sell']
                    key = f"items_commodities_{slug}"
                    if prix > 0 and key not in prix_ressources:
                        prix_ressources[key] = prix
        except requests.exceptions.RequestException as e:
            self.show_error_popup(f"Erreur API (commodities_raw_prices_all) : {e}")
            return

        # 📝 Mise à jour du .ini
        try:
            with open(global_ini_path, 'r', encoding='utf-8') as file:
                lignes = file.readlines()

            updated_count = 0

            with open(global_ini_path, 'w', encoding='utf-8') as file:
                for ligne in lignes:
                    match = re.match(r'^(items_commodities_\w+)\s*=\s*(.+?)\s*\(\d+\s*aUEC\s*/\s*scu\s*\)', ligne)
                    if match:
                        nom_cle, nom_affichage = match.group(1), match.group(2)
                        if nom_cle in prix_ressources:
                            prix = prix_ressources[nom_cle]
                            nouvelle_ligne = re.sub(
                                r'\(\d+\s*aUEC\s*/\s*scu\s*\)',
                                f'({int(prix)}aUEC/scu)',
                                ligne
                            )
                            file.write(nouvelle_ligne)
                            print(f"🔁 {nom_cle} mis à jour avec {prix}aUEC")
                            updated_count += 1
                            continue
                    file.write(ligne)

            self.show_success_popup(f"{updated_count} ressources mises à jour avec succès pour le terminal {id_terminal}.")

        except Exception as e:
            self.show_error_popup(f"Erreur lors de la mise à jour du fichier : {e}")


    def delete_translation(self):
        """Supprime les fichiers de traduction du dossier sélectionné."""
        base_path = self.folder_path.get()
        if not base_path:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier.")
            return

        french_path = os.path.join(base_path, "data", "Localization", "french_(france)")
        user_cfg_path = os.path.join(base_path, "user.cfg")

        deleted_anything = False

        if os.path.exists(french_path):
            shutil.rmtree(french_path)
            deleted_anything = True

        if os.path.exists(user_cfg_path):
            os.remove(user_cfg_path)
            deleted_anything = True

        if deleted_anything:
            self.show_success_popup("La traduction a été supprimée avec succès. ✅")
        else:
            messagebox.showwarning("Erreur", "Aucun fichier de traduction à supprimer.")

        self.check_installation_status()
        self.check_version_by_hash()

    def load_terminals_data(self):
        """Charge les données des terminaux depuis l'API."""
        api_url = "https://api.uexcorp.space/2.0/terminals"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            self.terminals_data = data['data']
            star_systems = sorted({item['star_system_name'] for item in self.terminals_data if item['star_system_name'] is not None})
            self.star_systems_combobox['values'] = star_systems
            self.adjust_combobox_width(self.star_systems_combobox, star_systems)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur API", f"Impossible de récupérer les données des terminaux : {e}")

    def update_terminals_list(self, event):
        """Met à jour la liste des terminaux en fonction du système stellaire sélectionné."""
        selected_system = self.star_systems.get()
        self.terminals_combobox['values'] = []

        if selected_system and selected_system != "Sélectionnez un système stellaire":
            terminals_in_system = sorted([item['name'] for item in self.terminals_data
                                           if item['star_system_name'] == selected_system and item['name'] is not None])
            self.terminals_combobox['values'] = terminals_in_system
            self.adjust_combobox_width(self.terminals_combobox, terminals_in_system)
            self.filter_terminals_list()

    def filter_terminals_list(self, *args):
        """Filtre la liste des terminaux en fonction de la recherche."""
        search_term = self.search_var.get().lower()
        selected_system = self.star_systems.get()
        self.terminals_combobox['values'] = []

        if selected_system and selected_system != "Sélectionnez un système stellaire":
            filtered_terminals = sorted([item['name'] for item in self.terminals_data
                                         if item['star_system_name'] == selected_system and search_term in item['name'].lower()])
            self.terminals_combobox['values'] = filtered_terminals
            self.adjust_combobox_width(self.terminals_combobox, filtered_terminals)

    def set_terminal_id(self, event):
        """Remplit la case de l'ID du terminal en fonction du terminal sélectionné."""
        selected_terminal = self.terminals.get()
        if selected_terminal and selected_terminal != "Sélectionnez un terminal":
            for item in self.terminals_data:
                if item['name'] == selected_terminal:
                    self.terminal_id_entry.delete(0, 'end')
                    self.terminal_id_entry.insert(0, str(item['id']))
                    break

    def create_directories(self, base_path):
        french_path = os.path.join(base_path, "data", "Localization", "french_(france)")
        os.makedirs(french_path, exist_ok=True)
        return french_path

    def download_file(self, url, destination):
        try:
            url_with_timestamp = f"{url}?t={int(time.time())}"
            print(f"Téléchargement depuis : {url_with_timestamp}")
            response = requests.get(url_with_timestamp, timeout=10)
            response.raise_for_status()
            with open(destination, "wb") as file:
                file.write(response.content)
            print(f"Fichier téléchargé : {destination}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau : {e}")
            messagebox.showerror("Erreur", f"Échec du téléchargement (réseau) : {e}")
        except Exception as e:
            print(f"Erreur générale : {e}")
            messagebox.showerror("Erreur", f"Échec du téléchargement : {e}")

    def calculate_file_hash(self, file_path):
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            return None

    def calculate_online_hash(self, url):

        sha256 = hashlib.sha256()
        try:
            url_with_timestamp = f"{url}?t={int(time.time())}" 
            response = requests.get(url_with_timestamp, timeout=10)
            response.raise_for_status()
            sha256.update(response.content)
            return sha256.hexdigest()
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau lors du téléchargement pour le hash : {e}")
            return None

    def check_installation_status(self):
        base_path = self.folder_path.get()
        if base_path:
            french_path = os.path.join(base_path, "data", "Localization", "french_(france)")
            global_ini_path = os.path.join(french_path, "global.ini")
            user_cfg_path = os.path.join(base_path, "user.cfg")

            if os.path.exists(global_ini_path) and os.path.exists(user_cfg_path):
                self.install_button.config(state="disabled")
                self.update_button.config(state="normal")
                self.update_prices_button.config(state="normal")
                self.delete_button.config(state="normal")
            else:
                self.install_button.config(state="normal")
                self.update_button.config(state="disabled")
                self.update_prices_button.config(state="disabled")
                self.delete_button.config(state="disabled")
        else:
            self.install_button.config(state="disabled")
            self.update_button.config(state="disabled")
            self.update_prices_button.config(state="disabled")
            self.delete_button.config(state="disabled")

    def check_version_by_hash(self):
        base_path = self.folder_path.get()
        if not base_path:
            self.version_text.set("Aucun dossier sélectionné.")
            self.update_button.config(state="disabled")
            return

        french_path = os.path.join(base_path, "data", "Localization", "french_(france)")
        global_ini_path = os.path.join(french_path, "global.ini")

        if not os.path.exists(global_ini_path):
            self.version_text.set("Installation initiale nécessaire.")
            self.update_button.config(state="disabled")
            return

        try:
            local_hash = self.calculate_file_hash(global_ini_path)
            print(f"Hash local : {local_hash}")

            online_hash = self.calculate_online_hash(self.global_ini_url)
            print(f"Hash en ligne : {online_hash}")

            if local_hash == online_hash:
                self.version_text.set("Vous êtes à jour.")
                self.version_label.config(foreground="#5db267")
                self.update_button.config(state="disabled")
            else:
                self.version_text.set("Une mise à jour est disponible.")
                self.version_label.config(foreground="#68c2c8")
                self.update_button.config(state="normal")
        except Exception as e:
            self.version_text.set("Erreur lors de la vérification.")
            print(f"Erreur générale : {e}")

    def adjust_combobox_width(self, combobox, values):
        if values:
            max_length = max(len(value) for value in values)
            combobox.configure(width=max_length + 5)

    def show_success_popup(self, message):
        top = Tk()
        top.title("Succès")

        # Obtenez les dimensions de l'écran
        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        # Définissez la taille de la fenêtre pop-up
        window_width = 450
        window_height = 150

        # Calculez la position x, y pour centrer la fenêtre pop-up
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Définissez la géométrie de la fenêtre pop-up
        top.geometry(f'{window_width}x{window_height}+{x}+{y}')
        top.configure(bg="#28a745")

        # Gestion du chemin d'accès pour PyInstaller
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(__file__)

        icon_path = os.path.join(application_path, "icon.ico")
        top.iconbitmap(icon_path)

        msg = ttk.Label(top, text=message, font=("Arial", 12), foreground="white", background="#28a745")
        msg.pack(expand=True)

        ttk.Button(top, text="OK", command=top.destroy).pack(pady=10)

    def show_error_popup(self, message):
        """Affiche une pop-up d'erreur stylisée."""
        top = Tk()
        top.title("Erreur")

        # Obtenez les dimensions de l'écran
        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        # Définissez la taille de la fenêtre pop-up
        window_width = 300
        window_height = 150

        # Calculez la position x, y pour centrer la fenêtre pop-up
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Définissez la géométrie de la fenêtre pop-up
        top.geometry(f'{window_width}x{window_height}+{x}+{y}')
        top.configure(bg="#b45959")

        # Gestion du chemin d'accès pour PyInstaller
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(__file__)

        icon_path = os.path.join(application_path, "icon.ico")
        top.iconbitmap(icon_path)

        msg = ttk.Label(top, text=message, font=("Arial", 12), foreground="white", background="#b45959", style="Delete.TButton")
        msg.pack(expand=True)

        ttk.Button(top, text="OK", command=top.destroy).pack(pady=10)


if __name__ == "__main__":
    root = Tk()
    app = TraductionApp(root)
    root.mainloop()