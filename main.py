import pygame as pg
import math
import tkinter as tk
from PIL import Image, ImageTk
pg.mixer.init()

scores=[]
uniZC = 0

# actual game

def menu():
    #menu
    song = pg.mixer.Sound('sounds/song.wav')
    song.play()
    root = tk.Tk()
    root.title("Welcome to THE ZOMBIE KILLER")
    root.geometry("1500x900")
    def click(root):
        song.stop()
        gameloop(root)
    def controls1():
        #controls page
        page = tk.Toplevel()
        page.geometry("1020x570")
        page.title("Controls")
        bgImage = Image.open("images/control.png")
        bgPhoto = ImageTk.PhotoImage(bgImage)
        bgLabel = tk.Label(page, image=bgPhoto)
        bgLabel.place(relwidth=1, relheight=1)
        bgLabel.image = bgPhoto
        page.mainloop()
    image = tk.PhotoImage(file="images/logo.png")
    label = tk.Label(root, image=image)
    button = tk.Button(root, text="Play Now!", command=lambda: click(root), font=("Helvetica", 24, "bold"), bg="#dadbd9", fg="darkgreen", padx=20, pady=10)
    controls = tk.Button(root, text="Controls", command=lambda: controls1   (), font=("Helvetica", 24, "bold"), bg="#dadbd9", fg="darkgreen", padx=20, pady=10)
    controls.pack()
    def position_button():
        root.update_idletasks()
        button_width = controls.winfo_width()
        x = 1500 - button_width -20
        y = 20
        controls.place(x=x, y=y)
    root.after(100, position_button)
    button.place(relx=0.5, y=700, anchor="center")
    label.pack(pady=0)
    root.mainloop()

