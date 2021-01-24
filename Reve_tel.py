from random import randint
import time
from math import sqrt
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle
from kivy.core.text import Label as CoreLabel

__author__ = "reza0310"

# Designate Our .kv design file
Builder.load_file('odaame.kv')

layout = []


class HUD:

    def __init__(self):
        self.longueur, self.largeur = Window.size
        self.boutons = []

    def bind(self, emplacement, taille, action, type="Bouton"):
        print("Binding",action,'sur x variant de',(emplacement[0]-(taille[0]//2), emplacement[0]+(taille[0]//2)),'et y',(emplacement[1]-(taille[1]//2), emplacement[1]+(taille[1]//2)))
        self.boutons.append({"type": type, "x": (emplacement[0]-(taille[0]//2), emplacement[0]+(taille[0]//2)), "y": (emplacement[1]-(taille[1]//2), emplacement[1]+(taille[1]//2)), "action": action})

    def unbind(self, unbin="all"):
        if unbin == 'all':
            self.boutons = []
        else:
            for bouton in self.boutons:
                if bouton["action"] == unbin:
                    self.boutons.remove(bouton)

    def press(self, touch):
        for bouton in self.boutons:
            if bouton["x"][0] < touch.spos[0]*1000 < bouton["x"][1] and bouton["y"][0] < touch.spos[1]*1000 < bouton["y"][1]:
                print(bouton["action"])
                eval(bouton["action"])  # Handle joysticks

    def recoordonner(self, tupl):
        return int((tupl[0] / 1000) * self.longueur), int((tupl[1] / 1000) * self.largeur)

    def recoordonner_double(self, tupl):
        return int((tupl[0] / 1000) * self.longueur), int((tupl[1] / 1000) * self.largeur), int((tupl[2] / 1000) * self.longueur), int((tupl[3] / 1000) * self.largeur)

    def texte(self, x, y, texte, remove = True):
        label = CoreLabel(text=str(texte), font_size=20)
        label.refresh()
        text = label.texture
        rec = Rectangle(size=text.size, pos=self.recoordonner((x, y)), texture=text)
        layout.canvas.add(rec)
        if remove:
            def rmv(dt):
                layout.canvas.remove(rec)
            Clock.schedule_once(rmv, 1/30)

    def actualiser(self, dt):
        self.longueur, self.largeur = Window.size


class JEU:

    def initialiser(self):
        global debut, pause, vitesse, mechants, murs, fin, perso, game_over, en_jeu, coffres, armes, bonus, balles, score, drones, defilement, bosss, cooldown_murs
        armes = [{"nom": "Doigt", "munitions": 0}, {"nom": "Drone", "munitions": 0},
                 {"nom": "Akalalalalala", "munitions": 0}, {"nom": "Charge", "munitions": 0}]
        bonus = [{"nom": "Flash", "munitions": 0}, {"nom": "Mégasaut", "munitions": 0},
                 {"nom": "Multisauts", "munitions": 0}, {"nom": "RandomTP", "munitions": 0}]
        bosss = [{"boss": Dronus(), "event": "pc", "combat": "pc"}]
        layout.entities = set()
        for bos in bosss:
            layout.add_entity(bos["boss"])
        hud.unbind("all")
        game_over = False
        score = 0
        defilement = 0
        perso = char("perso.png")
        murs = []
        mechants = []
        coffres = []
        balles = []
        drones = []
        pause = 0
        debut = cooldown_murs = time.time()
        layout.img_fond = Image(source="fond.png")
        (img_x, img_y) = layout.img_fond.texture.size
        (img_x_new, img_y_new) = (9000-defilement, img_y)
        crop_pos_x = (img_x - img_x_new) / 2
        crop_pos_y = (img_y - img_y_new) / 2
        subtexture = layout.img_fond.texture.get_region(crop_pos_x, crop_pos_y, img_x_new, img_y_new)
        layout.fond = Rectangle(pos=(0, 0), size=(1000, 1000), texture=subtexture)
        layout.canvas.add(layout.fond)
        layout.add_entity(perso)
        self.event1 = Clock.schedule_interval(layout.refresh, 1/60)  # 60 fps
        self.event2 = Clock.schedule_interval(self.actualiser, 1/60)  # 60 fps
        self.event3 = Clock.schedule_interval(hud.actualiser, 1/20)  # 20 fps
        hud.bind((500, 500), (600, 1000), "perso.sauter()")
        hud.bind((950, 750), (200, 500), "perso.utiliser('bonus')")
        hud.bind((950, 250), (200, 500), "perso.utiliser('arme')")
        hud.bind((50, 750), (200, 500), "perso.ajouter('bonus')")
        hud.bind((50, 250), (200, 500), "perso.ajouter('arme')")

    def actualiser(self, dt):
        global debut, pause, vitesse, mechants, murs, fin, perso, game_over, en_jeu, coffres, armes, bonus, balles, score, drones, defilement, bosss, cooldown_murs

        if not game_over:
            pts = int(time.time() - debut - pause) + score
            level = 1
            besoin = (level ** 1.5) * 4
            while besoin < pts:
                pts -= besoin
                level += 1
                besoin = (level ** 1.5) * 4
            reste = int((pts / besoin) * 100)
            vitesse = level + 4
            cd = (vitesse / (vitesse * 4)) / (vitesse / 10)

            if level == 5 and bosss[0]["event"] == "pc":
                print("event boss 1")
                bosss[0]["event"] = "ec"
            elif level == 10 and bosss[0]["combat"] == "pc":
                print("fight boss 1")
                bosss[0]["combat"] = "ec"
                mechants.append(bosss[0]["boss"])
                bosss[0]["boss"].mortel = True
            defilement += vitesse
            if defilement >= 10000:
                print("pouitch")
                defilement -= (10000-hud.longueur)
            chances = randint(1, int(1000 / level))
            if chances == 1:
                mechants.append(mechant("ennemi.png", -100))
                layout.add_entity(mechants[-1])
            chances = randint(1, 175)
            if chances == 1:
                coffres.append(coffre())
                layout.add_entity(coffres[-1])

            if time.time() - cooldown_murs >= cd:
                cooldown_murs = time.time()
                murs.append(mur())
                layout.add_entity(murs[-1])
            i = 0
            while i < len(murs):
                murs[i].actualiser()
                if murs[i].x >= 1000:
                    layout.remove_entity(murs[i])
                    murs.pop(i)
                    i -= 1
                i += 1
            perso.actualiser()
            for mecha in mechants:
                mecha.actualiser()
                if mecha.x > 1000:
                    layout.remove_entity(mecha)
                    mechants.remove(mecha)

            for coffrer in coffres:
                coffrer.actualiser()
                if coffrer.x > 1500:
                    layout.remove_entity(coffrer)
                    coffres.remove(coffrer)

            for balle in balles:
                balle.actualiser()
            for dro in drones:
                dro.actualiser()
            for bosses in bosss:
                bosses["boss"].actualiser()

            hud.texte(920, 920, perso.money)
            hud.texte(900, 40, "Score: " + str(int(time.time() - debut - pause) + score))
            hud.texte(890, 70, f"Level: {str(level)} ({str(reste)}%)")
            hud.texte(10, 70, "Bonus:")
            hud.texte(10, 40, bonus[perso.bonus]["nom"] + " " + str(bonus[perso.bonus]["munitions"]))
            hud.texte(150, 70, "Arme:")
            hud.texte(150, 40, armes[perso.arme]["nom"] + " " + str(armes[perso.arme]["munitions"]))
            return 0
        else:
            hud.unbind()
            hud.bind((500, 500), (1000, 1000), "jeu.initialiser()")
            hud.texte(500, 500, "GAME OVER", False)
            hud.texte(470, 480, "Appuyez pour recommencer", False)
            self.event1.cancel()
            self.event2.cancel()
            self.event3.cancel()


hud = HUD()
jeu = JEU()


class char:

    def __init__(self, image):
        self.gravite = 50
        self.x = 475
        self.y = 475
        self.sauts = 0
        self.image = Rectangle(pos=(self.x, self.y), size=(50, 50), source=image)
        self.money = 100000
        self.arme = 0
        self.bonus = 0
        self.en_charge = False
        self.cooldown_charge = 0

    def sauter(self):
        if self.sauts >= 1:
            self.gravite = 10
            self.sauts -= 1

    def actualiser(self):
        global game_over, fin, score
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((50, 50))
        self.y += self.gravite
        if self.gravite > -9:
            self.gravite -= 1
        if self.x > 475 or self.en_charge:
            self.x -= 1
        elif self.x < 475 and not self.en_charge:
            self.x += 1
        for mur in murs:
            if mur.x-50 < self.x < mur.x + mur.longueur and mur.y <= self.y <= mur.y + 10:
                self.sauts = 5
                self.gravite = 0
            elif mur.x-50 < self.x < mur.x + mur.longueur and mur.y <= self.y+50 <= mur.y + 10:
                self.gravite = -1
            if mur.x + mur.longueur < self.x < mur.x + mur.longueur + 5 and mur.y - 49 <= self.y <= mur.y + 10:
                self.x += vitesse + 1
        self.angles = [{"x": self.x, "y": self.y}, {"x": self.x + 50, "y": self.y}, {"x": self.x, "y": self.y + 50},
                       {"x": self.x + 50, "y": self.y + 50}]
        for mechan in mechants:
            for angle in self.angles:
                if mechan.x <= angle["x"] <= mechan.x + 50 and mechan.y <= angle["y"] <= mechan.y + 50:
                    if self.en_charge:
                        try:
                            mechants.remove(mechan)
                            score += 10
                        except:
                            print("Méchante erreur")
                    else:
                        game_over = True
        if self.en_charge and time.time() - self.cooldown_charge >= 5:
            self.en_charge = False
            self.cooldown_charge = 0
        if self.x > 1000 or self.y < 0:
            game_over = True

    def utiliser(self, chose):
        if chose == "arme":
            if armes[self.arme]["nom"] == "Doigt" and armes[self.arme]["munitions"] > 0:
                balles.append(balle("balle jaune", 1, 150, 100))
                armes[self.arme]["munitions"] -= 1

            elif armes[self.arme]["nom"] == "Charge" and armes[self.arme]["munitions"] > 0:
                self.en_charge = True
                self.cooldown_charge = time.time()
                armes[self.arme]["munitions"] -= 1

            elif armes[self.arme]["nom"] == "Akalalalalala" and armes[self.arme]["munitions"] > 0:
                balles.append(balle("balle grise", 100, 200, 50))
                armes[self.arme]["munitions"] -= 1

            elif armes[self.arme]["nom"] == "Drone" and armes[self.arme]["munitions"] > 0:
                drones.append(drone())
                armes[self.arme]["munitions"] -= 1

        else:
            if bonus[self.bonus]["nom"] == "Flash" and bonus[self.bonus]["munitions"] > 0:
                bonus[self.bonus]["munitions"] -= 1
                hud.fill(couleurs["jaune"])
                self.x -= 200

            elif bonus[self.bonus]["nom"] == "Mégasaut" and bonus[self.bonus]["munitions"] > 0 and self.sauts >= 2:
                bonus[self.bonus]["munitions"] -= 1
                self.gravite = 50
                self.sauts -= 2

            elif bonus[self.bonus]["nom"] == "Multisauts" and bonus[self.bonus]["munitions"] > 0:
                bonus[self.bonus]["munitions"] -= 1
                self.sauts += 5

            elif bonus[self.bonus]["nom"] == "RandomTP" and bonus[self.bonus]["munitions"] > 0:
                bonus[self.bonus]["munitions"] -= 1
                self.x = randint(0, 1000)
                self.y = randint(0, 1000)

    def ajouter(self, truc):
        if truc == 'arme':
            self.arme += 1
            if self.arme >= len(armes):
                self.arme = 0
        else:
            self.bonus += 1
            if self.bonus >= len(bonus):
                self.bonus = 0


class mechant(char):

    def __init__(self, couleur, x):
        super().__init__(couleur)
        self.x = x
        self.y = randint(0, 500)
        self.sauts = 10000
        self.gravite = 0
        self.pvs = self.pvs_max = 1

    def actualiser(self):
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((50, 50))
        self.y += self.gravite
        if self.gravite >= -9:
            self.gravite -= 1
        self.x += vitesse
        for mur in murs:
            if mur.x-50 < self.x < mur.x + mur.longueur and mur.y <= self.y <= mur.y + 10:
                self.sauts = 5
                self.gravite = 0
            elif mur.x-50 < self.x < mur.x + mur.longueur and mur.y <= self.y+50 <= mur.y + 10:
                self.gravite = -1
        for mecha in [i for i in mechants if i != self]:
            if mecha.x - 50 < self.x < mecha.x + 50 and mecha.y <= self.y <= mecha.y + 50:
                self.gravite = 20


class mur:

    def __init__(self):
        good = False
        while not good:
            self.y = randint(50, 990)
            good = True
            for rum in murs:
                if rum.y - 25 < self.y < rum.y + 35:
                    good = False
        self.longueur = randint(100, 1000)
        self.x = -self.longueur
        self.image = Rectangle(pos=(self.x, self.y), size=(self.longueur, 10), source="plateforme.png")

    def actualiser(self):
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((self.longueur, 10))
        self.x += vitesse


class coffre:

    def __init__(self):
        self.type = randint(0, 2)
        if self.type == 2:
            self.type = 1
        self.x = -200
        self.y = randint(500 * self.type, 500 * self.type + 500)
        self.image = Rectangle(pos=(self.x, self.y), size=(100, 100), source=images["c2" if self.type == 1 else "c1"])

    def actualiser(self):
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((100, 100))
        self.x += vitesse
        dists = []
        for angle in perso.angles:
            dists.append(int(sqrt(((self.x) - angle["x"]) ** 2 + ((self.y) - angle["y"]) ** 2)))
        if sorted(dists)[0] < 100 and (self.type == 1 or (self.type == 0 and perso.money >= 10000)):
            coffres.remove(self)
            layout.remove_entity(self)
            if self.type == 0:
                perso.money -= 10000
            prix = {0: [] + bonus + armes, 1: [100, 100, 100, 100, 100, 1000, 1000, 1000, 1000, 10000] + bonus}
            gain = prix[self.type][randint(0, len(prix[self.type]) - 1)]
            if type(gain) == int:
                perso.money += gain
            elif type(gain) == dict and self.type == 0:
                gain["munitions"] += 10
            elif type(gain) == dict:
                gain["munitions"] += 3
            else:
                print(gain)


class balle:

    def __init__(self, couleur, vitesse, dim_x, dim_y, *args):
        if len(args) == 0:
            self.x = perso.x + 1
            self.y = perso.y
        else:
            self.x = args[0][0]
            self.y = args[0][1]
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.image = Rectangle(pos=(self.x, self.y), size=(self.dim_x, self.dim_y), source=images[couleur])
        self.vitesse = vitesse

    def actualiser(self):
        global score
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((self.dim_x, self.dim_y))
        self.x -= self.vitesse
        for mechan in mechants:
            angles = [{"x": mechan.x, "y": mechan.y}, {"x": mechan.x + 50, "y": mechan.y},
                      {"x": mechan.x, "y": mechan.y + 50}, {"x": mechan.x + 50, "y": mechan.y + 50}]
            for angle in angles:
                if self.x <= angle["x"] <= self.x + self.dim_x and self.y <= angle["y"] <= self.y + self.dim_y:
                    try:
                        mechan.pvs -= 1
                        if mechan.pvs <= 0:
                            score += 10 * mechan.pvs_max
                            mechants.remove(mechan)
                    except:
                        print("Méchante erreur")
        if self.x < -self.dim_x:
            balles.remove(self)
        layout.canvas.add(self.image)
        def rmv(dt):
            layout.canvas.remove(self.image)
        Clock.schedule_once(rmv, 1/30)


class bad_balle(balle):

    def __init__(self, couleur, vitesse, dim_x, dim_y, *args):
        super().__init__(couleur, vitesse, dim_x, dim_y, *args)

    def actualiser(self):
        global game_over
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((self.dim_x, self.dim_y))
        self.x += self.vitesse
        angles = [{"x": perso.x, "y": perso.y}, {"x": perso.x + 50, "y": perso.y},
                  {"x": perso.x, "y": perso.y + 50}, {"x": perso.x + 50, "y": perso.y + 50}]
        for angle in angles:
            if self.x <= angle["x"] <= self.x + self.dim_x and self.y <= angle["y"] <= self.y + self.dim_y:
                try:
                    game_over = True
                except:
                    print("Méchante erreur")
        if self.x > 1000:
            balles.remove(self)
        layout.canvas.add(self.image)
        def rmv(dt):
            layout.canvas.remove(self.image)
        Clock.schedule_once(rmv, 1/30)


class drone:

    def __init__(self):
        self.cooldown = time.time()
        self.x = 900
        self.y = 50
        self.direction = "bas"
        self.image = Rectangle(pos=(self.x, self.y), size=(100, 100), source=images["drone"])

    def actualiser(self):
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((100, 100))
        if time.time() - self.cooldown >= 10:
            drones.remove(self)
        if self.direction == "bas":
            self.y += 10
            if self.y >= 850:
                self.direction = "haut"
        else:
            self.y -= 10
            if self.y <= 50:
                self.direction = "bas"
        chances = randint(1, 40)
        if chances == 1:
            balles.append(balle("balle grise", 100, 200, 50, (self.x, self.y)))
        layout.canvas.add(self.image)
        def rmv(dt):
            layout.canvas.remove(self.image)
        Clock.schedule_once(rmv, 1/30)


class boss:

    def __init__(self):
        self.pvs = self.pvs_max = 10
        self.mortel = False

    '''def afficher(self):
        if self.mortel:
            hud.draw_rect(couleurs["rose"], hud.recoordonner_double((50, 100, 70, 800)))
            hud.draw_rect(couleurs["rose"], hud.recoordonner_double((50, 100, 70, self.pvs * 80)), True)'''


class Dronus(boss, drone):

    def __init__(self):
        boss.__init__(self)
        drone.__init__(self)
        self.x = 100

    '''def afficher(self):
        if bosss[0]["combat"] == "ec":
            boss.afficher(self)
        if bosss[0]["combat"] == "ec" or bosss[0]["event"] == "ec":
            self.image.pos = hud.recoordonner((self.x, self.y))'''

    def actualiser(self):
        self.image.pos = hud.recoordonner((self.x, self.y))
        self.image.size = hud.recoordonner((100, 100))
        if bosss[0]["event"] == "ec":
            self.y += 10
            if self.y >= 850:
                bosss[0]["event"] = "t"
                self.y = 50
                layout.canvas.remove(self.image)
                return 0
            chances = randint(1, 40)
            if chances == 1:
                balles.append(bad_balle("balle grise", 10, 200, 50, (self.x, self.y)))
            layout.canvas.add(self.image)
            def rmv(dt):
                layout.canvas.remove(self.image)
            Clock.schedule_once(rmv, 1/30)

        elif bosss[0]["combat"] == "ec":
            if self.direction == "bas":
                self.y += 10
                if self.y >= 850:
                    self.direction = "haut"
            else:
                self.y -= 10
                if self.y <= 50:
                    self.direction = "bas"
            chances = randint(1, 40)
            if chances == 1:
                balles.append(bad_balle("balle grise", 10, 200, 50, (self.x, self.y)))
            if self.pvs <= 0:
                bosss[0]["combat"] = "t"
            layout.canvas.add(self.image)
            def rmv(dt):
                layout.canvas.remove(self.image)
            Clock.schedule_once(rmv, 1/30)


def pauser():
    while True:
        hud.texte("PAUSE", hud.recoordonner((450, 490)))
        hud.refresh()
        # Handle


images = {"fond": "fond.png", "c1": "coffre noir.png", "c2": "coffre marron.png", "balle jaune": "balle jaune.png",
          "balle grise": "balle parfaite.png", "drone": "drone.png"}

couleurs = {"noir": (0, 0, 0),
            "blanc": (255, 255, 255),
            "bleu": (0, 0, 255),
            "rouge": (255, 0, 0),
            "vert": (0, 255, 0),
            "marron": (153, 0, 0),
            "violet": (190, 0, 255),
            "jaune": (255, 255, 0),
            "rose": (200, 0, 200)}

en_jeu = True
FPS = 60
level = 1
reste = 1


class Layout(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_entity(self, entity):
        self.entities.add(entity)
        self.canvas.add(entity.image)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            self.canvas.remove(entity.image)

    def refresh(self, dt):
        global defilement
        with self.canvas:
            subtexture = self.img_fond.texture.get_region(9000-defilement, 0, 1000, 1000)
            self.fond.texture = subtexture
            self.fond.size = (hud.longueur, hud.largeur)

    def on_touch_down(self, touch):
        hud.press(touch)


class ODAAMEApp(App):
    def build(self):
        global layout
        Window.clearcolor = (1, 1, 1, 1)
        self.title = 'O.D.A.A.M.E.'
        layout = Layout()
        jeu.initialiser()
        return layout


ODAAMEApp().run()