"""Generate original tiles and editable Tiled TMX/TSX assets. Pillow only."""
from pathlib import Path
from PIL import Image, ImageDraw
import random
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent/'assets'
T=32

def atlas():
    image=Image.new('RGBA',(256,64));rng=random.Random(42)
    for n in range(16):
        tile=Image.new('RGBA',(32,32));d=ImageDraw.Draw(tile)
        if n in [0,1,4,5,9,11]:
            colors={0:'#547e59',1:'#c4ab7b',4:'#7d858c',5:'#a57c54',9:'#536572',11:'#a88761'}
            d.rectangle((0,0,31,31),fill=colors[n])
            for _ in range(12):
                x,y=rng.randrange(32),rng.randrange(32)
                d.line((x,y,x+2,y),fill={0:'#638f61',1:'#b49a6d',4:'#91999e',5:'#7f5e43',9:'#637685',11:'#725b47'}[n])
            if n in [5,11]:
                for y in [4,13,23]:d.line((0,y,31,y),fill='#665241',width=2)
            if n==9:
                d.line((0,0,31,0),fill='#364956');d.line((0,0,0,31),fill='#364956')
        elif n==2:
            d.rectangle((0,0,31,31),fill='#315f77')
            for x,y in [(3,8),(18,19),(8,29)]:d.line((x,y,x+9,y),fill='#4d869c',width=2)
        elif n==3:
            d.ellipse((1,20,31,31),fill='#294c41')
            d.rectangle((13,15,19,31),fill='#76573f')
            d.polygon([(16,0),(29,14),(24,14),(32,25),(0,25),(9,13),(3,13)],fill='#2d5748')
            d.polygon([(16,1),(23,14),(9,14)],fill='#467756')
            d.line((9,18,23,18),fill='#3c6a4f',width=3)
        elif n==6:
            d.rectangle((0,0,31,31),fill='#ceb88c')
            d.rectangle((1,1,30,30),outline='#96744f',width=2)
            d.line((0,15,31,15),fill='#b29a73',width=2)
        elif n==7:
            d.rectangle((0,0,31,31),fill='#925251')
            for y in range(0,32,8):
                d.line((0,y,31,y),fill='#b36960',width=2)
                for x in range(0,32,16):d.line((x+(y%16),y,x+(y%16),y+7),fill='#6b4549')
        elif n==8:
            for x,y in [(7,8),(23,22),(9,27)]:
                d.line((x,y,x,y+4),fill='#375c44');d.ellipse((x-2,y-2,x+2,y+2),fill='#f3ce7c')
        elif n==10:
            d.ellipse((4,25,28,31),fill='#273d48')
            d.rectangle((9,5,24,27),fill='#87959d')
            d.rectangle((5,1,27,7),fill='#a3aeb0')
            d.rectangle((5,25,28,29),fill='#627983')
            d.line((13,8,13,23),fill='#b2b9b3',width=2)
        elif n in [12,13]:
            d.ellipse((2,24,30,31),fill='#293d35')
            d.rectangle((4,12,28,28),fill='#81523c',outline='#382e2b',width=2)
            d.rectangle((4,9 if n==12 else 2,28,17 if n==12 else 9),fill='#b17c47',outline='#f2d082',width=2)
            if n==13:d.rectangle((7,11,25,17),fill='#201f29')
            d.rectangle((14,16,18,21),fill='#f2d082')
        elif n==14:
            d.rectangle((14,11,18,31),fill='#755b44')
            d.rectangle((3,3,29,18),fill='#aa8859',outline='#dfc389',width=2)
            d.line((9,10,23,10),fill='#453e38',width=2)
        else:
            d.ellipse((3,22,29,31),fill='#435c6f')
            d.polygon([(16,0),(27,13),(16,28),(5,13)],fill='#79dfd1',outline='#e0f2c5')
            d.line((16,2,16,25),fill='#c5fff0',width=2)
        image.paste(tile,((n%8)*32,(n//8)*32))
    ROOT.mkdir(parents=True,exist_ok=True)
    image.save(ROOT/'tiles.png')
    ts=ET.Element('tileset',version='1.10',tiledversion='1.11.0',name='Lume',tilewidth='32',tileheight='32',tilecount='16',columns='8')
    ET.SubElement(ts,'image',source='tiles.png',width='256',height='64')
    for n in [2,3,6,7,10]:
        tile=ET.SubElement(ts,'tile',id=str(n));props=ET.SubElement(tile,'properties')
        ET.SubElement(props,'property',name='solid',type='bool',value='true')
    ET.indent(ts);ET.ElementTree(ts).write(ROOT/'lume.tsx',encoding='UTF-8',xml_declaration=True)

def obj(kind,name,x,y,**properties):return dict(kind=kind,name=name,x=x,y=y,props=properties)

def create(name,w,h,kind,objects):
    rng=random.Random(name)
    ground=[[10 if kind=='ruins' else 1 for x in range(w)] for y in range(h)]
    detail=[[0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if x in [0,w-1] or y in [0,h-1]:detail[y][x]=11 if kind=='ruins' else 4
            elif kind!='ruins' and rng.random()<.05:detail[y][x]=9
    def path(x1,y1,x2,y2):
        for x in range(min(x1,x2),max(x1,x2)+1):ground[y1][x]=2;detail[y1][x]=0
        for y in range(min(y1,y2),max(y1,y2)+1):ground[y][x2]=2;detail[y][x2]=0
    if kind=='village':
        for y in [12,16]:path(3,y,w-2,y)
        path(16,4,16,21);path(6,7,8,12)
        for x,y in [(3,3),(22,4),(22,16)]:
            for yy in range(y,y+4):
                for xx in range(x,x+6):detail[yy][xx]=8 if yy<y+2 else 7
        for y in range(18,22):
            for x in range(10,14):ground[y][x]=3
    elif kind=='forest':
        for y in range(1,h-1):
            for x in range(1,w-1):
                if rng.random()<.17:detail[y][x]=4
        path(2,15,44,15);path(12,15,12,8);path(36,15,36,21);path(44,15,44,5)
        for y in range(21,27):
            for x in range(20,28):ground[y][x]=3;detail[y][x]=0
    else:
        for x in [8,18]:
            for y in range(3,21):
                if y not in [10,14]:detail[y][x]=11
        for x,y in [(4,4),(14,6),(26,17),(23,11)]:detail[y][x]=11
    for o in objects:
        x,y=o['x'],o['y'];detail[y][x]=0
        # Guarantee a walkable approach to every interactive object.
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            if 0<x+dx<w-1 and 0<y+dy<h-1:detail[y+dy][x+dx]=0
    titles={'vila':'Vila de Lume','bosque':'Bosque das Lanternas','ruinas':'Ruínas da Primeira Luz'}
    root=ET.Element('map',version='1.10',tiledversion='1.11.0',orientation='orthogonal',renderorder='right-down',width=str(w),height=str(h),tilewidth='32',tileheight='32',infinite='0',nextlayerid='4',nextobjectid=str(len(objects)+1))
    props=ET.SubElement(root,'properties');ET.SubElement(props,'property',name='title',value=titles[name])
    ET.SubElement(root,'tileset',firstgid='1',source='lume.tsx')
    for lid,label,grid in [(1,'Chao',ground),(2,'Detalhes',detail)]:
        layer=ET.SubElement(root,'layer',id=str(lid),name=label,width=str(w),height=str(h))
        data=ET.SubElement(layer,'data',encoding='csv');data.text='\n'+',\n'.join(','.join(map(str,row)) for row in grid)+'\n'
    layer=ET.SubElement(root,'objectgroup',id='3',name='Objetos')
    for i,o in enumerate(objects):
        el=ET.SubElement(layer,'object',id=str(i+1),name=o['name'],type=o['kind'],x=str(o['x']*32),y=str(o['y']*32),width='32',height='32')
        props=ET.SubElement(el,'properties')
        for key,val in o['props'].items():ET.SubElement(props,'property',name=key,value=str(val))
    ET.indent(root);ET.ElementTree(root).write(ROOT/f'{name}.tmx',encoding='UTF-8',xml_declaration=True)

def main():
    atlas()
    create('vila',32,24,'village',[
        obj('npc','Iara',13,12,dialog='quest'),obj('npc','Bento',8,8,dialog='hint'),
        obj('chest','vila_fragmento',6,17,reward='fragment',amount=1),
        obj('chest','vila_moedas',26,11,reward='gold',amount=30),
        obj('beacon','Farol',16,6),obj('sign','placa_vila',28,12,text='Leste: Bosque das Lanternas. M abre o mapa.'),
        obj('portal','saida_bosque',30,12,destination='bosque',spawn_x=3,spawn_y=15)])
    create('bosque',48,30,'forest',[
        obj('portal','volta_vila',2,15,destination='vila',spawn_x=29,spawn_y=12),
        obj('npc','Caio',23,14,dialog='forest'),
        obj('chest','chave_antiga',12,8,reward='key',amount=1),
        obj('chest','bosque_fragmento',36,21,reward='fragment',amount=1),
        obj('chest','bosque_moedas',8,16,reward='gold',amount=45),
        obj('sign','placa_ruinas',43,6,text='As ruínas guardam a última luz. Procure a chave no noroeste.'),
        obj('portal','entrada_ruinas',44,5,destination='ruinas',spawn_x=3,spawn_y=18,requires='key')])
    create('ruinas',32,24,'ruins',[
        obj('portal','volta_bosque',2,18,destination='bosque',spawn_x=44,spawn_y=6),
        obj('npc','Eco',14,14,dialog='ruins'),
        obj('chest','ruinas_fragmento',24,7,reward='fragment',amount=1),
        obj('chest','ruinas_moedas',25,18,reward='gold',amount=80),
        obj('sign','inscricao',5,18,text='Três fragmentos, uma só luz. Leve-os ao farol da vila.')])
    print('Atlas original, TSX e três mapas TMX gerados.')

if __name__=='__main__':main()
