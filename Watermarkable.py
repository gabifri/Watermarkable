import os
import json
import threading
import ctypes
import logging
import tempfile
from tkinter import (
    Tk, Frame, Label, Button, StringVar, Entry,
    filedialog, ttk, messagebox, simpledialog,
    Canvas, BOTH, NW, DISABLED
)
from PIL import Image, ImageTk, ImageOps

# Logger setup
datefmt = '%Y-%m-%d %H:%M:%S'
LOG_FILE = os.path.expanduser('~/.wm_log.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format=f'%(asctime)s %(levelname)s: %(message)s',
    datefmt=datefmt
)

# Hide console on Windows
try:
    ctypes.windll.kernel32.FreeConsole()
except Exception:
    pass

PROFILES_FILE = os.path.expanduser('~/.wm_profiles.json')
SUPPORTED_EXT = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        root.title("Watermarkable")
        root.geometry("900x500")
        logging.info("Application started")

        self.profiles = self.load_profiles()
        self.current_profile = None
        self.preview_img = None
        self.last_output_dir = None

        # Layout
        main = Frame(root)
        main.pack(fill=BOTH, expand=True)
        ctrl = Frame(main, width=350)
        ctrl.pack(side='left', fill='y', padx=10, pady=10)
        prevf = Frame(main)
        prevf.pack(side='right', fill=BOTH, expand=True, padx=10, pady=10)

        # Profile
        Label(ctrl, text="Profil Watermark:").pack(anchor='w')
        self.profile_var = StringVar()
        self.profile_cb = ttk.Combobox(
            ctrl, textvariable=self.profile_var,
            values=list(self.profiles.keys()), state='readonly'
        )
        self.profile_cb.pack(fill='x', pady=5)
        self.profile_cb.bind('<<ComboboxSelected>>', lambda e: self.load_profile())

        btnf = Frame(ctrl)
        btnf.pack(fill='x', pady=(0,10))
        Button(btnf, text="Nouveau", command=self.new_profile).pack(side='left', expand=True)
        Button(btnf, text="Éditer", command=self.edit_profile).pack(side='left', expand=True)
        Button(btnf, text="Supprimer", command=self.delete_profile).pack(side='left', expand=True)

        # Source path
        Label(ctrl, text="Chemin dossier images:").pack(anchor='w', pady=(10,0))
        self.src_var = StringVar()
        Entry(ctrl, textvariable=self.src_var).pack(fill='x')
        Button(ctrl, text="Parcourir", command=self.select_folder).pack(fill='x', pady=5)

        # Position
        Label(ctrl, text="Position du filigrane:").pack(anchor='w', pady=(10,0))
        self.pos_var = StringVar(value='Bas Droite')
        ttk.Combobox(
            ctrl, textvariable=self.pos_var,
            values=['Bas Droite','Bas Gauche','Haut Droite','Haut Gauche','Centre'],
            state='readonly'
        ).pack(fill='x', pady=5)

        # Preview & Start
        Button(ctrl, text="Rafraîchir aperçu", command=self.update_preview).pack(fill='x', pady=5)
        Button(ctrl, text="Démarrer Traitement", command=self.start).pack(fill='x', pady=5)

        # Open output
        self.open_btn = Button(ctrl, text="Ouvrir dossier sortie", state=DISABLED, command=self.open_output)
        self.open_btn.pack(fill='x', pady=(5,20))

        # Status
        self.status_var = StringVar(value="En attente...")
        Label(ctrl, textvariable=self.status_var).pack(anchor='w')

        # Preview canvas
        self.canvas = Canvas(prevf, bg='grey')
        self.canvas.pack(fill=BOTH, expand=True)

    def load_profiles(self):
        try:
            if os.path.exists(PROFILES_FILE):
                with open(PROFILES_FILE) as f:
                    return json.load(f)
        except Exception as e:
            logging.error("load_profiles: %s", e, exc_info=True)
        return {}

    def save_profiles(self):
        try:
            with open(PROFILES_FILE, 'w') as f:
                json.dump(self.profiles, f)
        except Exception as e:
            logging.error("save_profiles: %s", e, exc_info=True)
            messagebox.showerror("Erreur","Impossible de sauvegarder les profils.")

    def new_profile(self):
        name = simpledialog.askstring("Nouveau profil","Nom du profil :")
        if not name or name in self.profiles:
            return
        p = self.ask_params()
        if p:
            self.profiles[name] = p
            self.save_profiles()
            self.profile_cb['values'] = list(self.profiles.keys())
            self.profile_var.set(name)
            self.load_profile()

    def edit_profile(self):
        name = self.profile_var.get()
        if name in self.profiles:
            p = self.ask_params(self.profiles[name])
            if p:
                self.profiles[name] = p
                self.save_profiles()
                self.load_profile()

    def delete_profile(self):
        name = self.profile_var.get()
        if name and messagebox.askyesno("Supprimer","Supprimer '%s' ?"%name):
            del self.profiles[name]
            self.save_profiles()
            self.profile_cb['values'] = list(self.profiles.keys())
            self.profile_var.set('')
            self.current_profile=None
            self.update_preview()

    def ask_params(self, prev=None):
        prev = prev or {'wm_file':'','scale':0.2,'margin':10}
        wm_file = filedialog.askopenfilename(title="Watermark PNG", filetypes=[('PNG','*.png')])
        if not wm_file:
            return None
        scale = simpledialog.askinteger("Taille (%)","Largeur watermark (%) :", initialvalue=int(prev['scale']*100), minvalue=5, maxvalue=100)
        margin = simpledialog.askinteger("Marge (px)","Marge depuis le bord (px) :", initialvalue=prev['margin'], minvalue=0, maxvalue=500)
        return {'wm_file': wm_file, 'scale': scale/100.0, 'margin': margin}

    def load_profile(self):
        name = self.profile_var.get()
        if name in self.profiles:
            self.current_profile = self.profiles[name]
            self.update_preview()

    def select_folder(self):
        d = filedialog.askdirectory(title="Dossier images")
        if d:
            self.src_var.set(d)
            self.update_preview()

    def update_preview(self):
        self.canvas.delete('all')
        self.open_btn.config(state=DISABLED)
        folder = self.src_var.get()
        cfg = self.current_profile
        if not (folder and cfg and os.path.isdir(folder)):
            return
        try:
            for fname in os.listdir(folder):
                if fname.lower().endswith(SUPPORTED_EXT):
                    src = os.path.join(folder, fname)
                    break
            else:
                return
            tmp = tempfile.NamedTemporaryFile(suffix=os.path.splitext(src)[1], delete=False)
            tmp_path = tmp.name; tmp.close()
            self._apply_single(src, tmp_path, cfg, self.pos_var.get())
            img = Image.open(tmp_path)
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            img.thumbnail((cw, ch), Image.Resampling.LANCZOS)
            self.preview_img = ImageTk.PhotoImage(img)
            self.canvas.create_image((cw-img.width)//2,(ch-img.height)//2,anchor=NW,image=self.preview_img)
            os.unlink(tmp_path)
        except Exception as e:
            logging.error("update_preview: %s", e, exc_info=True)
            messagebox.showerror("Erreur Aperçu", str(e))

    def _apply_single(self, src, dst, cfg, position):
        img = ImageOps.exif_transpose(Image.open(src).convert('RGBA'))
        wm_src = Image.open(cfg['wm_file']).convert('RGBA')
        wm_w = int(img.width * cfg['scale'])
        wm_h = int(wm_w * wm_src.height / wm_src.width)
        wm = wm_src.resize((wm_w, wm_h), Image.Resampling.LANCZOS)
        m = cfg['margin']
        pos_map = {'Bas Droite':(img.width-wm_w-m,img.height-wm_h-m),
                   'Bas Gauche':(m,img.height-wm_h-m),
                   'Haut Droite':(img.width-wm_w-m,m),
                   'Haut Gauche':(m,m),
                   'Centre':((img.width-wm_w)//2,(img.height-wm_h)//2)}
        p = pos_map.get(position)
        layer = Image.new('RGBA', img.size)
        layer.paste(wm, p, wm)
        result = Image.alpha_composite(img, layer).convert('RGB')
        result.save(dst)

    def start(self):
        folder=self.src_var.get(); cfg=self.current_profile
        if not (folder and cfg and os.path.isdir(folder)):
            messagebox.showwarning("Attention","Profil et dossier requis"); return
        files=[f for f in os.listdir(folder) if f.lower().endswith(SUPPORTED_EXT)]
        total=len(files); self.status_var.set(f"0/{total} Photos traitées")
        threading.Thread(target=self.run_apply,args=(folder,cfg,self.pos_var.get(),files),daemon=True).start()

    def run_apply(self,folder,cfg,position,files):
        out_dir=os.path.join(folder,'Avec WaterMark'); os.makedirs(out_dir,exist_ok=True)
        self.last_output_dir=out_dir; wm_src=Image.open(cfg['wm_file']).convert('RGBA')
        count=0
        for f in files:
            try:
                src=os.path.join(folder,f); img=ImageOps.exif_transpose(Image.open(src).convert('RGBA'))
                wm_w=int(img.width*cfg['scale']); wm_h=int(wm_w*wm_src.height/wm_src.width)
                wm=wm_src.resize((wm_w,wm_h),Image.Resampling.LANCZOS); m=cfg['margin']
                pos_map={'Bas Droite':(img.width-wm_w-m,img.height-wm_h-m),
                         'Bas Gauche':(m,img.height-wm_h-m),
                         'Haut Droite':(img.width-wm_w-m,m),
                         'Haut Gauche':(m,m),
                         'Centre':((img.width-wm_w)//2,(img.height-wm_h)//2)}
                p=pos_map[position]; layer=Image.new('RGBA',img.size); layer.paste(wm,p,wm)
                result=Image.alpha_composite(img,layer).convert('RGB')
                dst=os.path.join(out_dir,f"{os.path.splitext(f)[0]}_wm{os.path.splitext(f)[1]}")
                result.save(dst); count+=1; self.status_var.set(f"{count}/{len(files)} Photos traitées")
            except Exception as e:
                logging.error("run_apply %s: %s",f,e,exc_info=True)
        self.status_var.set(f"Terminé: {count}/{len(files)}"); self.open_btn.config(state=NORMAL)

    def open_output(self):
        if self.last_output_dir and os.path.isdir(self.last_output_dir):
            os.startfile(self.last_output_dir)

if __name__=='__main__':
    root=Tk(); WatermarkApp(root); root.mainloop()
