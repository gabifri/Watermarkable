# Watermarkable
Open source watermarking tools
Réflexion durant quelques secondes


````markdown
# Watermarkable

Un petit utilitaire Python pour ajouter en masse un filigrane (watermark) sur toutes les photos d’un dossier, via un raccourci Windows.

---

## 📋 Prérequis

1. **Windows 10+**  
2. **Python 3.10+**  
   Téléchargez et installez Python depuis https://www.python.org/downloads/windows/ en cochant “Add Python to PATH”.  
3. **Module Pillow**  
   Ouvrez une invite de commandes (Win + R, tapez `cmd`), puis :
   ```bash
   pip install Pillow
````

---

## 🚀 Installation du projet

1. **Cloner le dépôt**
   Ouvrez PowerShell ou un terminal, puis :

   ```powershell
   git clone https://github.com/<votre-pseudo>/Watermarkable.git
   cd Watermarkable
   ```
2. **Vérifier que Watermarkable.py est présent**

   ```text
   Watermarkable.py
   README.md
   ```
3. **Tester manuellement**
   Dans le terminal, lancez :

   ```bash
   python Watermarkable.py
   ```

   L’interface graphique doit s’ouvrir.

---

## 🔧 Créer un raccourci Windows “double-clic”

1. **Localiser `Watermarkable.py` et votre exécutable Python**

   * Script : `C:\chemin\vers\Watermarkable\Watermarkable.py`
   * Python : par exemple `C:\Users\<VotreCompte>\AppData\Local\Programs\Python\Python310\python.exe`

2. **Créer le raccourci**

   * Cliquez droit dans le dossier (ou sur le Bureau) → **Nouveau** → **Raccourci**.
   * Dans la fenêtre « Emplacement de l’élément », saisissez :

     ```
     "C:\Users\<VotreCompte>\AppData\Local\Programs\Python\Python310\python.exe" "C:\chemin\vers\Watermarkable\Watermarkable.py"
     ```
   * Cliquez **Suivant**.

3. **Nommer le raccourci**

   * Par exemple : `Watermarkable`
   * Cliquez **Terminer**.

4. **(Optionnel) Personnaliser l’icône**

   * Clic droit sur le raccourci → **Propriétés** → onglet **Raccourci** → **Changer d’icône…**
   * Naviguez vers un fichier `.ico` de votre choix, ou sélectionnez-en un dans la liste.

5. **(Optionnel) Définir le dossier de “Démarrage dans”**

   * Dans **Propriétés** → onglet **Raccourci** → champ **Démarrer dans**

     ```
     C:\chemin\vers\Watermarkable
     ```

---

## 🎉 Utilisation

1. Double-cliquez simplement sur l’icône **Watermarkable**.
2. Dans l’interface qui s’ouvre :

   * Choisissez ou créez un profil de watermark (image PNG, échelle, marge).
   * Sélectionnez le dossier contenant vos photos.
   * Cliquez sur **Démarrer le traitement**.
3. Toutes les images avec filigrane seront générées dans un sous-dossier `Avec_Watermark`.

---

## 🛠️ Débogage & FAQ

* **Rien ne se passe au double-clic**

  * Vérifiez que le chemin de `python.exe` et de `Watermarkable.py` sont corrects (attention aux guillemets et aux espaces).
  * Ouvrez un terminal et exécutez la même ligne de commande pour voir d’éventuels messages d’erreur.

* **Module “Pillow” introuvable**

  * Relancez :

    ```bash
    pip install --upgrade Pillow
    ```

* **Changer la version de Python**

  * Si vous avez plusieurs versions, utilisez la bonne `python.exe` dans le raccourci (par ex. Python39, Python310…).

---

## 📄 Licence

Ce projet est sous licence MIT – voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

*Bon watermarking ! 🎨*

```
