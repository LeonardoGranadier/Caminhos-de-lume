from collections import deque

def path_to(world,point,allow_portal=False):
    start=(world.x,world.y);area=world.current
    queue=deque([start]);previous={start:None}
    while queue:
        pos=queue.popleft()
        if pos==point:
            path=[]
            while previous[pos] is not None:path.append(pos);pos=previous[pos]
            return list(reversed(path))
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            p=pos[0]+dx,pos[1]+dy
            if p in previous or not area.walkable(*p):continue
            o=area.by_pos.get(p)
            if o and o['type']=='portal' and not (allow_portal and p==point):continue
            previous[p]=pos;queue.append(p)
    raise ValueError(f'Sem caminho em {world.area}: {start} -> {point}')

def route_object(world,object_id):
    obj=next(o for o in world.current.objects if o['id']==object_id)
    if obj['type']=='portal':return path_to(world,(obj['x'],obj['y']),True)
    paths=[]
    for dx,dy in [(0,1),(1,0),(-1,0),(0,-1)]:
        try:paths.append(path_to(world,(obj['x']+dx,obj['y']+dy)))
        except ValueError:pass
    if not paths:raise ValueError(f'Objeto sem acesso: {object_id}')
    return min(paths,key=len)

def arrive(world,object_id):
    obj=next(o for o in world.current.objects if o['id']==object_id)
    for x,y in route_object(world,object_id):
        if not world.move(x-world.x,y-world.y):raise ValueError(f'Movimento bloqueado para {object_id}')
    if obj['type']!='portal':world.facing=(obj['x']-world.x,obj['y']-world.y)

def close_dialog(world):
    while world.dialog:world.next_dialog()

JOURNEY=['Iara','vila_fragmento','saida_bosque','Caio','chave_antiga',
         'bosque_fragmento','entrada_ruinas','Eco','ruinas_fragmento',
         'volta_bosque','volta_vila','Farol']