def gameloop(root):
    root.destroy()

    #constants + media
    jump = pg.mixer.Sound('sounds/jump.wav')
    coin= pg.mixer.Sound('sounds/coin.wav')
    gunshot = pg.mixer.Sound('sounds/gun.wav')
    bite = pg.mixer.Sound('sounds/zombie.wav')
    empty = pg.mixer.Sound('sounds/empty.wav')
    knife = pg.mixer.Sound('sounds/knife.wav')
    zomb = pg.image.load('images/zombie.png')
    zomb = pg.transform.scale(zomb, (100,100))
    vigil = pg.image.load('images/vigil.png')
    vigil = pg.transform.scale(vigil, (100,100))
    vigil = pg.transform.flip(vigil, True, False)
    knif = pg.image.load('images/knife.png')
    knif = pg.transform.scale(knif, (knif.get_width()/10,knif.get_height()/10))
    knif = pg.transform.flip(knif, True, False)
    rKnif = pg.image.load('images/rKnife.png')
    rKnif = pg.transform.scale(rKnif, (rKnif.get_width()/10, rKnif.get_height()/10))
    WIDTH = 1500
    HEIGHT  = 900
    FLOOR = 700 # y = 700 techinically
    mColor =(99, 108, 122)
    clock = pg.time.Clock()

    #funcs n classes
    
    def road(surface):
        pg.draw.rect(surface, (0,0,0), (0,700,1500,200))
        x = 50
        for _ in range(5):
            pg.draw.rect(surface, (250, 228, 27), (x,785, 100,30))
            x+=300

    class Knife(pg.sprite.Sprite):
        def __init__(self, coord, image, rImage):
            super().__init__()
            self.image = image
            self.rImage = rImage
            self.x, self.y = coord
            self.uRect = pg.Rect((self.x, self.y, self.image.get_width(), self.image.get_height()))
            self.rect = pg.Rect((self.x, self.y, self.rImage.get_width(), self.rImage.get_height()))
            self.hist = [False, False]
            self.zc = 0
        def update(self, obj):
            self.rect.x = obj.rect.x-self.rect.width
            self.rect.y = obj.rect.y
            self.upRect = pg.Rect((obj.rect.x+10, obj.rect.y-self.rect.width + 65, self.rect.height, self.rect.width))
            surface.blit(self.image, self.upRect.topleft)
            click = pg.mouse.get_pressed()[0]
            if click:
                if not self.hist[-1]:
                    knife.play()
                pg.draw.rect(surface, (mColor), self.upRect)
                self.rect.x += 30
                self.rect.y += 45
                surface.blit(self.rImage, self.rect.topleft)
                for zombie in zombies:
                    if zombie.rect.colliderect(self.rect):
                        zombie.count +=1
                    if zombie.count >=40:
                        zombies.remove(zombie)
                        coin.play()
                        self.zc+=1
                    zombie.health = 1- zombie.count/40
            self.hist.append(click)

    class Bullet(pg.sprite.Sprite):
        def __init__(self, x, y, upper, line):
            super().__init__()
            self.x = x
            self.line = line
            self.check = True
            self.y = y
            self.upper = upper
            self.rect = pg.Rect((self.x, self.y, 10, 10))
        def update(self):
            rate = 5
            if self.line[0] == None:
                if self.y <= HEIGHT:
                    self.y-=rate
                    self.coord = (self.x, self.y)
                    pg.draw.circle(surface, (0,0,0), self.coord, 5,5)
            else:   
                if pg.mouse.get_pos()[0] <= p1.gun.leftMid[0]:
                    if self.x >= self.upper:
                        self.y = self.line[0]*self.x + self.line[1]
                        self.coord = (self.x,self.y)
                        pg.draw.circle(surface, (0,0,0), self.coord, 5,5)
                        self.x-=rate
                    else:
                        self.check = False
                else:
                    if self.x <= self.upper:
                        self.y = self.line[0]*self.x + self.line[1]
                        self.coord = (self.x,self.y)
                        pg.draw.circle(surface, (0,0,0), self.coord, 5,5)
                        self.x+=rate
                    else:
                        self.check = False
            self.rect.topleft = (self.x, self.y)

    class Zombie(pg.sprite.Sprite):
        def __init__(self, surface, color, x,image):
            super().__init__()
            #attributes
            self.forward = True
            self.color = color
            self.surface = surface
            self.x = x
            self.image = image
            self.count = 0
            self.height = image.get_height()
            self.y = FLOOR-self.height
            self.width = image.get_width()
            self.font = pg.font.Font(None, 36)
            self.health = 1.0
            self.rect = pg.Rect((self.x, self.y, self.width, self.height))
        def update(self):
            #moving logic --> zombies go forward until they hit a wall, and then go in the other direction
            r = 5*3
            if self.forward:
                if self.x <= WIDTH-self.width-r:
                    self.x+=r
                else:
                    self.image = pg.transform.flip(self.image, True, False)
                    self.forward = False
            if not self.forward:
                if self.x >= r:
                    self.x-=r
                else:
                    self.image = pg.transform.flip(self.image, True, False)
                    self.forward = True
            self.rect.topleft = (self.x, self.y)
            text = self.font.render(f"{round(self.health,1) * 100}%", True, (48, 209, 48))
            surface.blit(text, (self.x + (self.width-text.get_width())/2, self.y-25))
            surface.blit(self.image, (self.x, self.y))

    class Gun():
        def __init__(self, surface, color, x,y, width, height):
            self.surface = surface
            self.color = color
            self.width = width
            self.height = height
            self.x = x-width
            self.y = y
            self.relPts = [(width-20,0), (2*width-20, 0), (width*2-20, height), (width-20,height)]
            self.points = []
        def shift(self, center):
            cx,cy = center
            pts = []
            for pt in self.relPts:
                x = pt[0] + cx
                y = pt[1] + cy
                pts.append((x,y))
            self.points = pts
        def rotate(self, cursor_pos):
            '''
            FUTURE: lots of cool trig/math/physics logic in this
            '''
            # the midpoint of the short left side
            left_midpoint = (
            self.points[0][0],  # x-coordinate of the left edge (same for top-left and bottom-left)
            (self.points[0][1] + self.points[3][1]) / 2  # Midpoint y-coordinate of the left edge
            )
            self.leftMid = left_midpoint
            # Calculate the angle to point towards the cursor
            mx, my = cursor_pos
            dx, dy = mx - left_midpoint[0], my - left_midpoint[1]
            self.angle = math.degrees(math.atan2(dy, dx))  # Calculate the angle in degrees

            # Rotate each point around the new pivot (left midpoint)
            rotated_pts = []
            for x, y in self.points:
                # Translate to origin (relative to pivot)
                temp_x = x - left_midpoint[0]
                temp_y = y - left_midpoint[1]

                # Apply rotation
                rotated_x = temp_x * math.cos(math.radians(self.angle)) - temp_y * math.sin(math.radians(self.angle))
                rotated_y = temp_x * math.sin(math.radians(self.angle)) + temp_y * math.cos(math.radians(self.angle))

                # Translate back to original position
                final_x = rotated_x + left_midpoint[0]
                final_y = rotated_y + left_midpoint[1]
                rotated_pts.append((final_x, final_y))
            self.points = rotated_pts
            if dx != 0:
                slope = dy / dx  # Calculate slope
                intercept = self.leftMid[1] - slope * self.leftMid[0]  # Calculate y-intercept (b)
                a = slope**2 + 1
                b_quad = -2 * self.leftMid[0] + 2 * slope * intercept - 2 * slope * self.leftMid[1]
                c = self.leftMid[0]**2 + (self.leftMid[1] - intercept)**2 - 200**2  # 50^2 = 2500

                # Discriminant
                disc = b_quad**2 - 4 * a * c
                if disc >= 0:
                    # Select root based on cursor position
                    if cursor_pos[0] > self.leftMid[0]:
                        x = (-b_quad + math.sqrt(disc)) / (2 * a)
                    else:
                        x = (-b_quad - math.sqrt(disc)) / (2 * a)
                    y = slope * x + intercept
                    #pg.draw.line(surface, (0, 255, 0), self.leftMid, (x, y), 5)
                    self.line = [slope, intercept]
            
            else:
                # Handle vertical line case (dx == 0)
                x = self.leftMid[0]
                y_offset = 50 if dy > 0 else -50
                y = self.leftMid[1] + y_offset
                self.line = [None,None]
            self.upper = x
        def update(self, center, cursor_pos):
            self.shift(center) #units are RELATIVELY shifted to the p1 toplefts
            self.rotate(cursor_pos)
            pg.draw.polygon(self.surface, self.color, self.points) 

    class Viglilante(pg.sprite.Sprite):
        def __init__(self, surface, color, x, image):
            super().__init__()
            self.hist = ['A']
            self.surface = surface
            self.color = color
            self.image = image
            self.width = image.get_width()
            self.height = image.get_height()
            self.x= x
            self.y = FLOOR-self.height
            self.rect = pg.Rect((self.x, self.y, self.width, self.height))
            #a knife
            self.knife = Knife((self.x, self.y), knif, rKnif)
            #a gun
            self.gun = Gun(surface, (0,0,0), x, self.y, 50, 15)
            #physics 
            self.Y_GRAVITY = 1.25 # gravity force
            self.JUMP_HEIGHT = 25 # jump power
            self.Y_VELOCITY = 0 # vigilante not moving at first
            self.jumping = False # we aint jumping at first
        def update(self):
            keys = pg.key.get_pressed()
            if (keys[pg.K_w] or keys[pg.K_SPACE]) and not self.jumping: # if space pressed and it not a double jump
                self.Y_VELOCITY = -self.JUMP_HEIGHT  # velocity goes up (direction) by jump height magnitude
                jump.play()
                self.jumping = True

            self.Y_VELOCITY += self.Y_GRAVITY # each frame the direction slows down by gravity force
            self.y += self.Y_VELOCITY # each frame the y level of the pos is gonna change in the direction of the velocity'

            if self.y >= FLOOR - self.height: #if self.y hits the floor or falls through, we're back to not moving state
                self.y = FLOOR - self.height  
                self.Y_VELOCITY = 0  
                self.jumping = False 
            if keys[pg.K_a]:
                if self.hist[-1]!= 'A':
                    self.image = pg.transform.flip(self.image, True, False)
                if self.x - 0 >= 15: 
                    self.x-=15
                else:
                    self.x = 0
                self.hist.append('A')
            if keys[pg.K_d]:
                if self.hist[-1]!= 'D':
                    self.image = pg.transform.flip(self.image, True, False)
                if WIDTH-self.x >= self.width+15:
                    self.x+=15
                else:
                    self.x = WIDTH-self.width
                self.hist.append('D')
            self.rect.topleft = (self.x, self.y)
            surface.blit(self.image, self.rect.topleft)
            keys = pg.key.get_pressed()
            if not keys[pg.K_LSHIFT]:
                self.gun.update(self.rect.topleft, pg.mouse.get_pos())
            else:
                self.knife.update(self)

    # main loop

    # vars for main loop
    running = True
    pg.font.init()
    font = pg.font.Font(None, 56)
    surface = pg.display.set_mode((WIDTH,HEIGHT))
    pg.display.set_caption("The Zombie Killer")
    surface.fill(mColor)
    bCount = 0
    zc = 0
    his = []

    # group zombie sprites, all sprites, and the plater
    zombies = pg.sprite.Group()
    p1 = Viglilante(surface, (255,0,0), 750,vigil) #p1Y = FLOOR - p1HEIGHT
    bullets = pg.sprite.Group()

    #future spawn rate for zombies and health
    spawn = 0
    health = 10000

    while running:
        #start frame by reset + draw roads + bullet, health, zombie counts
        surface.fill(mColor)
        collisions = []
        road(surface)
        text = font.render(f"Health: {health}", True, (10,255,0))
        surface.blit(text, (0,0,text.get_width(), text.get_height()))
        Text = font.render(f"Bullets: {bCount}", True, (0,0,0))
        surface.blit(Text, (WIDTH-Text.get_width(), 0, Text.get_width()-20, Text.get_height()))
        zD = font.render(f"Zombie Count: {zc}", True, (255,10,0))
        val = (WIDTH-zD.get_width())/2
        surface.blit(zD, (int(val),0))

        # this just updates the player + gun according to key strokes
        p1.update()

        #zombie logic

        # every ith frame spawn another zombie or bullet
        if (spawn % 50*2== 0):
            zombies.add(Zombie(surface, (0,0,255), 0, zomb))
        if (spawn % 50*2.25 == 0) and bCount <= len(zombies)-1 and len(zombies)>=2:
            bCount += 1
        for zombie in zombies:
            zombie.update()
        #zombie contact --> -10 health
        if pg.sprite.spritecollide(p1, zombies, False):
            his.append(1)
            health-= 10
        else:
            his.append(0)
        if his[-1] == 1 and his[-2] == 0:
            bite.play()
        spawn+=1
        
        #self explanatory
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and not keys[pg.K_LSHIFT]:
                if bCount > 0:
                    gunshot.play()
                    bound = p1.gun.upper
                    bullet = Bullet(p1.x,p1.y,bound, p1.gun.line)
                    bullets.add(bullet)
                    bCount-=1
                else:
                    empty.play()
            elif event.type == pg.MOUSEBUTTONDOWN and keys[pg.K_LSHIFT]:
                pass

        if health == 0:
            gameOver(zc)
            running = False

        #see if bullet hit zombie
        collisions =  pg.sprite.groupcollide(bullets, zombies, True, True)
        for _ in range(len(collisions)):
            coin.play()
        zc += len(collisions)
        zc+=p1.knife.zc
        p1.knife.zc = 0
        for bullet in bullets:
            if bullet.check:
                bullet.update()
            else:
                bullets.remove(bullet)
        clock.tick(45)
        pg.display.flip()

def gameOver(zc):
    over = tk.Tk()
    over.title("GAME OVER")
    over.geometry("500x300")
    scores.append(zc)
    label = tk.Label(over, text=f"Max Score: {max(scores)}", font=("Helvetica", 36, "bold"))
    label.pack(pady=50)
    button = tk.Button(over, text="Play Again!", command=lambda: gameloop(over), font=("Helvetica", 24, "bold"), bg="#dadbd9", fg="red", padx=20, pady=10)
    button.place(relx=0.5, y=200, anchor="center")
    over.mainloop()

def main():
    menu()
if __name__ == "__main__":
    main()