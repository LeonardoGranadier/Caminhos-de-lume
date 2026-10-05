"""Tiled-driven exploration, interactions and persistent state."""
from dataclasses import dataclass
from pathlib import Path
import json
import pytmx

BASE=Path(__file__).resolve().parent
MAPS=('vila','bosque','ruinas')

class Area:
    def __init__(self,name):
        self.name=name
        self.tmx=pytmx.TiledMap(str(BASE/'assets'/f'{name}.tmx'))
        self.w,self.h=self.tmx.width,self.tmx.height
        self.title=self.tmx.properties.get('title',name)
        self.objects=[]
        self.solid=set()
        for layer in self.tmx.layers:
            if isinstance(layer,pytmx.TiledTileLayer):
                for x,y,gid in layer:
                    if (self.tmx.get_tile_properties_by_gid(gid) or {}).get('solid',False):self.solid.add((x,y))
            elif isinstance(layer,pytmx.TiledObjectGroup):
                for o in layer:
                    self.objects.append({'id':o.name,'type':o.type,'x':int(o.x//32),'y':int(o.y//32),**o.properties})
        self.by_pos={(o['x'],o['y']):o for o in self.objects}

    def walkable(self,x,y):
        if not (0<=x<self.w and 0<=y<self.h) or (x,y) in self.solid:return False
        o=self.by_pos.get((x,y))
        return not o or o['type']=='portal'


class World:
    def __init__(self,save_path=None):
        self.areas={name:Area(name) for name in MAPS}
        self.area='vila';self.x=16;self.y=15;self.facing=(0,1)
        self.gold=0;self.fragments=0;self.key=False;self.quest=False;self.completed=False
        self.opened=set();self.visited={'vila'};self.dialog=[];self.speaker=''
        self.message='Fale com Iara, perto da praça.'
        self.save_path=Path(save_path) if save_path else None
        self.steps=0

    @property
    def current(self):return self.areas[self.area]

    def talk(self,speaker,lines):
        self.speaker=speaker;self.dialog=list(lines)

    def next_dialog(self):
        if self.dialog:self.dialog.pop(0)

    def move(self,dx,dy):
        if self.dialog or abs(dx)+abs(dy)!=1:return False
        self.facing=(dx,dy);x,y=self.x+dx,self.y+dy
        if not self.current.walkable(x,y):return False
        o=self.current.by_pos.get((x,y))
        if o and o['type']=='portal':
            if o.get('requires')=='key' and not self.key:
                self.talk('Portão antigo',['O portão está trancado.','Procure a chave antiga em um baú no bosque.'])
                return False
            destination=o.get('destination')
            if destination not in self.areas:
                self.message='Destino inválido no mapa.';return False
            sx,sy=int(o['spawn_x']),int(o['spawn_y'])
            if not self.areas[destination].walkable(sx,sy):
                self.message='Ponto de entrada bloqueado no mapa.';return False
            self.area=destination;self.x=sx;self.y=sy
            self.visited.add(destination);self.message=self.current.title;self.save()
        else:self.x=x;self.y=y
        self.steps+=1
        return True

    def nearby(self):
        dx,dy=self.facing
        points=[(self.x+dx,self.y+dy),(self.x,self.y-1),(self.x+1,self.y),(self.x,self.y+1),(self.x-1,self.y)]
        for p in points:
            o=self.current.by_pos.get(p)
            if o and o['type']!='portal':return o
        return None

    def interact(self):
        if self.dialog:self.next_dialog();return
        o=self.nearby()
        if not o:self.message='Aproxime-se de alguém, de um baú ou de uma placa.';return
        kind=o['type']
        if kind=='chest':
            if o['id'] in self.opened:
                self.talk('Baú',['Você já recolheu o conteúdo deste baú.']);return
            reward=o['reward'];amount=int(o.get('amount',1))
            if reward=='fragment':self.fragments+=amount;line=f'Fragmento de luz encontrado! {self.fragments}/3'
            elif reward=='key':self.key=True;line='Você encontrou a chave antiga das ruínas!'
            elif reward=='gold':self.gold+=amount;line=f'Você encontrou {amount} moedas!'
            else:self.message='Recompensa desconhecida.';return
            self.opened.add(o['id']);self.talk('Tesouro',[line]);self.message=line;self.save()
        elif kind=='sign':self.talk('Placa',[o.get('text','')])
        elif kind=='beacon':
            if self.completed:self.talk('Farol de Lume',['A luz voltou para a vila. Obrigado por explorar!'])
            elif self.fragments>=3:
                self.completed=True;self.gold+=100
                self.talk('Farol de Lume',['Os três fragmentos despertam o farol!','Lume volta a brilhar. Você recebeu 100 moedas.','A aventura foi concluída. Continue explorando livremente.']);self.save()
            else:self.talk('Farol de Lume',[f'Faltam {3-self.fragments} fragmentos para restaurar a luz.'])
        elif kind=='npc':
            topic=o.get('dialog')
            if o.get('text'):
                lines=o['text'].split('|')
            elif topic=='quest':
                if self.completed:lines=['Você restaurou nosso farol. A vila será sempre sua casa!']
                elif self.fragments>=3:lines=['Você reuniu os fragmentos!','Leve-os ao farol, ao norte da praça.']
                else:lines=['Sou Iara. O farol de Lume perdeu sua luz.','Há três fragmentos: um na vila, um no bosque e um nas ruínas.','Abra os baús e traga os fragmentos ao farol. M abre seu mapa.']
                self.quest=True;self.save()
            elif topic=='hint':lines=['Ouvi dizer que há um baú no sudoeste da vila.','As passagens na borda dos mapas levam a outras áreas.']
            elif topic=='forest':lines=['A chave das ruínas está em um baú no noroeste.','O fragmento deste bosque fica a sudeste.','Depois, siga para o portão no nordeste.']
            else:lines=['Sou o eco de quem guardava este lugar.','O último fragmento está na sala nordeste.','As aberturas entre as colunas formam o caminho.']
            self.talk(o['id'],lines)

    def save(self):
        if not self.save_path:return True
        data={name:getattr(self,name) for name in ['area','x','y','gold','fragments','key','quest','completed']}
        data.update(version=1,opened=sorted(self.opened),visited=sorted(self.visited))
        try:
            self.save_path.parent.mkdir(exist_ok=True,parents=True)
            tmp=self.save_path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(self.save_path)
            return True
        except OSError:self.message='Não foi possível salvar.';return False

    def load(self):
        if not self.save_path or not self.save_path.exists():return False
        try:
            d=json.loads(self.save_path.read_text(encoding='utf-8'))
            if d['version']!=1 or d['area'] not in self.areas:raise ValueError()
            for n in ['x','y','gold','fragments']:
                if type(d[n]) is not int or d[n]<0:raise ValueError()
            if d['fragments']>3 or not self.areas[d['area']].walkable(d['x'],d['y']):raise ValueError()
            known={o['id'] for a in self.areas.values() for o in a.objects if o['type']=='chest'}
            if not set(d['opened'])<=known or not set(d['visited'])<=set(MAPS):raise ValueError()
            for n in ['key','quest','completed']:
                if type(d[n]) is not bool:raise ValueError()
            for n in ['area','x','y','gold','fragments','key','quest','completed']:setattr(self,n,d[n])
            self.opened=set(d['opened']);self.visited=set(d['visited']);self.dialog=[]
            self.message='Progresso carregado.';return True
        except (OSError,ValueError,KeyError,TypeError):self.message='Arquivo de progresso inválido.';return False
