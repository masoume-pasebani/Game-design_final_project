from StacksAndQueues import Queue

class Monster(object):
    def __init__(self, cx, cy):
        self.width = 20
        self.cx = cx
        self.cy = cy
        self.movementSpeed = 6
        self.attackSpeed = 6
        self.health = 6

    def __repr__(self):
        return f'Monster(Location:{(self.cx, self.cy)}, Health:{self.health})'


    @staticmethod
    def path(goalCell, cameFrom, startingCell):
        current = goalCell
        endPath = []
        while current != startingCell:
            endPath.append(current)
            current = cameFrom[current]
        endPath.reverse()
        return endPath

    def findPlayer(self, graph, player):
        def inBounds(currentNode, player):
            nodeX, nodeY = currentNode
            if (player.cx - player.width <= nodeX + player.width and 
            player.cx + player.width >= nodeX - player.width and 
            player.cy - player.width <= nodeY + player.width and 
            player.cy + player.width >= nodeY - player.width):
                return True
            return False
        startingCell = (self.cx, self.cy)
        queue = Queue()
        cameFrom = dict()
        queue.enqueue(startingCell) 
        cameFrom[startingCell] = None
        while queue.len() != 0:
            currentNode = queue.dequeue()
            if inBounds(currentNode, player): 
                return Monster.path(currentNode, cameFrom, startingCell)
            for node in graph[currentNode]:
                if node not in cameFrom:
                    cameFrom[node] = currentNode
                    queue.enqueue(node)
        return None

    def moveTowardPlayer(self, app):
        path = self.findPlayer(app.currentRoom.graph, app.player)
        if path != None and len(path) >= 1:
            self.cx = path[0][0]
            self.cy = path[0][1]
    
    def inBoundsOfPlayer(self, app):
        if (app.player.cx - app.player.width <= self.cx + self.width and 
            app.player.cx + app.player.width >= self.cx - self.width and 
            app.player.cy - app.player.width <= self.cy + self.width and 
            app.player.cy + app.player.width >= self.cy - self.width): 
                if app.debugOn: return
                app.player.health -= 1

    def attackInBoundsOfMonster(self, circleX, circleY, r): 
        x1, y1 = self.cx - self.width, self.cy - self.width
        x2, y2 = self.cx + self.width, self.cy + self.width
        xn = max(x1, min(circleX, x2))
        yn = max(y1, min(circleY, y2))
        dx = xn - circleX
        dy = yn - circleY
        return (dx**2 + dy**2) <= r**2



class fishMonster(Monster):
    def __init__(self, cx, cy):
        super().__init__(cx, cy)
        self.width = 20
        self.movementSpeed = 4
        self.attackSpeed = 12
        self.health = 2
        self.pathToPlayer = []
    
    def __repr__(self):
        return f'fishMonster(Location:{(self.cx, self.cy)}, Health:{self.health})'

    def moveTowardPlayer(self, app):
        if len(self.pathToPlayer) == 0:
            self.pathToPlayer = self.findPlayer(app.currentRoom.graph, app.player)
        if len(self.pathToPlayer) >= 1:
            self.cx = self.pathToPlayer[0][0]
            self.cy = self.pathToPlayer[0][1]
            self.pathToPlayer = self.pathToPlayer[1:]
            
