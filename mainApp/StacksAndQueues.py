class Stack(object):
    def __init__(self):
        self.stack = []

    def __repr__(self):
        return f'{self.stack}'

    def append(self, value):
        self.stack.append(value)

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()
    
    def len(self):
        return len(self.stack)

class Queue(object):
    def __init__(self):
        self.queue = []

    def __repr__(self):
        return f'{self.queue}'

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if len(self.queue) < 1:
            return None
        return self.queue.pop(0)
        
    def len(self):
        return len(self.queue)
    
