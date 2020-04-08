try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
except:
    import Tkinter as tk


class Alien(object):

    def __init__(self):
        self.id = None
        self.alive = True
        self.go_back = False

    def touched_by(self, canvas, projectile):

        proj_position = canvas.coords(projectile.id)
        alien_position = canvas.coords(self.id)

        if len(proj_position) == 2 and len(alien_position) == 2:
            proj_x, proj_y = proj_position[0], proj_position[1]
            alien_x, alien_y = alien_position[0], alien_position[1]

            self.alive = False
            print("Dead")

    def install_in(self, canvas, x, y, image, tag):
        self.id = canvas.create_image(x, y, image=image, tags=tag)

    def move_in(self, canvas, dx=10, dy=1):

        speed_y = 0

        coords = canvas.coords(self.id)

        x = coords[0]

        if 0 <= x < 800:
            if not self.go_back:
                speed_x = dx
            else:
                speed_x = -dx

        elif x < 0 or x >= 800:
            self.go_back = not self.go_back
            speed_y = dy
            if x < 0:
                speed_x = dx
            else:
                speed_x = -dx

        if self.alive:
            canvas.move(self.id, 0, 3)
        else:
            canvas.delete(self.id)


class Fleet(object):

    def __init__(self):

        self.id = None
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_inner_gap = 20
        self.alien_x_delta = 5
        self.alien_y_delta = 15

        self.pim = tk.PhotoImage(file="alien.gif")
        self.explosion = tk.PhotoImage(file="explosion.gif")

        fleet_size = self.aliens_lines * self.aliens_columns

        self.aliens_lines * self.aliens_columns
        self.aliens_fleet = [None] * fleet_size

    def install_in(self, canvas):

        # On créé une matrice d'aliens.
        x = y = 40
        i = j = index = 0

        nb_rows = self.aliens_lines
        nb_cols = self.aliens_columns

        while i < nb_rows:

            while j < nb_cols:

                alien = Alien()
                alien.install_in(canvas, x, y, image=self.pim, tag="alien")

                if index < len(self.aliens_fleet):
                    self.aliens_fleet[index] = alien

                x += self.aliens_inner_gap + 60
                j += 1
                index += 1

            y += self.aliens_inner_gap + 35
            x = 40
            i += 1
            j = 0

    def move_in(self, canvas):

        should_move = True
        width = int(canvas.cget("width"))

        # On récupère tous les éléments ayant pour tag "alien" et le defender.
        aliens = canvas.find_withtag("alien")
        _, defender_y, _, _ = canvas.bbox("defender")

        if len(self.aliens_fleet) > 0:
            x, y, end_x, end_y = canvas.bbox("alien")

            # On déplace touts les aliens.
            for al in self.aliens_fleet:
                if al is not None:
                    al.move_in(canvas, 0, 5)

            if end_y >= defender_y - 10:
                should_move = False

        if should_move is True:
            canvas.after(500, self.move_in, canvas)
        else:
            print("Vous avez perdu")

    def manage_touched_aliens_by(self, canvas, defender):

        has_won = False
        bullets = defender.fired_bullets
        aliens = self.aliens_fleet

        # On met à jour le nombre de balles.
        text = canvas.find_withtag("bullets_remaining")
        canvas.itemconfigure(text, text="Nombre de balles: %d / %d" % (
            defender.max_fired_bullets - len(defender.fired_bullets), defender.max_fired_bullets))

        if len(bullets) > 0:
            for bull in bullets:

                for al in aliens:
                    if al is not None:
                        # On recupère le rectangle contenant chaque alien.
                        bull_x, bull_y, bull_end_x, bull_end_y = canvas.bbox(al.id)
                        touches = canvas.find_overlapping(bull_x, bull_y, bull_end_x, bull_end_y)

                        # Si un élément est touché, on éfface le projectile et on créé une explosion.
                        if len(touches) > 1:
                            try:
                                defender.fired_bullets.remove(bull)
                                canvas.delete(bull.id)

                            except ValueError:
                                # Si l'élément qu'on essaie de supprimer n'existe pas, on ne fait rien :)
                                pass

                            # On créé une explosion.
                            explosion = canvas.create_image(bull_x, bull_y, image=self.explosion)
                            canvas.after(100, canvas.delete, explosion)

                            # On supprime l'alien touché.
                            self.aliens_fleet.remove(al)
                            canvas.delete(al.id)

                            if len(self.aliens_fleet) == 0:
                                has_won = True
                                print("Vous avez gagné")

        if has_won is False:
            canvas.after(100, self.manage_touched_aliens_by, canvas, defender)


