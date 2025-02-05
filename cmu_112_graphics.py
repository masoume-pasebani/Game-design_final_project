
import sys
if ((sys.version_info[0] != 3) or (sys.version_info[1] < 6)):
    raise Exception('cmu_112_graphics.py requires Python version 3.6 or later.')

import datetime
MAJOR_VERSION = 0
MINOR_VERSION = 9.0 

from tkinter import *
from tkinter import messagebox, simpledialog, filedialog
import inspect, copy, traceback
import sys, os
from io import BytesIO

def failedImport(importName, installName=None):
    installName = installName or importName
    print('**********************************************************')
    print(f'** Cannot import {importName} -- it seems you need to install {installName}')
    print(f'** This may result in limited functionality or even a runtime error.')
    print('**********************************************************')
    print()

try: from PIL import Image, ImageTk, ImageDraw, ImageFont
except ModuleNotFoundError: failedImport('PIL', 'pillow')

if sys.platform.startswith('linux'):
    try: import pyscreenshot as ImageGrabber
    except ModuleNotFoundError: failedImport('pyscreenshot')
else:
    try: from PIL import ImageGrab as ImageGrabber
    except ModuleNotFoundError: pass # Our PIL warning is already printed above

try: import requests
except ModuleNotFoundError: failedImport('requests')

def getHash(obj):
    # This is used to detect MVC violations in redrawAll
    # @TODO: Make this more robust and efficient
    try:
        return getHash(obj.__dict__)
    except:
        if (isinstance(obj, list)): return getHash(tuple([getHash(v) for v in obj]))
        elif (isinstance(obj, set)): return getHash(sorted(obj))
        elif (isinstance(obj, dict)): return getHash(tuple([obj[key] for key in sorted(obj)]))
        else:
            try: return hash(obj)
            except: return getHash(repr(obj))

class WrappedCanvas(Canvas):
    # Enforces MVC: no drawing outside calls to redrawAll
    # Logs draw calls (for autograder) in canvas.loggedDrawingCalls
    def __init__(wrappedCanvas, app):
        wrappedCanvas.loggedDrawingCalls = [ ]
        wrappedCanvas.logDrawingCalls = True
        wrappedCanvas.inRedrawAll = False
        wrappedCanvas.app = app
        super().__init__(app._root, width=app.width, height=app.height)

    def log(self, methodName, args, kwargs):
        if (not self.inRedrawAll):
            self.app._mvcViolation('you may not use the canvas (the view) outside of redrawAll')
        if (self.logDrawingCalls):
            self.loggedDrawingCalls.append((methodName, args, kwargs))

    def create_arc(self, *args, **kwargs): self.log('create_arc', args, kwargs); return super().create_arc(*args, **kwargs)
    def create_bitmap(self, *args, **kwargs): self.log('create_bitmap', args, kwargs); return super().create_bitmap(*args, **kwargs)
    def create_line(self, *args, **kwargs): self.log('create_line', args, kwargs); return super().create_line(*args, **kwargs)
    def create_oval(self, *args, **kwargs): self.log('create_oval', args, kwargs); return super().create_oval(*args, **kwargs)
    def create_polygon(self, *args, **kwargs): self.log('create_polygon', args, kwargs); return super().create_polygon(*args, **kwargs)
    def create_rectangle(self, *args, **kwargs): self.log('create_rectangle', args, kwargs); return super().create_rectangle(*args, **kwargs)
    def create_text(self, *args, **kwargs): self.log('create_text', args, kwargs); return super().create_text(*args, **kwargs)
    def create_window(self, *args, **kwargs): self.log('create_window', args, kwargs); return super().create_window(*args, **kwargs)

    def create_image(self, *args, **kwargs):
        self.log('create_image', args, kwargs);
        usesImage = 'image' in kwargs
        usesPilImage = 'pilImage' in kwargs
        if ((not usesImage) and (not usesPilImage)):
            raise Exception('create_image requires an image to draw')
        elif (usesImage and usesPilImage):
            raise Exception('create_image cannot use both an image and a pilImage')
        elif (usesPilImage):
            pilImage = kwargs['pilImage']
            del kwargs['pilImage']
            if (not isinstance(pilImage, Image.Image)):
                raise Exception('create_image: pilImage value is not an instance of a PIL/Pillow image')
            image = ImageTk.PhotoImage(pilImage)
        else:
            image = kwargs['image']
            if (isinstance(image, Image.Image)):
                raise Exception('create_image: image must not be an instance of a PIL/Pillow image\n' +
                    'You perhaps meant to convert from PIL to Tkinter, like so:\n' +
                    '     canvas.create_image(x, y, image=ImageTk.PhotoImage(image))')
        kwargs['image'] = image
        return super().create_image(*args, **kwargs)

