
from cmu_112_graphics import *
from enemies import *
from player import * 
from rooms import *
from sprites import *
import random, time


def appStarted(app):
    app.startScreen = True
    app.infoScreen = False
    app.startScreenX = random.randint(-100,-80)
    app.startScreenY = random.randint(-100,-80)
    app.startCircleDeltaX = 20
    app.startCircleDeltaY = 20
    app.startScreenR = 80
    app.doorWidth = 40
    app.nextDoorWidth = 20
    app.itemsWidth = 10
    app.mapMargin = 140
    app.itemFunctions = {'healthPack': healthPack, 'speedUp': speedUp, 
                'damageUp': damageUp, 'increaseManaRegen': increaseManaRegen, 
                'hpUp':hpUp}
    app.doors = {
        'top':[app.width//2 - app.doorWidth, 0, 
               app.width//2 + app.doorWidth, app.doorWidth//3], 
        'bottom':[app.width//2 - app.doorWidth, app.height - app.doorWidth//3, 
                  app.width//2 + app.doorWidth, app.height],
        'left':[0, app.height//2 - app.doorWidth, 
                app.doorWidth//3, app.height//2 + app.doorWidth],
        'right':[app.width - app.doorWidth//3, app.height//2 - app.doorWidth, 
                 app.width, app.height//2 + app.doorWidth]
    }
    initializeWorld(app)
    initializePlayerAndMonsters(app)
    initializeSprites(app)
    app.displayingMap = False
    app.displayMessage = False
    app.messageSize = 30
    app.gameOver = False
    app.debugOn = False
    app.playerWonTheGame = False

    app.keyPressedTimer = None
    app.totalKeyPressedTimer = None
    app.lastKeyPressed = None

    app.monsterMovementTimer = 0
    app.monsterAttackTimer = 0
    app.bossAttackTimer = 0

    print(app.currentRoom)

def initializeWorld(app):
    app.rooms = Room.generateRooms(Room)
    for room in app.rooms:

        if room.cell != (0,0):
            roomPixelList = Room.createRoomPixelList(app.width, app.height) 

            for i in range(random.randint(8,15)):
                randomCell = findRockRandomCell(app, roomPixelList)

                room.rocks.append(randomCell)
                roomPixelList.remove(randomCell)
            chance = random.randrange(1,10)


            if chance in {1,2}:
                randomItem = random.choice(list(app.itemFunctions.keys()))
                itemData = {'cell': random.choice(roomPixelList), 
                            'function':app.itemFunctions[randomItem], 
                            'name': randomItem}
                room.items.append(itemData)


            room.graph = Room.createAdjacencyList(roomPixelList, 40)

    for i in range(2):
        randomRoom = random.choice(app.rooms)
        while randomRoom.cell == (0,0):
            randomRoom = random.choice(app.rooms)
        itemData = {'cell': random.choice(roomPixelList), 
                    'function':app.itemFunctions['healthPack'], 
                    'name': 'healthPack'}
        randomRoom.items.append(itemData)


    app.roomGraph = Room.createAdjacencyList(Room.createRoomList(), 1)

def initializePlayerAndMonsters(app):

    for room in app.rooms:
        if room.hasPlayer:
            app.player = room.player = Player(app.width, app.height)
            app.currentRoom = room
    farthestRoomCell = Room.findFarthestRoom(app.roomGraph, app.currentRoom.cell)

    for room in app.rooms:
        if room.cell == farthestRoomCell:
            app.bossRoom = room
            room.isBossRoom = True
            room.generateBoss(room.graph, app.width, app.height)
        if room.cell != (0,0) and room.cell != farthestRoomCell:
            for i in range(random.randint(2,5)):
                room.generateEnemi(room.graph, app.width, app.height)

def initializeSprites(app):
    #Sprites:
    app.character = PlayerSpritesheet(app, 'images/player.png')
    app.character.scaleImage(app, .7)
    app.character.initializeIdleSpriteList()
    app.character.initializeRunningSpriteList()
    app.character.initializeAttackSpriteList()
    app.character.initializePhysicalAttackSpriteList()
    app.skeleton = MonsterSpritesheet(app, 'images/enemi1.png')
    app.skeleton.scaleImage(app, 1.7)
    app.skeleton.initializeRunningSpriteList(1.7)
    app.bat = BatSpritesheet(app, 'images/enemi2.png')
    app.bat.scaleImage(app, 3)
    app.bat.initializeRunningSpriteList(3)
    app.boss = BossSpritesheet(app, 'images/boss.png')
    app.boss.scaleImage(app, 3)
    app.boss.initializeRunningSpriteList(3)
    app.rocksImage = Spritesheet(app, 'images/stones.png')
    app.rocksImage.cropImage(6,539,112,630)
    app.rocksImage.scaleImage(app, .5)

def findRockRandomCell(app, roomList):
    middleX = app.width//2
    middleY = app.height//2
    dWidth = app.doorWidth

    topDoorSet = {(middleX,0),(middleX,dWidth),(middleX,dWidth*2),(middleX - dWidth,0),
                  (middleX-dWidth,dWidth),(middleX+dWidth,0),(middleX+dWidth,dWidth)}
    bottomDoorSet = {(middleX,app.height-dWidth),(middleX,app.height-(dWidth*2)),
                     (middleX-dWidth,app.height-dWidth),(middleX-dWidth,app.height-(dWidth*2)),
                     (middleX+dWidth,app.height-dWidth),(middleX+dWidth,app.height-(dWidth*2))}
    leftDoorSet = {(0,middleY),(dWidth,middleY),(0,middleY-dWidth),(dWidth,middleY-dWidth),
                   (0,middleY+dWidth),(dWidth,middleY+dWidth)}
    rightDoorSet = {(app.width-dWidth,middleY),(app.width-(dWidth*2),middleY),
                    (app.width-dWidth,middleY-dWidth),(app.width-(dWidth*2),middleY-dWidth),
                    (app.width-dWidth,middleY+dWidth),(app.width-(dWidth*2),middleY+dWidth)}
    randomCell = random.choice(roomList)
    while (randomCell in topDoorSet or randomCell in bottomDoorSet or 
           randomCell in leftDoorSet or randomCell in rightDoorSet):
        randomCell = random.choice(roomList)
    return randomCell

def mousePressed(app, event):
    if not app.startScreen and not app.infoScreen:
        app.player.attackWithMouse(app, event.x, event.y)
    elif app.startScreen and clickInBoundsOfStart(app, event.x, event.y):
        app.startScreen = False
        app.infoScreen = False 
    elif app.startScreen and clickInBoundsOfInfo(app, event.x, event.y):
        app.startScreen = False
        app.infoScreen = True
    elif app.infoScreen:
        app.startScreen = True
        app.infoScreen = False

def clickInBoundsOfStart(app, x, y):
    buttonX0 = app.width//2 - 60
    buttonY0 = app.height//2 - 30
    buttonX1 = app.width//2 + 60
    buttonY1 = app.height//2 + 30
    return (x >= buttonX0 - 80 and x <= buttonX1 - 80 and 
        y >= buttonY0 + 40 and y <= buttonY1 + 40)

def clickInBoundsOfInfo(app, x, y):
    buttonX0 = app.width//2 - 60
    buttonY0 = app.height//2 - 30
    buttonX1 = app.width//2 + 60
    buttonY1 = app.height//2 + 30
    return (x >= buttonX0 + 80 and x <= buttonX1 + 80 and 
        y >= buttonY0 + 40 and y <= buttonY1 + 40)

def keyPressed(app, event):
    if app.startScreen: return 
    elif app.infoScreen: return

    app.keyPressedTimer = time.time()
    app.totalKeyPressedTimer = time.time()
    app.lastKeyPressed = event.key

    if event.key == 'r':
        restartApp(app)
    playerMovement(app, event.key)
    app.player.attackWithKeys(app, event.key)
    if event.key == 'b':
        app.currentRoom.hasPlayer = False
        app.currentRoom.player = None
        app.currentRoom = app.bossRoom 
        app.currentRoom.hasPlayer = True
        app.currentRoom.player = app.player
    elif event.key == 'Space':
        app.player.physicalAttack(app)
    elif event.key == 'm':
        displayMap(app)
    elif event.key == 'c':
        app.debugOn = not app.debugOn
        if app.debugOn: 
            app.message = 'Debug mode is now on'
            app.displayMessage = True
        else: 
            app.message = 'Debug mode is now off'
            app.displayMessage = True

def displayMap(app):
    app.displayingMap = not app.displayingMap

def restartApp(app):
    Room.rooms = []
    Room.selectionRooms = []
    appStarted(app)
    Room.floorNumber = 0


def advanceToNextFloor(app):
    currentFloorNumber = Room.floorNumber
    Room.rooms = []
    Room.selectionRooms = []
    #Old Player Stats:
    playersCurrentHealth = app.player.health
    movementSpeed = app.player.movementSpeed
    totalHealth = app.player.totalHealth
    attackDamage = app.player.attackDamage
    totalMana = app.player.totalMana
    manaRegenSpeed = app.player.manaRegenSpeed
    #Reset:
    appStarted(app)
    app.startScreen = False
    #Previous Player Stats:
    Room.floorNumber = currentFloorNumber + 1
    app.player.health = playersCurrentHealth
    app.player.movementSpeed = movementSpeed
    app.player.totalHealth = totalHealth
    app.player.attackDamage = attackDamage 
    app.player.totalMana = totalMana
    app.player.manaRegenSpeed = manaRegenSpeed

def keyReleased(app, event):
    app.keyPressedTimer = None
    app.totalKeyPressedTimer = None
    app.lastKeyPressed = None
    app.character.isRunning = False

def timerFired(app):
    if app.startScreen:
        movesStartScreenCircle(app)
 
    if (app.keyPressedTimer != None and 
        time.time() - app.keyPressedTimer >= 0.02):
        playerMovement(app, app.lastKeyPressed) 
        app.keyPressedTimer = time.time() 

    if (app.totalKeyPressedTimer != None and 
        time.time() - app.totalKeyPressedTimer >= 0.5): 
        app.keyPressedTimer = None
        app.totalKeyPressedTimer = None


    if len(app.currentRoom.playerAttacks) > 0:
        movePlayerAttacks(app)
    if len(app.currentRoom.bossAttacks) > 0:
        BossEnemi.moveBossAttacks(app)


    if app.player.mana < app.player.totalMana:
        app.player.manaTimer += 1
        if app.player.manaTimer % app.player.manaRegenSpeed == 0: 
            app.player.mana += 1

    if app.player.health <= 0:
        app.gameOver = True



    app.monsterMovementTimer += 1
    app.monsterAttackTimer += 1
    app.bossAttackTimer += 1
    for monster in app.currentRoom.enemies:
        if len(app.currentRoom.enemies) == 0: return 
        if app.monsterMovementTimer % (monster.movementSpeed - Room.floorNumber) == 0:
            monster.moveTowardPlayer(app)

        if app.monsterMovementTimer % (monster.attackSpeed - Room.floorNumber) == 0:
            monster.inBoundsOfPlayer(app)
        if app.currentRoom == app.bossRoom:
            if app.bossAttackTimer % monster.shootingSpeed == 0:
                monster.attackPlayer(app)

    if (len(app.bossRoom.enemies) == 0 and app.bossRoom.hasPlayer and 
           (app.player.cx - app.player.width <= app.width//2 + app.nextDoorWidth and 
            app.player.cx + app.player.width >= app.width//2 - app.nextDoorWidth and 
            app.player.cy - app.player.width <= app.height//2 + app.nextDoorWidth and 
            app.player.cy + app.player.width >= app.height//2 - app.nextDoorWidth)):
        if Room.floorNumber == 4:
            app.playerWonTheGame = True
            app.gameOver = True
            return 
        advanceToNextFloor(app)


    if app.character.attacking:
        app.character.incrementAttackingCounter()
    elif app.character.isRunning:
        app.character.incrementRunningCounter()
    elif app.character.physicalAttacking:
        app.character.incrementPhysicalAttackingCounter()
    else:
        app.character.incrementIdleCounter()
    app.skeleton.incrementRunningCounter()
    app.boss.incrementRunningCounter()
    app.bat.incrementRunningCounter()

    if app.player.cx < app.width//2 and not app.skeleton.flipped: 
        app.skeleton.flipSpriteSheet(app.skeleton.runningSprites)
        app.skeleton.flipped = True
        app.boss.flipSpriteSheet(app.boss.runningSprites)
        app.boss.flipped = True
        app.bat.flipSpriteSheet(app.bat.runningSprites)
        app.bat.flipped = True
    elif app.player.cx >= app.width//2 and app.skeleton.flipped:
        app.skeleton.flipSpriteSheet(app.skeleton.runningSprites)
        app.skeleton.flipped = False
        app.boss.flipSpriteSheet(app.boss.runningSprites)
        app.boss.flipped = False
        app.bat.flipSpriteSheet(app.bat.runningSprites)
        app.bat.flipped = False

    ###################
    if app.displayMessage:
        app.messageSize -= 1
        if app.messageSize <= 15:
            app.displayMessage = False
            app.messageSize = 30
    ###################

def movesStartScreenCircle(app):
    if app.startScreenX >= app.width + 200:
        app.startCircleDeltaX *= -1
    if app.startScreenX <= -200:
        app.startCircleDeltaX *= -1
    if app.startScreenY <= -200:
        app.startCircleDeltaY *= -1
    if app.startScreenY >= app.height + 200:
        app.startCircleDeltaY *= -1
    app.startScreenX += app.startCircleDeltaX
    app.startScreenY += app.startCircleDeltaY

def redrawAll(app, canvas):
    if app.gameOver and not app.playerWonTheGame:
        drawGameOver(app, canvas)
    elif app.startScreen:
        drawStartScreen(app, canvas)

    elif app.gameOver and app.playerWonTheGame:
        drawWinningScreen(app, canvas)
    else:
        drawRoom(app, canvas)
        drawRocks(app, canvas)
        drawDoorToNextFloor(app, canvas)
        drawDoors(app, canvas)
        drawPlayer(app, canvas)
        drawPlayerAttacks(app, canvas)
        drawMonsters(app, canvas)
        drawBossAttacks(app, canvas)
        drawPlayerHealthAndMana(app, canvas)
        drawMonstersHealth(app, canvas)
        drawItems(app, canvas)
        drawMessage(app, canvas)
        drawMap(app, canvas)

def drawBackground(app, canvas):
    canvas.create_image(app.width//2, app.height//2, 
        image=ImageTk.PhotoImage(app.backgroundImage.spritesheet))

def drawPlayer(app, canvas):
    if app.character.attacking:
        sprite = app.character.attackSprites[app.character.attackingCounter]
    elif app.character.isRunning:
        sprite = app.character.runningSprites[app.character.runningCounter]
    elif app.character.physicalAttacking:
        sprite = app.character.physicalAttackSprites[app.character.physicalAttackCounter]
    else:
        sprite = app.character.idleSprites[app.character.idleSpriteCounter]
    canvas.create_image(app.player.cx, app.player.cy, image=ImageTk.PhotoImage(sprite))

def drawPlayerAttacks(app, canvas):
    for attack in app.currentRoom.playerAttacks:
        cx = attack['cx']
        cy = attack['cy']
        r = attack['radius']
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill='black')

def drawBossAttacks(app, canvas):
    color = 'firebrick2'
    for attack in app.currentRoom.bossAttacks:
        cx = attack['cx']
        cy = attack['cy']
        r = attack['radius']
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color)

def drawRoom(app, canvas):
    if app.currentRoom == app.bossRoom and app.currentRoom.hasPlayer:
        color = 'dark slate gray'
    else:
        color = 'lightblue4'
    canvas.create_rectangle(0, 0, app.width, app.height, fill=color)
    #Floor number
    if app.currentRoom.cell == (0,0):
        canvas.create_text(app.width//2, app.height//2, 
            text=f'{Room.floorNumber + 1}', font='Arial 80 bold', fill='white')
    #left wall
    canvas.create_rectangle(0,0, app.doorWidth//3, app.height, 
            fill='skyblue', width=0)
    #bottom wall
    canvas.create_rectangle(0,app.height - app.doorWidth//3, 
            app.width, app.height, fill='skyblue', width=0)
    #right wall 
    canvas.create_rectangle(app.width - app.doorWidth//3, 0, 
            app.width, app.height, fill='skyblue', width=0)
    #top wall 
    canvas.create_rectangle(0, 0, app.width, app.doorWidth//3, 
            fill='skyblue', width=0)

def drawDoors(app, canvas):
    dirs = [(0,-1),(0,+1),(-1,0),(+1,0)]
    if len(app.currentRoom.enemies) != 0: color = 'skyblue'
    elif app.bossRoom.hasPlayer: color = 'dark slate gray'
    else: color = 'lightblue4'
    for drow, dcol in dirs:
        if checkIfAdjacentRoom(app, (drow,dcol)):
            if drow == -1: #top door
                canvas.create_rectangle(app.doors['top'][0], 
                        app.doors['top'][1], app.doors['top'][2], 
                        app.doors['top'][3], fill=color, width=0)
            elif drow == +1: #bottom door
                canvas.create_rectangle(app.doors['bottom'][0], 
                        app.doors['bottom'][1], app.doors['bottom'][2], 
                        app.doors['bottom'][3], fill=color, width=0)
            elif dcol == -1: #left door
                canvas.create_rectangle(app.doors['left'][0], 
                        app.doors['left'][1], app.doors['left'][2], 
                        app.doors['left'][3], fill=color, width=0)
            elif dcol == +1: #right door
                canvas.create_rectangle(app.doors['right'][0], 
                        app.doors['right'][1], app.doors['right'][2], 
                        app.doors['right'][3], fill=color, width=0)

def drawMonsters(app, canvas):
    for monster in app.currentRoom.enemies:
        if app.currentRoom.isBossRoom:

            sprite = app.boss.runningSprites[app.boss.runningCounter]
            canvas.create_image(monster.cx, monster.cy, 
                                image=ImageTk.PhotoImage(sprite))
        elif isinstance(monster, BatEnemi):

            sprite = app.bat.runningSprites[app.bat.runningCounter]
            canvas.create_image(monster.cx, monster.cy, 
                                image=ImageTk.PhotoImage(sprite))
        else:

            sprite = app.skeleton.runningSprites[app.skeleton.runningCounter]
            canvas.create_image(monster.cx, monster.cy, 
                                image=ImageTk.PhotoImage(sprite))
    
def drawPlayerHealthAndMana(app, canvas):
    x0,y0,x1,y1 = 40,20,202,40
    canvas.create_rectangle(x0,y0,x1,y1, fill='white', width=2)
    healthBarWidth = 160
    cellWidth = healthBarWidth / (app.player.totalHealth)
    for i in range(app.player.health):
        canvas.create_rectangle(i * cellWidth + 41, 21, 
                (i * cellWidth + 41) + cellWidth, 39, fill='red', width=0)

    x0,y0,x1,y1 = 40,50,161,65
    canvas.create_rectangle(x0,y0,x1,y1, fill='white', width=2)
    manaBarWidth = 120
    cellWidth = manaBarWidth / (app.player.totalMana) 
    for i in range(app.player.mana):
        canvas.create_rectangle(i * cellWidth + x0, y0 + 1, 
                (i * cellWidth + x0) + cellWidth, y1 - 1, fill='blue', width=0)

def drawMonstersHealth(app, canvas):
    for monster in app.currentRoom.enemies:
        if isinstance(monster, BossEnemi):
            monsterHealth = 25
        elif isinstance(monster, BatEnemi):
            monsterHealth = 2
        else:
            monsterHealth = 6
        x0 = monster.cx - monster.width - 3
        y0 = monster.cy - monster.width - 18
        x1 = monster.cx + monster.width + 3
        y1 = monster.cy - monster.width - 15
        canvas.create_rectangle(x0, y0, x1, y1, fill='white')
        healthBarWidth = (monster.cx + monster.width + 3) - (monster.cx - monster.width - 3)
        cellWidth = healthBarWidth / monsterHealth
        for i in range(monster.health):
            canvas.create_rectangle(i * cellWidth + x0, y0, 
                    (i * cellWidth + x0) + cellWidth, y1, fill='red', width=0)

def drawDoorToNextFloor(app, canvas):
    if len(app.bossRoom.enemies) == 0 and app.currentRoom == app.bossRoom:
        if Room.floorNumber == 4:
            color = 'gold2'
        else:
            color = 'black'
        canvas.create_rectangle(app.width//2 - app.nextDoorWidth, 
            app.height//2 - app.nextDoorWidth, app.width//2 + app.nextDoorWidth, 
            app.height//2 + app.nextDoorWidth, fill=color)

def drawRocks(app, canvas):
    for x,y in app.currentRoom.rocks:
        width = app.currentRoom.rockWidth
        canvas.create_image(x,y, 
                    image=ImageTk.PhotoImage(app.rocksImage.spritesheet))

def drawItems(app, canvas):
    for dictionary in app.currentRoom.items:
        x,y = dictionary['cell']
        name = dictionary['name']
        if name == 'healthPack':
            color = 'red'
        if name == 'speedUp':
            color = 'yellow'
        if name == 'damageUp':
            color = 'purple' 
        if name == 'increaseManaRegen':
            color = 'blue'
        if name == 'hpUp':
            color = 'brown'
        canvas.create_rectangle(x - app.itemsWidth, y - app.itemsWidth, 
                            x + app.itemsWidth, y + app.itemsWidth, fill=color)

def drawGameOver(app, canvas):
    canvas.create_rectangle(0,0,app.width, app.height, fill='black')
    canvas.create_text(app.width//2, app.height//2, 
        text='GAMEOVER!\nYOU DIED!\nPress r to restart', 
        fill='yellow', font='Arial 24 bold')


def drawMap(app, canvas):
    if app.displayingMap == False: return 
    for room in app.rooms:
        row, col = room.cell
        if room.cell == (0,0):
            color = 'white'
        elif len(room.enemies) >= 1:
            color = 'skyblue'
        if (room == app.bossRoom and 
           (room == app.currentRoom or len(room.enemies) <= 0)):
            color = 'red'
        elif len(room.enemies) == 0:
            color = 'mint cream'
        centerRow = row + 5 - app.currentRoom.cell[0]
        centerCol = col + 5 - app.currentRoom.cell[1]
        x0, y0, x1, y1 = getCellBounds(app, centerRow, centerCol)
        canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        if room == app.currentRoom:
            canvas.create_oval(x0,y0,x1,y1, fill='purple')  

def getCellBounds(app, row, col):
    gridWidth = app.width - app.mapMargin * 2
    gridHeight = app.height - app.mapMargin * 2
    cellWidth = gridWidth / Room.cols
    cellHeight = gridHeight / Room.rows
    x0 = app.mapMargin + col * cellWidth 
    y0 = app.mapMargin + row * cellHeight 
    x1 = x0 + cellWidth
    y1 = y0 + cellHeight
    return (x0, y0, x1, y1)

def drawMessage(app, canvas):
    if app.displayMessage:
        canvas.create_text(app.width//2, app.height//2, text=f'{app.message}', 
            font=f'Arial {app.messageSize} bold', fill='white')

def drawStartScreen(app, canvas):
    canvas.create_rectangle(0,0,app.width, app.height, fill='cornflowerblue')
    canvas.create_rectangle(15,15, app.width - 15, app.height - 15, width=4)

    canvas.create_text(app.width//2, app.height//4, 
            text=' Razhaye Shenavar', font='Arial 36 bold', fill='black')
    buttonX0 = app.width//2 - 60
    buttonY0 = app.height//2 - 30
    buttonX1 = app.width//2 + 60
    buttonY1 = app.height//2 + 30
    canvas.create_rectangle(buttonX0 - 80, buttonY0 + 40, 
            buttonX1 - 80, buttonY1 + 40, width=4)
    canvas.create_rectangle(buttonX0 + 80, buttonY0 + 40, 
            buttonX1 + 80, buttonY1 + 40, width=4)
    canvas.create_text(app.width//2 - 80, app.height//2 + 40, 
            text='Start', fill='blue', font='Arial 28 bold')
    canvas.create_text(app.width//2 + 80, app.height//2 + 40, 
            text='Setting', fill='blue', font='Arial 24 bold')
    canvas.create_text(app.width//2, app.height//2.8, 
            text='Created by Masoume & Mahdie', font='Arial 12 bold', fill='black')


def drawWinningScreen(app, canvas):
    canvas.create_rectangle(0,0, app.width, app.height, fill='gold2')
    canvas.create_text(app.width//2, app.height//2, 
            text='CONGRATULATIONS\nYOU BEAT THE GAME!', 
            font='Arial 32 bold', fill='white')


runApp(width=800, height=640)
