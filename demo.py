import os
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
from game import App,View,World,pg,W,H
from routes import route_object,JOURNEY

class Demo:
    def __init__(self):
        self.app=App(World());self.index=0;self.path=[];self.hold=2.;self.step_clock=0
        self.started=False;self.done=False;self.records=[];self.obj=None;self.dialog_clock=0

    def tick(self,t,dt):
        a=self.app;w=a.world
        a.update(dt*3) # Travel is explicitly accelerated in the demonstration.
        if self.done:return
        if not self.started:
            if t>=2:a.key(pg.K_RETURN);self.started=True;self.hold=0
            return
        if self.hold>0:
            self.hold-=dt
            return
        if w.dialog:
            self.dialog_clock+=dt
            if self.dialog_clock>=1.6:a.key(pg.K_RETURN);self.dialog_clock=0
            return
        if self.obj is None:
            if self.index>=len(JOURNEY):self.done=True;return
            name=JOURNEY[self.index];self.obj=next(o for o in w.current.objects if o['id']==name)
            self.path=route_object(w,name)
        self.step_clock+=dt
        if self.path:
            if self.step_clock<.055:return
            self.step_clock=0
            x,y=self.path[0];dx,dy=x-w.x,y-w.y
            key={(1,0):pg.K_RIGHT,(-1,0):pg.K_LEFT,(0,1):pg.K_DOWN,(0,-1):pg.K_UP}[dx,dy]
            old=(w.area,w.x,w.y);a.key(key)
            if old!=(w.area,w.x,w.y):self.path.pop(0)
            return
        name=self.obj['id'];self.records.append((round(t,2),name,w.area))
        if self.obj['type']!='portal':
            w.facing=(self.obj['x']-w.x,self.obj['y']-w.y)
            a.key(pg.K_e)
        self.hold=.5;self.obj=None;self.index+=1

if __name__=='__main__':
    from pathlib import Path
    pg.init();pg.display.set_mode((1,1));canvas=pg.Surface((W,H));view=View(canvas);demo=Demo()
    folder=Path(__file__).resolve().parent/'previews';folder.mkdir(exist_ok=True)
    for i in range(90*24):
        t=i/24;demo.tick(t,1/24)
        if i%120==0:view.draw(demo.app,t);pg.image.save(canvas,str(folder/f'game-{int(t):02d}.png'))
    print(demo.records);print('Concluído:',demo.app.world.completed,'passos:',demo.app.world.steps)
    assert demo.app.world.completed
    pg.quit()