class App(object):
    majorVersion = MAJOR_VERSION
    minorVersion = MINOR_VERSION
    version = f'{majorVersion}.{minorVersion}'
    _theRoot = None # singleton Tkinter root object



    def redrawAll(app, canvas): pass      
    def appStarted(app): pass          
    def appStopped(app): pass           
    def keyPressed(app, event): pass    
    def keyReleased(app, event): pass   
    def mousePressed(app, event): pass  
    def mouseReleased(app, event): pass 
    def mouseMoved(app, event): pass    
    def mouseDragged(app, event): pass  
    def timerFired(app): pass           
    def sizeChanged(app): pass       




    def __init__(app, width=300, height=300, x=0, y=0, title=None, autorun=True, mvcCheck=True, logDrawingCalls=True):
        app.winx, app.winy, app.width, app.height = x, y, width, height
        app.timerDelay = 100     # milliseconds
        app.mouseMovedDelay = 50 # ditto
        app._title = title
        app._mvcCheck = mvcCheck
        app._logDrawingCalls = logDrawingCalls
        app._running = app._paused = False
        app._mousePressedOutsideWindow = False
        if autorun: app.run()

    def __repr__(app):
        keys = set(app.__dict__.keys())
        keyValues = [ ]
        for key in sorted(keys - app._ignoredFields):
            keyValues.append(f'{key}={app.__dict__[key]}')
        return f'App({", ".join(keyValues)})'

    def setSize(app, width, height):
        app._root.geometry(f'{width}x{height}')

    def setPosition(app, x, y):
        app._root.geometry(f'+{x}+{y}')

    def showMessage(app, message):
        messagebox.showinfo('showMessage', message, parent=app._root)

    def getUserInput(app, prompt):
        return simpledialog.askstring('getUserInput', prompt)

    def loadImage(app, path=None):
        if (app._canvas.inRedrawAll):
            raise Exception('Cannot call loadImage in redrawAll')
        if (path is None):
            path = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select file: ',filetypes = (('Image files','*.png *.gif *.jpg'),('all files','*.*')))
            if (not path): return None
        if (path.startswith('http')):
            response = requests.request('GET', path) # path is a URL!
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(path)
        return image

    def scaleImage(app, image, scale, antialias=False):
        # antialiasing is higher-quality but slower
        resample = Image.ANTIALIAS if antialias else Image.NEAREST
        return image.resize((round(image.width*scale), round(image.height*scale)), resample=resample)

    def getSnapshot(app):
        app._showRootWindow()
        x0 = app._root.winfo_rootx() + app._canvas.winfo_x()
        y0 = app._root.winfo_rooty() + app._canvas.winfo_y()
        result = ImageGrabber.grab((x0,y0,x0+app.width,y0+app.height))
        return result

    def saveSnapshot(app):
        path = filedialog.asksaveasfilename(initialdir=os.getcwd(), title='Select file: ',filetypes = (('png files','*.png'),('all files','*.*')))
        if (path):
            # defer call to let filedialog close (and not grab those pixels)
            if (not path.endswith('.png')): path += '.png'
            app._deferredMethodCall(afterId='saveSnapshot', afterDelay=0, afterFn=lambda:app.getSnapshot().save(path))

    def _togglePaused(app):
        app._paused = not app._paused

    def quit(app):
        app._running = False
        app._root.quit() # break out of root.mainloop() without closing window!

    def __setattr__(app, attr, val):
        d = app.__dict__
        d[attr] = val
        canvas = d.get('_canvas', None)
        if (d.get('running', False) and
            d.get('mvcCheck', False) and
            (canvas is not None) and
            canvas.inRedrawAll):
            app._mvcViolation(f'you may not change app.{attr} in the model while in redrawAll (the view)')

    def _printUserTraceback(app, exception, tb):
        stack = traceback.extract_tb(tb)
        lines = traceback.format_list(stack)
        inRedrawAllWrapper = False
        printLines = [ ]
        for line in lines:
            if (('"cmu_112_graphics.py"' not in line) and
                ('/cmu_112_graphics.py' not in line) and
                ('\\cmu_112_graphics.py' not in line) and
                ('/tkinter/' not in line) and
                ('\\tkinter\\' not in line)):
                printLines.append(line)
            if ('redrawAllWrapper' in line):
                inRedrawAllWrapper = True
        if (len(printLines) == 0):



            if inRedrawAllWrapper:
                printLines = ['    No traceback available. Error occurred in redrawAll.\n']
            else:
                printLines = lines
        print('Traceback (most recent call last):')
        for line in printLines: print(line, end='')
        print(f'Exception: {exception}')

    def _safeMethod(appMethod):
        def m(*args, **kwargs):
            app = args[0]
            try:
                return appMethod(*args, **kwargs)
            except Exception as e:
                app._running = False
                app._printUserTraceback(e, sys.exc_info()[2])
                if ('_canvas' in app.__dict__):
                    app._canvas.inRedrawAll = True # not really, but stops recursive MVC Violations!
                    app._canvas.create_rectangle(0, 0, app.width, app.height, fill=None, width=10, outline='red')
                    app._canvas.create_rectangle(10, app.height-50, app.width-10, app.height-10,
                                                 fill='white', outline='red', width=4)
                    app._canvas.create_text(app.width/2, app.height-40, text=f'Exception! App Stopped!', fill='red', font='Arial 12 bold')
                    app._canvas.create_text(app.width/2, app.height-20, text=f'See console for details', fill='red', font='Arial 12 bold')
                    app._canvas.update()
                app.showMessage(f'Exception: {e}\nClick ok then see console for details.')
        return m

    def _methodIsOverridden(app, methodName):
        return (getattr(type(app), methodName) is not getattr(App, methodName))

    def _mvcViolation(app, errMsg):
        app._running = False
        raise Exception('MVC Violation: ' + errMsg)

    @_safeMethod
    def _redrawAllWrapper(app):
        if (not app._running): return
        if ('deferredRedrawAll' in app._afterIdMap): return # wait for pending call
        app._canvas.inRedrawAll = True
        app._canvas.delete(ALL)
        width,outline = (10,'red') if app._paused else (0,'white')
        app._canvas.create_rectangle(0, 0, app.width, app.height, fill='white', width=width, outline=outline)
        app._canvas.loggedDrawingCalls = [ ]
        app._canvas.logDrawingCalls = app._logDrawingCalls
        hash1 = getHash(app) if app._mvcCheck else None
        try:
            app.redrawAll(app._canvas)
            hash2 = getHash(app) if app._mvcCheck else None
            if (hash1 != hash2):
                app._mvcViolation('you may not change the app state (the model) in redrawAll (the view)')
        finally:
            app._canvas.inRedrawAll = False
        app._canvas.update()

    def _deferredMethodCall(app, afterId, afterDelay, afterFn, replace=False):
        def afterFnWrapper():
            app._afterIdMap.pop(afterId, None)
            afterFn()
        id = app._afterIdMap.get(afterId, None)
        if ((id is None) or replace):
            if id: app._root.after_cancel(id)
            app._afterIdMap[afterId] = app._root.after(afterDelay, afterFnWrapper)

    def _deferredRedrawAll(app):
        app._deferredMethodCall(afterId='deferredRedrawAll', afterDelay=100, afterFn=app._redrawAllWrapper, replace=True)

    @_safeMethod
    def _appStartedWrapper(app):
        app.appStarted()
        app._redrawAllWrapper()

    _keyNameMap = { '\t':'Tab', '\n':'Enter', '\r':'Enter', '\b':'Backspace',
                   chr(127):'Delete', chr(27):'Escape', ' ':'Space' }

    @staticmethod
    def _useEventKey(attr):
        raise Exception(f'Use event.key instead of event.{attr}')

    @staticmethod
    def _getEventKeyInfo(event, keysym, char):
        key = c = char
        hasControlKey = (event.state & 0x4 != 0)
        if ((c in [None, '']) or (len(c) > 1) or (ord(c) > 255)):
            key = keysym
            if (key.endswith('_L') or
                key.endswith('_R') or
                key.endswith('_Lock')):
                key = 'Modifier_Key'
        elif (c in App._keyNameMap):
            key = App._keyNameMap[c]
        elif ((len(c) == 1) and (1 <= ord(c) <= 26)):
            key = chr(ord('a')-1 + ord(c))
            hasControlKey = True
        if hasControlKey and (len(key) == 1):
            # don't add control- prefix to Enter, Tab, Escape, ...
            key = 'control-' + key
        return key

    class EventWrapper(Event):
        def __init__(self, event):
            for key in event.__dict__:
                if (not key.startswith('__')):
                    self.__dict__[key] = event.__dict__[key]

    class MouseEventWrapper(EventWrapper):
        def __repr__(self):
            return f'Event(x={self.x}, y={self.y})'

    class KeyEventWrapper(EventWrapper):
        def __init__(self, event):
            keysym, char = event.keysym, event.char
            del event.keysym
            del event.char
            super().__init__(event)
            self.key = App._getEventKeyInfo(event, keysym, char)
        def __repr__(self):
            return f'Event(key={repr(self.key)})'
        keysym = property(lambda *args: App._useEventKey('keysym'),
                          lambda *args: App._useEventKey('keysym'))
        char =   property(lambda *args: App._useEventKey('char'),
                          lambda *args: App._useEventKey('char'))

    @_safeMethod
    def _keyPressedWrapper(app, event):
        event = App.KeyEventWrapper(event)
        if (event.key == 'control-s'):
            app.saveSnapshot()
        elif (event.key == 'control-p'):
            app._togglePaused()
            app._redrawAllWrapper()
        elif (event.key == 'control-q'):
            app.quit()
        elif (event.key == 'control-x'):
            os._exit(0) # hard exit avoids tkinter error messages
        elif (app._running and
              (not app._paused) and
              app._methodIsOverridden('keyPressed') and
              (not event.key == 'Modifier_Key')):
            app.keyPressed(event)
            app._redrawAllWrapper()

    @_safeMethod
    def _keyReleasedWrapper(app, event):
        if (not app._running) or app._paused or (not app._methodIsOverridden('keyReleased')): return
        event = App.KeyEventWrapper(event)
        if (not event.key == 'Modifier_Key'):
            app.keyReleased(event)
            app._redrawAllWrapper()

    @_safeMethod
    def _mousePressedWrapper(app, event):
        if (not app._running) or app._paused: return
        if ((event.x < 0) or (event.x > app.width) or
            (event.y < 0) or (event.y > app.height)):
            app._mousePressedOutsideWindow = True
        else:
            app._mousePressedOutsideWindow = False
            app._mouseIsPressed = True
            app._lastMousePosn = (event.x, event.y)
            if (app._methodIsOverridden('mousePressed')):
                event = App.MouseEventWrapper(event)
                app.mousePressed(event)
                app._redrawAllWrapper()

    @_safeMethod
    def _mouseReleasedWrapper(app, event):
        if (not app._running) or app._paused: return
        app._mouseIsPressed = False
        if app._mousePressedOutsideWindow:
            app._mousePressedOutsideWindow = False
            app._sizeChangedWrapper()
        else:
            app._lastMousePosn = (event.x, event.y)
            if (app._methodIsOverridden('mouseReleased')):
                event = App.MouseEventWrapper(event)
                app.mouseReleased(event)
                app._redrawAllWrapper()

    @_safeMethod
    def _timerFiredWrapper(app):
        if (not app._running) or (not app._methodIsOverridden('timerFired')): return
        if (not app._paused):
            app.timerFired()
            app._redrawAllWrapper()
        app._deferredMethodCall(afterId='_timerFiredWrapper', afterDelay=app.timerDelay, afterFn=app._timerFiredWrapper)

    @_safeMethod
    def _sizeChangedWrapper(app, event=None):
        if (not app._running): return
        if (event and ((event.width < 2) or (event.height < 2))): return
        if (app._mousePressedOutsideWindow): return
        app.width,app.height,app.winx,app.winy = [int(v) for v in app._root.winfo_geometry().replace('x','+').split('+')]
        if (app._lastWindowDims is None):
            app._lastWindowDims = (app.width, app.height, app.winx, app.winy)
        else:
            newDims =(app.width, app.height, app.winx, app.winy)
            if (app._lastWindowDims != newDims):
                app._lastWindowDims = newDims
                app.updateTitle()
                app.sizeChanged()
                app._deferredRedrawAll() # avoid resize crashing on some platforms

    @_safeMethod
    def _mouseMotionWrapper(app):
        if (not app._running): return
        mouseMovedExists = app._methodIsOverridden('mouseMoved')
        mouseDraggedExists = app._methodIsOverridden('mouseDragged')
        if ((not app._paused) and
            (not app._mousePressedOutsideWindow) and
            (((not app._mouseIsPressed) and mouseMovedExists) or
             (app._mouseIsPressed and mouseDraggedExists))):
            class MouseMotionEvent(object): pass
            event = MouseMotionEvent()
            root = app._root
            event.x = root.winfo_pointerx() - root.winfo_rootx()
            event.y = root.winfo_pointery() - root.winfo_rooty()
            event = App.MouseEventWrapper(event)
            if ((app._lastMousePosn !=  (event.x, event.y)) and
                (event.x >= 0) and (event.x <= app.width) and
                (event.y >= 0) and (event.y <= app.height)):
                if (app._mouseIsPressed): app.mouseDragged(event)
                else: app.mouseMoved(event)
                app._lastMousePosn = (event.x, event.y)
                app._redrawAllWrapper()
        if (mouseMovedExists or mouseDraggedExists):
            app._deferredMethodCall(afterId='mouseMotionWrapper', afterDelay=app.mouseMovedDelay, afterFn=app._mouseMotionWrapper)

    def updateTitle(app):
        app._title = app._title or type(app).__name__
        app._root.title(f'{app._title} ({app.width} x {app.height})')

    def getQuitMessage(app):
        appLabel = type(app).__name__
        if (app._title != appLabel):
            if (app._title.startswith(appLabel)):
                appLabel = app._title
            else:
                appLabel += f" '{app._title}'"
        return f"*** Closing {appLabel}.  Bye! ***\n"

    def _showRootWindow(app):
        root = app._root
        root.update(); root.deiconify(); root.lift(); root.focus()

    def _hideRootWindow(app):
        root = app._root
        root.withdraw()

    @_safeMethod
    def run(app):
        app._mouseIsPressed = False
        app._lastMousePosn = (-1, -1)
        app._lastWindowDims= None # set in sizeChangedWrapper
        app._afterIdMap = dict()
        # create the singleton root window
        if (App._theRoot is None):
            App._theRoot = Tk()
            App._theRoot.createcommand('exit', lambda: '') # when user enters cmd-q, ignore here (handled in keyPressed)
            App._theRoot.protocol('WM_DELETE_WINDOW', lambda: App._theRoot.app.quit()) # when user presses 'x' in title bar
            App._theRoot.bind("<Button-1>", lambda event: App._theRoot.app._mousePressedWrapper(event))
            App._theRoot.bind("<B1-ButtonRelease>", lambda event: App._theRoot.app._mouseReleasedWrapper(event))
            App._theRoot.bind("<KeyPress>", lambda event: App._theRoot.app._keyPressedWrapper(event))
            App._theRoot.bind("<KeyRelease>", lambda event: App._theRoot.app._keyReleasedWrapper(event))
            App._theRoot.bind("<Configure>", lambda event: App._theRoot.app._sizeChangedWrapper(event))
        else:
            App._theRoot.canvas.destroy()
        app._root = root = App._theRoot # singleton root!
        root.app = app
        root.geometry(f'{app.width}x{app.height}+{app.winx}+{app.winy}')
        app.updateTitle()
        # create the canvas
        root.canvas = app._canvas = WrappedCanvas(app)
        app._canvas.pack(fill=BOTH, expand=YES)
        # initialize, start the timer, and launch the app
        app._running = True
        app._paused = False
        app._ignoredFields = set(app.__dict__.keys()) | {'_ignoredFields'}
        app._appStartedWrapper()
        app._timerFiredWrapper()
        app._mouseMotionWrapper()
        app._showRootWindow()
        root.mainloop()
        app._hideRootWindow()
        app._running = False
        for afterId in app._afterIdMap: app._root.after_cancel(app._afterIdMap[afterId])
        app._afterIdMap.clear() # for safety
        app.appStopped()
        print(app.getQuitMessage())


