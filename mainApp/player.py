
class Player(object):
    def __init__(self, appWidth, appHeight): 
        self.cx = appWidth//2
        self.cy = appHeight//2
        self.width = 20
        self.movementSpeed = 10
        self.totalHealth = 12
        self.health = 12
        self.attackSpeed = 15
        self.attackDamage = 1
        self.totalMana = 16
        self.mana = 16
        self.manaTimer = 0
        self.manaRegenSpeed = 5
    
    def __repr__(self):
        return f'Player(Location:{(self.cx, self.cy)}, Health:{self.health})'

    def attackWithMouse(self, app, x, y):
        if self.mana < 2: return 
        ##########
        app.swimmer.attackingCounter = 0
        app.swimmer.attacking = True
        ##########
        radius = 8
        cx, cy = self.cx, self.cy
        deltaX = (x - cx) / self.attackSpeed
        deltaY = (y - cy) / self.attackSpeed
        app.currentRoom.playerAttacks.append({'cx': cx, 'cy': cy, 
            'radius': radius, 'deltaX': deltaX, 'deltaY':deltaY})
        if not app.debugOn: self.mana -= 2

    def attackWithKeys(self, app, key):
        if key not in ['Right', 'Left', 'Up', 'Down']: return 
        if self.mana < 2: return 
        #############
        app.swimmer.attackingCounter = 0
        app.swimmer.attacking = True
        #############
        radius = 8
        cx, cy = self.cx, self.cy
        deltaX = 0
        deltaY = 0
        if key == 'Right':
            deltaX = self.attackSpeed
        elif key == 'Left':
            deltaX = -self.attackSpeed
        elif key == 'Up':
            deltaY = -self.attackSpeed
        elif key == 'Down':
            deltaY = self.attackSpeed
        app.currentRoom.playerAttacks.append({'cx': cx, 'cy': cy, 
                        'radius': radius, 'deltaX': deltaX, 'deltaY':deltaY})
        if not app.debugOn: self.mana -= 2

    def attackInBoundsOfPlayer(self, circleX, circleY, r): 
        x1, y1 = self.cx - self.width, self.cy - self.width
        x2, y2 = self.cx + self.width, self.cy + self.width
        xn = max(x1, min(circleX, x2))
        yn = max(y1, min(circleY, y2))
        dx = xn - circleX
        dy = yn - circleY
        return (dx**2 + dy**2) <= r**2

    def physicalAttack(self, app):
        if self.mana < 6: return 
        app.swimmer.physicalAttackCounter = 0
        app.swimmer.physicalAttacking = True
        if not app.debugOn: self.mana -= 6
        radius = 8
        deltas = {'right': (self.attackSpeed, 0), 'down': (0, self.attackSpeed), 
            'left': (-self.attackSpeed, 0), 'up': (0, -self.attackSpeed),
            'down-right': (self.attackSpeed, self.attackSpeed), 
            'down-left': (-self.attackSpeed, self.attackSpeed), 
            'up-left': (-self.attackSpeed, -self.attackSpeed), 
            'up-right': (self.attackSpeed, -self.attackSpeed)}
        for key in deltas:
            deltaX, deltaY = deltas[key]
            app.currentRoom.playerAttacks.append({'cx': self.cx, 'cy': self.cy, 
                        'radius': radius, 'deltaX': deltaX, 'deltaY':deltaY})

def playerMovement(app, key):
    if key == 'w':
        app.player.cy -= app.player.movementSpeed
        if inBoundsOfRocks(app): app.player.cy += app.player.movementSpeed
        app.swimmer.isRunning = True
        app.swimmer.physicalAttacking = app.swimmer.attacking = False
    elif key == 's':
        app.player.cy += app.player.movementSpeed
        if inBoundsOfRocks(app): app.player.cy -= app.player.movementSpeed
        app.swimmer.isRunning = True
        app.swimmer.physicalAttacking = app.swimmer.attacking = False
    elif key in {'a', 'Left'}:
        if key == 'a':
            app.player.cx -= app.player.movementSpeed
            if inBoundsOfRocks(app): app.player.cx += app.player.movementSpeed
        app.swimmer.isRunning = True
        app.swimmer.physicalAttacking = app.swimmer.attacking = False
        if not app.swimmer.flipped:
            app.swimmer.flipped = True
            app.swimmer.flipSpriteSheet(app.swimmer.runningSprites)
            app.swimmer.flipSpriteSheet(app.swimmer.attackSprites)
            app.swimmer.flipSpriteSheet(app.swimmer.idleSprites)
            app.swimmer.flipSpriteSheet(app.swimmer.physicalAttackSprites)
    elif key in {'d', 'Right'}:
        if key == 'd': 
            app.player.cx += app.player.movementSpeed
            if inBoundsOfRocks(app): app.player.cx -= app.player.movementSpeed
        app.swimmer.isRunning = True
        app.swimmer.physicalAttacking = app.swimmer.attacking = False
        if app.swimmer.flipped:
            app.swimmer.flipped = False
            app.swimmer.flipSpriteSheet(app.swimmer.runningSprites)
            app.swimmer.flipSpriteSheet(app.swimmer.attackSprites)
            app.swimmer.flipSpriteSheet(app.swimmer.idleSprites)
            app.swimmer.flipSpriteSheet(app.swimmer.physicalAttackSprites)

    checkIfChangeOfRoom(app)
    inBoundsOfRoom(app)
    inBoundsOfRocks(app)
    inBoundsOfItem(app)

