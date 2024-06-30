import pygame
import random
import os
import math




pygame.init()
HEIGHT=640
WIDTH=1024
FPS=60
screen = pygame.display.set_mode((WIDTH,HEIGHT))
PSpeedX=6
PSpeedY=6
enemys=[]
PATH='C:\\Users\\Dell\\Desktop\\pygame\\platformer\\'
def displayBackground():
    image = pygame.image.load(PATH+"sprits\\platforms\\background_.jpg")
    _,_,width,height= image.get_rect()
    for i in range(HEIGHT//height+1):
        for j in range(WIDTH//width+1):
            screen.blit(image,(j*width,i*height))


def flip(sprites):
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites]

def lode_sprite_sheets(dir1,width,height,direction=False):
    
    all_sprites={}

    images= os.listdir(os.path.join(PATH+"sprits",dir1))
    for image in images:
        sprite_sheet=pygame.image.load(os.path.join(PATH+"sprits",dir1,image)).convert_alpha()
        sprite_sheet = pygame.transform.scale(sprite_sheet, (int(sprite_sheet.get_width() ), int(sprite_sheet.get_height() )))
        sprites=[]
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect = pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append(surface)

        all_sprites[image.replace('.png',''+'_right')]=sprites
        if direction:
            all_sprites[image.replace('.png',''+'_left')]=flip(sprites)
    return all_sprites


def load_block(size,type):
    if type=='GB':
        path=os.path.join(PATH,'sprits','platforms','midground_.png')
    elif type=='SKP':
        path=os.path.join(PATH,'sprits','platforms','evelmidground_.png')
    image=pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect((16,32,size,size))
    surface.blit(image,(0,0),rect)
    return surface

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None) -> None:
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.name=name
        self.width=width
        self.height=height

    def drow(self,window):
        window.blit(self.image,(self.rect.x,self.rect.y))
        if self.type=="SKP":
            if self.timer/FPS==2:
                enemys.append(Enemy(self.rect.left,self.rect.top,40,65))
                self.timer=0
            self.timer+=1

class Block(Object):
    def __init__(self,x,y,size,type):
        if type=='SKP':
            self.timer=0
        super().__init__(x,y,size,size)
        self.type=type
        block = load_block(size,self.type)
        self.image.blit(block,(0,0))
        self.mask=pygame.mask.from_surface(self.image)
    def update_block(self):
        self.image = load_block(self.rect.width,self.type)


class Entity(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,sprite_dir) -> None:
        width=int(width*1)
        height=int(height*1)
        super().__init__()
        self.SPRITES = lode_sprite_sheets(dir1=sprite_dir,width=width,height=height,direction=True)
        self.sprite=''
        self.animation_delay=2 
        self.animation_type=0
        self.rect= pygame.Rect(x,y,width,height)
        self.x_vel=0
        self.y_vel=0
        self.mask=None
        self.direction='left'
        self.animation_count=0
        self.Gravity=1
        self.fall_count=0
        self.jump_count=0
        self.HP=0

    def move(self,dx,dy):
        self.rect.x+=dx
        self.rect.y+=dy

    def move_left(self,vel):
        self.rect.x-=vel
        self.direction='left'

    def move_right(self,vel):
        self.rect.x+=vel
        self.direction='right'

    def loop(self,fps):
        self.y_vel += min(1, (self.fall_count/fps)*self.Gravity)
        self.move(self.x_vel,self.y_vel)
        self.fall_count+=1            

    
    def update(self):
        self.rect=self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask= pygame.mask.from_surface(self.sprite)
        pass

    def drow(self,window):
        ans=self.update_animation()
        window.blit(self.sprite,(self.rect.x,self.rect.y))
        self.update() 
        #pygame.draw.rect(window,(255,0,0),self.rect)
        return ans
    
    def landed(self):
        self.fall_count=0
        self.jump_count=0

    def hit_head(self):
        self.y_vel*=-1

    def jump(self):
        self.y_vel=-1*PSpeedY
        self.animation_count=0
        self.jump_count=(self.jump_count+1)%2
        if self.jump_count!=1:
            self.fall_count=0
        self.animation_type=3

    