class TopLevelApp(App):
    _apps = dict() # maps fnPrefix to app

    def __init__(app, fnPrefix='', **kwargs):
        if (fnPrefix in TopLevelApp._apps):
            print(f'Quitting previous version of {fnPrefix} TopLevelApp.')
            TopLevelApp._apps[fnPrefix].quit()
        if ((fnPrefix != '') and ('title' not in kwargs)):
            kwargs['title'] = f"TopLevelApp '{fnPrefix}'"
        TopLevelApp._apps[fnPrefix] = app
        app._fnPrefix = fnPrefix
        app._callersGlobals = inspect.stack()[1][0].f_globals
        app.mode = None
        super().__init__(**kwargs)

    def _callFn(app, fn, *args):
        if (app.mode != None) and (app.mode != ''):
            fn = app.mode + '_' + fn
        fn = app._fnPrefix + fn
        if (fn in app._callersGlobals): app._callersGlobals[fn](*args)

    def redrawAll(app, canvas): app._callFn('redrawAll', app, canvas)
    def appStarted(app): app._callFn('appStarted', app)
    def appStopped(app): app._callFn('appStopped', app)
    def keyPressed(app, event): app._callFn('keyPressed', app, event)
    def keyReleased(app, event): app._callFn('keyReleased', app, event)
    def mousePressed(app, event): app._callFn('mousePressed', app, event)
    def mouseReleased(app, event): app._callFn('mouseReleased', app, event)
    def mouseMoved(app, event): app._callFn('mouseMoved', app, event)
    def mouseDragged(app, event): app._callFn('mouseDragged', app, event)
    def timerFired(app): app._callFn('timerFired', app)
    def sizeChanged(app): app._callFn('sizeChanged', app)



runApp = TopLevelApp


if (__name__ == '__main__'):
    try: import cmu_112_graphics_tests
    except: pass
