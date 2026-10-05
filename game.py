from pathlib import Path
import os
import sys
import math
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'.deps'))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
if '--smoke' in sys.argv:
    os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
try:
    import pygame as pg
    import pytmx
    from pytmx.util_pygame import load_pygame
except ImportError:
    raise SystemExit('Instale as dependências: python -m pip install -r requirements.txt')
from world import World,MAPS

W,H,T=960,640,48
WHITE=(241,236,214);GOLD=(246,205,119);MUTED=(170,191,182);INK=(20,38,39)

class App:
    def __init__(self,world):
        self.world=world;self.title=True;self.help=False;self.minimap=False;self.inventory=False
        self.running=True;self.cooldown=0;self.visual=[world.x,world.y];self.from_pos=self.visual[:];self.elapsed=1;self.transition=0

    def sync(self):
        self.visual=[self.world.x,self.world.y];self.from_pos=self.visual[:];self.elapsed=1

    def key(self,key):
        w=self.world
        if key==pg.K_F1:self.help=not self.help;return
        if self.help:
            if key==pg.K_ESCAPE:self.help=False
            return
        if self.title:
            if key in [pg.K_RETURN,pg.K_SPACE]:
                w.load();self.title=False;self.sync()
            elif key==pg.K_ESCAPE:self.running=False
            return
        if key==pg.K_ESCAPE:
            if w.dialog:w.dialog=[]
            elif self.minimap or self.inventory:self.minimap=False;self.inventory=False
            else:w.save();self.running=False
        elif key==pg.K_m:self.minimap=not self.minimap;self.inventory=False
        elif key in [pg.K_i,pg.K_TAB]:self.inventory=not self.inventory;self.minimap=False
        elif key==pg.K_F5:
            if w.save():w.message='Progresso salvo.'
        elif key==pg.K_F9:
            w.load();self.sync()
        elif self.minimap or self.inventory:return
        elif key in [pg.K_e,pg.K_RETURN,pg.K_SPACE]:w.interact()
        else:
            move={pg.K_w:(0,-1),pg.K_UP:(0,-1),pg.K_s:(0,1),pg.K_DOWN:(0,1),pg.K_a:(-1,0),pg.K_LEFT:(-1,0),pg.K_d:(1,0),pg.K_RIGHT:(1,0)}
            if key in move and self.cooldown<=0:
                before=[w.x,w.y];old=w.area
                if w.move(*move[key]):
                    if old!=w.area:self.sync();self.transition=.4
                    else:self.from_pos=before;self.elapsed=0
                    self.cooldown=.13

    def update(self,dt):
        self.cooldown=max(0,self.cooldown-dt);self.transition=max(0,self.transition-dt)
        self.elapsed=min(1,self.elapsed+dt/.13)
        u=self.elapsed*(2-self.elapsed)
        self.visual=[self.from_pos[0]+(self.world.x-self.from_pos[0])*u,self.from_pos[1]+(self.world.y-self.from_pos[1])*u]