class Player(Entity):
    def __init__(self, x, y, width, height) -> None:
        super().__init__(x, y, width, height,'wizard')
        self.HP=20
        self.score=0

    def update_animation(self):
        if self.HP<=0:
            sprite_sheet='Death'
            return False
        elif self.animation_type==2:
            sprite_sheet='Attack2'
        elif self.x_vel!=0:
            sprite_sheet='Run'
        elif self.y_vel<-0.5:
            sprite_sheet='Jump'
        elif self.y_vel>4:
            sprite_sheet='Fall'
        else:
            sprite_sheet = 'Idle'
        sprite_sheet_name = sprite_sheet+'_'+self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count//self.animation_delay)%len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count+=1
        if self.animation_type==2 and sprite_index==len(sprites)-1:
            self.animation_type=0 
        return True

    def handel_vertical_collision(self,obj):
        if (self.rect.bottom < obj.rect.bottom and self.rect.bottom > obj.rect.top):
            
            if self.y_vel<0.1:
                self.y_vel=0
            else:
                self.y_vel=-1*self.y_vel/7.5


            if self.rect.x>obj.rect.left-obj.rect.width/2:
                if self.rect.bottom<=obj.rect.top:
                    self.rect.left=obj.rect.left-self.rect.width/2
                self.rect.bottom=obj.rect.y

            self.landed()
                
        elif self.y_vel < 0:
            self.y_vel = 0
            self.rect.top = obj.rect.bottom
            self.hit_head()
        else:
            self.rect.bottom=obj.rect.top


        '''
        elif self.y_vel > 2:
            if self.y_vel<0.1:
                self.y_vel=0
            else:
                self.y_vel=-1*self.y_vel/7.5
                self.rect.bottom=obj.rect.top
            self.landed()
            print('hi')
        '''

    def handel_movement(self,objects,enemys):
        self.x_vel=0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and self.animation_type!=2:
            self.x_vel=PSpeedX
            self.direction='right'
        elif keys[pygame.K_a] and self.animation_type!=2:
            self.x_vel=-1*PSpeedX
            self.direction='left'
        elif keys[pygame.K_e]:
            self.animation_type=2
            self.x_vel=0
            for enemy in enemys:
                if math.sqrt((self.rect.x-enemy.rect.x)**2+(self.rect.y-enemy.rect.y)**2)<150:
                    enemy.HP-=10/FPS
                    if enemy.HP<=0:
                        self.score+=1
        if (self.rect.x>WIDTH or self.rect.x<0):
            if len(enemys)==0:
                self.rect.x=WIDTH/2
                self.rect.y=0
                generate_tarain()
            else:
                if self.rect.x<=0:
                    self.rect.left=0
                else:
                    self.rect.right=WIDTH
        if self.rect.y>=HEIGHT+100:
            self.HP=0
        player_rect=self.rect.copy()
        player_rect.x+=self.x_vel
        for obj in objects:
            if obj.type=="SKP" and math.sqrt((self.rect.x-obj.rect.x)**2+(self.rect.y-obj.rect.y)**2)<125:
                if pygame.key.get_pressed()[pygame.K_c]:
                    obj.type="GB"
                    obj.update_block()
                    if self.HP<30:
                        self.HP+=5
                    self.score+=2
            if pygame.sprite.collide_mask(self, obj):
                self.handel_vertical_collision(obj)
            if pygame.key.get_pressed()[pygame.K_f] and math.sqrt((self.rect.x-obj.rect.x)**2+(self.rect.y-obj.rect.y)**2)<100:
                objects.remove(obj)
        return objects