class Defender(object):

    def __init__(self):

        self.width = 20
        self.height = 20
        self.move_delta = 20
        self.id = None

        self.max_fired_bullets = 8
        self.fired_bullets = []

    def install_in(self, canvas):

        lx = 400 + self.width / 2
        ly = 600 - self.height - 10
        self.id = canvas.create_rectangle(lx, ly, lx + self.width, ly + self.height, fill="white", tags="defender")

    def move_in(self, canvas, dx):

        mcoords = canvas.coords(self.id)

        if mcoords[0] < 50:
            dx = 30

        if mcoords[0] > 720:
            dx = - 30

        canvas.move(self.id, dx, 0)

    def fire(self, canvas):

        mcoords = canvas.coords(self.id)
        X = mcoords[0] + self.width / 4
        Y = mcoords[1]
        d = Bullet(self)

        self.fired_bullets.append(d)
        d.install_in(canvas, X, Y)
        d.move_in(canvas)


# les bullets ne se creent qu'en appuyant sur la touche espace
class Bullet(object):

    def __init__(self, shooter):

        self.radius = 5
        self.color = "red"
        self.speed = 8
        self.id = None
        self.shooter = shooter

    def install_in(self, canvas, x, y):

        r = self.radius
        self.id = canvas.create_oval(x, y, x + self.radius * 2, y - self.radius * 2, fill=self.color)
        return self

    def move_in(self, canvas):

        defender = self.shooter
        canvas.move(self.id, 0, -self.speed)
        canvas.after(100, self.move_in, canvas)

        for b in defender.fired_bullets:
            if canvas.coords(b.id)[1] < 0:
                defender.fired_bullets.remove(b)
                canvas.delete(b.id)

    def start(self, canvas):
        pass


class Game(object):

    def __init__(self, frame):

        width = 800
        height = 600
        self.frame = frame
        self.canvas = tk.Canvas(self.frame, width=width, height=height, bg="black")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.bullets_remaining_label = self.canvas.create_text(80, 10, text="Nombre de balles: 0", fill="white",
                                                               tag="bullets_remaining")

        self.defender = Defender()
        self.bullet = Bullet(self.defender)

        # La matrice fleet contient tous les ennemis :)
        self.fleet = Fleet()

    def start(self):

        # On ajoute les joueur et matrice sur la canvas principale.
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)
        self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        self.fleet.move_in(self.canvas)

        self.frame.winfo_toplevel().bind("<Key>", self.keypress)

    def keypress(self, event):

        x = 0
        if event.keysym == 'Left':
            x = -30
        if event.keysym == 'Right':
            x = 30
        elif event.keysym == 'space':
            # Si le nombre de balles tirées est inférieur égal à 8
            # on tire
            defender = self.defender
            if len(defender.fired_bullets) <= defender.max_fired_bullets:
                defender.fire(self.canvas)

        self.defender.move_in(self.canvas, x)

    def start_animation(self):
        self.start()


class SpaceInvaders(object):
    ''' Main Game class '''

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        width = 800
        height = 600
        self.frame = tk.Frame(self.root, width=width, height=height, bg="green")
        self.frame.pack()

        self.game = Game(self.frame)

    def play(self):
        self.game.start_animation()
        self.root.mainloop()


jeu = SpaceInvaders()
jeu.play()