class View:
    def __init__(self,surface):
        self.s=surface;self.fonts={}
        self.maps={name:load_pygame(str(BASE/'assets'/f'{name}.tmx'),pixelalpha=True) for name in MAPS}
        self.tiles={}
        for name,tmx in self.maps.items():
            self.tiles[name]={gid:pg.transform.scale(image,(T,T)) for gid,image in enumerate(tmx.images) if image is not None}
        atlas=pg.image.load(str(BASE/'assets'/'tiles.png')).convert_alpha()
        self.icons={n:pg.transform.scale(atlas.subsurface(((n%8)*32,(n//8)*32,32,32)),(T,T)) for n in range(16)}

    def font(self,size,bold=False):
        if (size,bold) not in self.fonts:self.fonts[size,bold]=pg.font.Font(pg.font.match_font('dejavusans',bold=bold),size)
        return self.fonts[size,bold]

    def text(self,text,x,y,size=20,color=WHITE,bold=False,center=False):
        image=self.font(size,bold).render(str(text),True,color)
        self.s.blit(image,(x-image.get_width()//2 if center else x,y))

    def panel(self,rect,color=INK,edge=(104,139,119)):
        pg.draw.rect(self.s,(10,25,25),pg.Rect(rect).move(3,4),border_radius=10)
        pg.draw.rect(self.s,color,rect,border_radius=10);pg.draw.rect(self.s,edge,rect,2,border_radius=10)

    def wrapped(self,text,x,y,maxwidth=790,size=20,color=WHITE):
        line='';yy=y
        for word in text.split():
            test=(line+' '+word).strip()
            if self.font(size).size(test)[0]>maxwidth:
                self.text(line,x,yy,size,color);yy+=size+10;line=word
            else:line=test
        if line:self.text(line,x,yy,size,color)

    def person(self,x,y,color,t,hero=False,moving=False):
        x=int(x);y=int(y)
        pg.draw.ellipse(self.s,(32,61,47),(x+7,y+34,34,11))
        stride=int(math.sin(t*13)*3) if moving else 0
        pg.draw.rect(self.s,(44,47,56),(x+14,y+31+stride,8,10))
        pg.draw.rect(self.s,(44,47,56),(x+27,y+31-stride,8,10))
        pg.draw.rect(self.s,color,(x+12,y+19,26,19))
        pg.draw.rect(self.s,(239,205,163),(x+13,y+7,24,20))
        pg.draw.rect(self.s,(61,53,49),(x+11,y+3,29,10))
        pg.draw.rect(self.s,(61,53,49),(x+11,y+9,5,12))
        pg.draw.rect(self.s,(32,44,42),(x+19,y+15,3,4));pg.draw.rect(self.s,(32,44,42),(x+30,y+15,3,4))
        pg.draw.rect(self.s,(239,205,163),(x+6,y+24,7,10));pg.draw.rect(self.s,(239,205,163),(x+38,y+24,7,10))
        if hero:
            pg.draw.rect(self.s,GOLD,(x+12,y+25,26,5));pg.draw.rect(self.s,(62,92,111),(x+36,y+21,7,17))

    def draw(self,app,t):
        w=app.world;a=w.current;tmx=self.maps[w.area]
        px,py=app.visual
        cx=max(0,min(a.w*T-W,(px+.5)*T-W/2));cy=max(0,min(a.h*T-512,(py+.5)*T-256))
        self.s.fill((38,61,50));self.s.set_clip((0,64,W,512))
        for layer in tmx.visible_layers:
            if not isinstance(layer,pytmx.TiledTileLayer):continue
            for x,y,gid in layer:
                sx,sy=x*T-cx,y*T-cy+64
                if -T<sx<W and 64-T<sy<576 and gid:
                    tile=self.tiles[w.area].get(gid)
                    if tile:self.s.blit(tile,(int(sx),int(sy)))
        actors=[]
        for o in a.objects:
            x,y=o['x']*T-cx,o['y']*T-cy+64
            if not -T<x<W or not 64-T<y<576:continue
            kind=o['type']
            if kind=='npc':actors.append((o['y'],x,y,o))
            elif kind=='chest':self.s.blit(self.icons[13 if o['id'] in w.opened else 12],(int(x),int(y)))
            elif kind=='beacon':
                self.s.blit(self.icons[15],(int(x),int(y+3*math.sin(t*2))))
                if w.completed:
                    for i in range(5):
                        angle=t+i*1.25;pg.draw.circle(self.s,GOLD,(int(x+24+math.cos(angle)*36),int(y+22+math.sin(angle)*30)),3)
            elif kind=='sign':self.s.blit(self.icons[14],(int(x),int(y)))
            elif kind=='portal':
                pg.draw.ellipse(self.s,(216,191,112),(x+3,y+24,42,19),3)
                self.text('↗',x+24,y-3,28,GOLD,True,True)
        actors.append((py,px*T-cx,py*T-cy+64,None))
        for _,x,y,o in sorted(actors,key=lambda a:a[0]):
            self.person(x,y,(57,140,151) if not o else (144,104,156) if o['id']=='Iara' else (140,144,92),t,not o,not o and app.elapsed<1)
            if o and abs(w.x-o['x'])+abs(w.y-o['y'])<=3:self.text(o['id'],x+24,y-19,16,GOLD,True,True)
        if w.area=='bosque':
            for i in range(14):
                x=(i*137+math.sin(t+i)*10)%W;y=100+(i*61)%425
                pg.draw.circle(self.s,(230,218,145),(int(x),int(y)),2)
        self.s.set_clip(None)
        pg.draw.rect(self.s,INK,(0,0,W,64));pg.draw.line(self.s,(105,133,107),(0,63),(W,63),2)
        self.text(a.title,23,12,23,GOLD,True)
        self.text(f'Fragmentos {w.fragments}/3',480,12,19,WHITE)
        self.text(f'{w.gold} moedas',735,12,19,GOLD)
        self.text('Farol restaurado!' if w.completed else 'Missão: restaure o farol de Lume',25,41,14,MUTED)
        self.text('Chave antiga ✓' if w.key else 'Explore e converse',735,41,14,MUTED)
        pg.draw.rect(self.s,INK,(0,576,W,64))
        nearby=w.nearby();hint=f'E: {nearby["id"].replace("_"," ")}' if nearby else 'WASD / setas: andar · E: interagir · M: mapa · I: mochila'
        self.text(hint,480,583,16,WHITE,center=True)
        self.text(w.message[:112],480,611,14,MUTED,center=True)
        if w.dialog:
            self.panel((55,401,850,162),edge=GOLD)
            self.text(w.speaker,79,414,22,GOLD,True)
            self.wrapped(w.dialog[0],79,449,790,20)
            self.text('E / Enter: continuar · Esc: fechar',480,535,15,MUTED,center=True)
        if app.minimap:
            self.panel((174,94,612,457),edge=GOLD)
            self.text('MAPA DA ÁREA',480,110,25,GOLD,True,True)
            size=min(11,480//a.w,280//a.h);ox=480-a.w*size//2;oy=157
            for y in range(a.h):
                for x in range(a.w):pg.draw.rect(self.s,(51,72,67) if (x,y) in a.solid else (112,146,101),(ox+x*size,oy+y*size,size,size))
            for o in a.objects:
                color=GOLD if o['type']=='chest' else (119,217,218) if o['type']=='portal' else (202,156,215)
                pg.draw.rect(self.s,color,(ox+o['x']*size,oy+o['y']*size,size,size))
            pg.draw.rect(self.s,(255,255,255),(ox+w.x*size,oy+w.y*size,size,size))
            self.text('Branco: você · Ouro: baú · Ciano: passagem',480,462,16,WHITE,center=True)
            self.text('Vila ↔ Bosque ↔ Ruínas',480,492,19,GOLD,True,True)
            self.text('M ou Esc: fechar',480,525,14,MUTED,center=True)
        if app.inventory:
            self.panel((216,158,528,302),edge=GOLD)
            self.text('MOCHILA',480,177,29,GOLD,True,True)
            for i,s in enumerate([f'Moedas: {w.gold}',f'Fragmentos de luz: {w.fragments}/3',f'Chave antiga: {"sim" if w.key else "não"}',f'Baús abertos: {len(w.opened)}/7',f'Áreas visitadas: {len(w.visited)}/3']):self.text(s,258,232+i*36,20)
        if app.title:
            shade=pg.Surface((W,H),pg.SRCALPHA);shade.fill((7,24,28,200));self.s.blit(shade,(0,0))
            self.text('UMA AVENTURA EM TILES',480,113,19,MUTED,True,True)
            self.text('CAMINHOS',480,171,66,GOLD,True,True)
            self.text('DE LUME',480,244,49,WHITE,True,True)
            self.text('Explore. Converse. Descubra.',480,332,23,MUTED,center=True)
            self.panel((225,398,510,96),edge=GOLD)
            self.text('Enter: começar / continuar',480,418,24,WHITE,True,True)
            self.text('F1: ajuda · Esc: sair',480,459,16,MUTED,center=True)
            self.text('Python + Pygame + pytmx · mapas editáveis no Tiled',480,558,17,MUTED,center=True)
        if app.help:
            self.panel((103,75,754,482),edge=GOLD)
            self.text('GUIA DE LUME',480,94,30,GOLD,True,True)
            lines=['WASD/setas: andar. E/Enter: interagir e avançar diálogos.',
                   'M: mapa da área. I/Tab: mochila. F1: esta ajuda.',
                   'F5: salvar. F9: carregar. Esc: fechar painel ou salvar e sair.',
                   'Fale com Iara na praça para conhecer a missão.',
                   'Encontre um fragmento em cada uma das três áreas.',
                   'A chave no bosque abre a passagem para as ruínas.',
                   'Leve os três fragmentos ao farol ao norte da praça.',
                   'Baús, moedas, missão e localização são salvos.',
                   'Este protótipo é de exploração, sem combate.',
                   'F1 ou Esc para voltar à aventura.']
            for i,line in enumerate(lines):self.text(line,128,154+i*36,17,WHITE)
        if app.transition:
            shade=pg.Surface((W,H),pg.SRCALPHA);shade.fill((20,38,39,int(110*app.transition/.4)));self.s.blit(shade,(0,0))

def main():
    pg.init();screen=pg.display.set_mode((W,H),pg.RESIZABLE);pg.display.set_caption('Caminhos de Lume — exploração em tiles')
    canvas=pg.Surface((W,H));view=View(canvas)
    smoke='--smoke' in sys.argv
    app=App(World(None if smoke else BASE/'saves'/'save.json'));clock=pg.time.Clock();t=0;frames=0
    while app.running:
        dt=min(clock.tick(60)/1000,.1);t+=dt
        for e in pg.event.get():
            if e.type==pg.QUIT:app.world.save();app.running=False
            elif e.type==pg.KEYDOWN:app.key(e.key)
        keys=pg.key.get_pressed()
        for key in [pg.K_w,pg.K_a,pg.K_s,pg.K_d,pg.K_UP,pg.K_LEFT,pg.K_DOWN,pg.K_RIGHT]:
            if keys[key]:app.key(key);break
        app.update(dt);view.draw(app,t)
        sw,sh=screen.get_size();scale=min(sw/W,sh/H);image=pg.transform.scale(canvas,(max(1,int(W*scale)),max(1,int(H*scale))))
        screen.fill((8,18,20));screen.blit(image,((sw-image.get_width())//2,(sh-image.get_height())//2));pg.display.flip()
        frames+=1
        if smoke and frames==2:app.key(pg.K_RETURN)
        if smoke and frames==4:app.key(pg.K_m)
        if smoke and frames>=8:app.running=False
    pg.quit()

if __name__=='__main__':main()