class Enemy(Entity):
    def __init__(self, x, y, width, height) -> None:
        super().__init__(x, y, width, height,'skeletion')
        self.ESpeedX=random.randint(0,PSpeedX-1)
        self.ESpeedY=2
        self.HP=10

    def update_animation(self):
        '''
        if self.animation_type==2:
            sprite_sheet='Attack2'
        elif self.x_vel!=0:
            sprite_sheet='Run'
        elif self.y_vel<-0.5:
            sprite_sheet='Jump'
        elif self.y_vel>4:
            sprite_sheet='Fall'
        else:
        '''
        if self.HP<=0:
            sprite_sheet="Idle"
            enemys.remove(self)
            return
        elif math.sqrt((player.rect.x-self.rect.x)**2+(player.rect.y-self.rect.y)**2)<(player.rect.width/2+self.rect.width/2+30):
            sprite_sheet='Atack'
            player.HP-=1/FPS
        else:
            sprite_sheet = 'Idle'
        sprite_sheet_name = sprite_sheet+'_'+self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count//self.animation_delay)%len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count+=1
        if self.animation_type==2 and sprite_index==len(sprites)-1:
            self.animation_type=0 

    def handel_vertical_collision(self,obj):
        if (self.rect.bottom < obj.rect.bottom and self.rect.bottom > obj.rect.top):
            if self.y_vel<0.1:
                self.y_vel=0
            else:
                self.y_vel=-1*self.y_vel/7.5
            if self.rect.x>obj.rect.left-obj.rect.width/2:
                if self.rect.bottom<=obj.rect.top:
                    self.rect.left=obj.rect.left-self.rect.width/2
                self.rect.bottom=obj.rect.y
            self.landed()
                
        elif self.y_vel < 0:
            self.y_vel = 0
            self.rect.top = obj.rect.bottom
            self.hit_head()
        else:
            self.rect.bottom=obj.rect.top

    def handel_movement(self,objects):
        self.x_vel=0
        if self.rect.y>HEIGHT:
            self.HP=0
        if player.rect.x>self.rect.x:
            self.direction='right'
            self.x_vel=self.ESpeedX
        elif player.rect.x<self.rect.x:
            self.x_vel=-self.ESpeedX
            self.direction='left'
        else:
            self.x_vel=0


        player_rect=self.rect.copy()
        player_rect.x+=self.x_vel
        colided_objects=[]
        for obj in objects:
            if pygame.sprite.collide_mask(self, obj):
                self.handel_vertical_collision(obj)
                colided_objects.append(obj)
        return colided_objects


player = Player(0,0,66,95)


tarainMap=[]
blocks=[]
def generate_tarain(block_size=49,window=screen,width=WIDTH//49+1):
    global tarainMap
    global blocks
    global enemys
    tarainMap.append((0,HEIGHT-block_size*2))
    tarainMap=[tarainMap[-1]]
    for i in range(1,width):
        if tarainMap[-1][1]<HEIGHT-block_size:
            #print(tarainMap[-1][1])
            tarainMap.append((i*block_size,tarainMap[-1][1]+random.randint(-block_size+2,block_size-2)))
        else:
            tarainMap.append((i*block_size,tarainMap[-1][1]-random.randint(0,block_size-2)))
    for enemy in enemys:
        enemys.remove(enemy)
    for block in blocks:
        blocks.remove(block)
    blocks=[]
    enemys=[]
    for i in tarainMap:
        if random.random()>0.3:
            blocks.append(Block(i[0],i[1],block_size,'GB'))
        else:
            blocks.append(Block(i[0],i[1],block_size,'SKP'))
        for j in range(1,int((HEIGHT-blocks[-1].rect.bottom)/block_size)+2):
            blocks.append(Block(i[0],i[1]+block_size*j,block_size,'GB'))




def main(screen):
    running=True
    clock = pygame.time.Clock()
    block_size=49
    generate_tarain(block_size)
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                    player.animation_type=0

        
        displayBackground()
        player.loop(FPS)
        for enemy in enemys:
            enemy.loop(FPS)
        running=player.drow(screen)
        for enemy in enemys:
            enemy.drow(screen)
        
        b=player.handel_movement(blocks,enemys)
        
        for enemy in enemys:
            enemy.handel_movement(blocks)
        for block in blocks:
            block.drow(screen)

        font = pygame.font.Font(None, 36)
        text = font.render("Score: "+str(player.score), True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.center = (50,50)
        screen.blit(text, text_rect)

        text = font.render("HP: "+str(int(player.HP)), True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.center = (50,100)
        screen.blit(text, text_rect)

        pygame.display.flip()




if __name__ == '__main__':
    main(screen)


#prieeprint