def movePlayerAttacks(app):
    for attack in app.currentRoom.playerAttacks: 
        attack['cx'] = attack['cx'] + attack['deltaX']
        attack['cy'] = attack['cy'] + attack['deltaY']
        if (attack['cx'] < 0 or attack['cx'] > app.width or 
            attack['cy'] < 0 or attack['cy'] > app.height): 
            app.currentRoom.playerAttacks.remove(attack)
        for monster in app.currentRoom.monsters:
            if monster.attackInBoundsOfMonster(attack['cx'], attack['cy'], attack['radius']):
                if attack in app.currentRoom.playerAttacks:
                    app.currentRoom.playerAttacks.remove(attack) 
                    if app.swimmer.physicalAttacking:
                        monster.health -= app.player.attackDamage * 2 
                    else:              
                        monster.health -= app.player.attackDamage
                if monster.health <= 0:
                    app.currentRoom.monsters.remove(monster)

def checkIfChangeOfRoom(app):
    if len(app.currentRoom.monsters) == 0 or app.debugOn:
        #left door
        if inBoundsOfDoor(app, 'left') and checkIfAdjacentRoom(app, (0,-1)):
            newRoomCell = (app.currentRoom.cell[0] + (0), app.currentRoom.cell[1] + (-1))
            changeRoom(app, newRoomCell, (0,-1))
        #right door
        elif inBoundsOfDoor(app, 'right') and checkIfAdjacentRoom(app, (0,+1)):
            newRoomCell = (app.currentRoom.cell[0] + (0), app.currentRoom.cell[1] + (+1))
            changeRoom(app, newRoomCell, (0,+1))
        #top door
        elif inBoundsOfDoor(app, 'top') and checkIfAdjacentRoom(app, (-1,0)):
            newRoomCell = (app.currentRoom.cell[0] + (-1), app.currentRoom.cell[1] + (0))
            changeRoom(app, newRoomCell, (-1,0))
        #bottom door
        elif inBoundsOfDoor(app, 'bottom') and checkIfAdjacentRoom(app, (+1,0)):
            newRoomCell = (app.currentRoom.cell[0] + (+1), app.currentRoom.cell[1] + (0))
            changeRoom(app, newRoomCell, (+1,0))


def inBoundsOfDoor(app, door):
    doorList = app.doors[door]
    x0, y0, x1, y1 = doorList[0], doorList[1], doorList[2], doorList[3] 
    return (app.player.cx - app.player.width <= x1 and 
            app.player.cx + app.player.width >= x0 and 
            app.player.cy - app.player.width <= y1 and 
            app.player.cy + app.player.width >= y0)

def inBoundsOfRoom(app):
    player = app.player
    if player.cx - player.width < 0:
        player.cx = player.width
    elif player.cx + player.width > app.width:
        player.cx = app.width - player.width
    elif player.cy - player.width < 0:
        player.cy = player.width
    elif player.cy + player.width > app.height:
        player.cy = app.height - player.width   

def inBoundsOfRocks(app):
    if app.debugOn: return False
    player = app.player
    rockWidth = app.currentRoom.rockWidth
    for rockX, rockY in app.currentRoom.rocks:
        if (player.cx - player.width < rockX + rockWidth and 
            player.cx + player.width > rockX - rockWidth and 
            player.cy - player.width < rockY + rockWidth and 
            player.cy + player.width > rockY - rockWidth):
            return True
    return False

    
def checkIfAdjacentRoom(app, adjacentCellDirection):
    drow, dcol = adjacentCellDirection
    roomRow, roomCol = app.currentRoom.cell
    newCell = (roomRow + drow, roomCol + dcol)
    for room in app.rooms:
        if room.cell == newCell:
            return True
    return False

def changeRoom(app, newRoomCell, direction):
    app.currentRoom.hasPlayer = False
    for room in app.rooms:
        if room.player != None:
            room.player = None
        if room.cell == newRoomCell:
            room.hasPlayer = True
            room.player = app.player
            app.currentRoom = room
            newPlayerPosition(app, direction)
            print(app.currentRoom)

def newPlayerPosition(app, direction):
    if direction == (0,-1):
        app.player.cx = app.width - app.doorWidth
        app.player.cy = app.height//2
    elif direction == (0,+1):
        app.player.cx = app.doorWidth
        app.player.cy = app.height//2
    elif direction == (-1,0):
        app.player.cx = app.width//2
        app.player.cy = app.height - app.doorWidth
    elif direction == (+1,0):
        app.player.cx = app.width//2
        app.player.cy = app.doorWidth

def inBoundsOfItem(app):
    player = app.player
    for dictionary in app.currentRoom.items:
        x, y = dictionary['cell']
        function = dictionary['function']
        if (player.cx - player.width < x + app.itemsWidth and 
            player.cx + player.width > x - app.itemsWidth and 
            player.cy - player.width < y + app.itemsWidth and 
            player.cy + player.width > y - app.itemsWidth):
                function(app)
                app.currentRoom.items.remove(dictionary)
                if dictionary['name'] == 'healthPack':
                    name = 'HEALTH PACK'
                if dictionary['name'] == 'speedUp':
                    name = 'SPEED UP PACK'
                if dictionary['name'] == 'damageUp':
                    name = 'DAMAGE UP PACK' 
                if dictionary['name'] == 'increaseManaRegen':
                    name = 'MANA REGEN UP PACK'
                if dictionary['name'] == 'hpUp':
                    name = 'HP UP PACK'
                app.message = f"YOU PICKED UP A {name}"
                print(app.message)
                app.displayMessage = True

#red
def healthPack(app):
    app.player.health += 5
#yellow
def speedUp(app):
    app.player.movementSpeed += 5
#green
def damageUp(app):
    app.player.attackDamage += 2
#blue
def increaseManaRegen(app):
    app.player.manaRegenSpeed -= 2
#brown
def hpUp(app):
    app.player.health += 5
    app.player.totalHealth += 5
