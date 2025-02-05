from PIL import Image, ImageTk, ImageDraw, ImageFont

#sprites file that contains the multiple sprites classes that use the PIL/Pillow 
#library 

class Spritesheet(object):
    def __init__(self, app, filename):
        self.filename = filename
        self.spritesheet = app.loadImage(filename)

    def flipSpriteSheet(self, spritesheet):
        for i in range(len(spritesheet)):
            spritesheet[i] = spritesheet[i].transpose(Image.FLIP_LEFT_RIGHT)
    
    def scaleImage(self, app, scale):
        self.spritesheet = app.scaleImage(self.spritesheet, scale)

    def cropImage(self, x0,y0,x1,y1):
        self.spritesheet = self.spritesheet.crop((x0,y0,x1,y1))



class PlayerSpritesheet(Spritesheet):
    def __init__(self, app, filename):
        super().__init__(app, filename)
        self.idleSprites = []
        self.runningSprites = []
        self.attackSprites = []
        self.physicalAttackSprites = []
        self.idleSpriteCounter = self.runningCounter = 0
        self.attackingCounter = self.physicalAttackCounter = 0
        self.flipped = self.isRunning = False
        self.attacking = self.physicalAttacking = False

    def initializeIdleSpriteList(self):
        margin = 48
        distBetweenSprites = 162
        spriteWidth = 104
        topY = 40
        bottomY = 100
        for i in range(6):
            sprite = self.spritesheet.crop((margin + i * distBetweenSprites, 
                        topY, spriteWidth + i * distBetweenSprites, bottomY))
            self.idleSprites.append(sprite)

    def initializeRunningSpriteList(self):
        margin = 48
        distBetweenSprites = 162
        spriteWidth = 104
        topY = 40
        bottomY = 100
        for i in range(14,22):
            sprite = self.spritesheet.crop((margin + i * distBetweenSprites, 
                        topY, spriteWidth + i * distBetweenSprites, bottomY))
            self.runningSprites.append(sprite)

    def initializeAttackSpriteList(self):
        margin = 48
        distBetweenSprites = 162
        spriteWidth = 126
        topY = 40
        bottomY = 100
        for i in range(6,11):
            sprite = self.spritesheet.crop((margin + i * distBetweenSprites, 
                        topY, spriteWidth + i * distBetweenSprites, bottomY))
            self.attackSprites.append(sprite)
    
    def initializePhysicalAttackSpriteList(self):
        margin = 48
        distBetweenSprites = 162
        spriteWidth = 135
        topY = 22
        bottomY = 100
        for i in range(22,30):
            sprite = self.spritesheet.crop((margin + i * distBetweenSprites, 
                        topY, spriteWidth + i * distBetweenSprites, bottomY))
            self.physicalAttackSprites.append(sprite)

    def incrementIdleCounter(self):
        self.idleSpriteCounter = (1 + self.idleSpriteCounter) % len(self.idleSprites)

    def incrementRunningCounter(self):
        self.runningCounter = (1 + self.runningCounter) % len(self.runningSprites)

    def incrementAttackingCounter(self):
        self.attackingCounter = (1 + self.attackingCounter) % len(self.attackSprites)
        if self.attackingCounter == len(self.attackSprites) - 1:
            self.attacking = False

    def incrementPhysicalAttackingCounter(self):
        self.physicalAttackCounter = (1 + self.physicalAttackCounter) % len(self.physicalAttackSprites)
        if self.physicalAttackCounter == len(self.physicalAttackSprites) - 1:
            self.physicalAttacking = False

class MonsterSpritesheet(Spritesheet):
    def __init__(self, app, filename):
        super().__init__(app, filename)
        self.runningSprites = []
        self.runningCounter = 0
        self.flipped = False
        self.isRunning = True
    
    def initializeRunningSpriteList(self, scale):
        distBetweenSprites = 22 * scale
        spriteWidth = 19 * scale
        topY = 0 * scale
        bottomY = 37 * scale
        for i in range(13):
            sprite = self.spritesheet.crop((i * distBetweenSprites, 
                        topY, i * distBetweenSprites + spriteWidth, bottomY))
            self.runningSprites.append(sprite)

    def incrementRunningCounter(self):
        self.runningCounter = (1 + self.runningCounter) % len(self.runningSprites)


class BossSpritesheet(Spritesheet):
    def __init__(self, app, filename):
        super().__init__(app, filename)
        self.runningSprites = []
        self.runningCounter = 0
        self.flipped = False
        self.isRunning = True

    def initializeRunningSpriteList(self, scale):
        margin = 14 * scale
        distBetweenSprites = 64 * scale
        spriteWidth = 44 * scale
        topY = 84 * scale
        bottomY = (47 + 84) * scale
        for i in range(12):
            sprite = self.spritesheet.crop((margin + i * distBetweenSprites, 
                        topY, i * distBetweenSprites + spriteWidth, bottomY))
            self.runningSprites.append(sprite)

    def incrementRunningCounter(self):
        self.runningCounter = (1 + self.runningCounter) % len(self.runningSprites)


class BatSpritesheet(Spritesheet):
    def __init__(self, app, filename):  
        super().__init__(app, filename)
        self.runningSprites = []
        self.runningCounter = 0
        self.flipped = False
        self.isRunning = True

    def initializeRunningSpriteList(self, scale):
        distBetweenSprites = 16 * scale
        spriteWidth = 15 * scale
        topY = 23 * scale
        bottomY = 41 * scale
        for i in range(5):
            sprite = self.spritesheet.crop((i * distBetweenSprites, topY, 
                                i * distBetweenSprites + spriteWidth, bottomY))
            self.runningSprites.append(sprite)

    def incrementRunningCounter(self):
        self.runningCounter = (1 + self.runningCounter) % len(self.runningSprites)
