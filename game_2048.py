# _*_ coding:UTF-8 _*_
import numpy,sys,random,pygame
from pygame.locals import*

Size = 4                                          #4*4行列
Block_WH = 110                                    #每个块的长度宽度
BLock_Space = 10                                  #两个块之间的间隙
Block_Size = Block_WH*Size+(Size+1)*BLock_Space
Matrix = numpy.zeros([Size,Size])                 #初始化矩阵4*4的0矩阵
Screen_Size = (Block_Size,Block_Size+110)
Title_Rect = pygame.Rect(0,0,Block_Size,110)      #设置上部分标题矩形的大小
Cube_Rect = pygame.Rect(0,110,Block_Size,Block_Size)    #设置下部分的大小
Result_Rect = pygame.Rect(0,0,Block_Size,Block_Size+110)    #结果页面大小
Restart_Rect = pygame.Rect(153,430,175,40)
Exit_Rect = pygame.Rect(153,480,175,40)
Score = 0               #得分

Block_Color = {                                   #存放块的颜色
        0:(206,192,183),
        2:(249,245,241),
        4:(255,255,128),
        8:(255,255,0),
        16:(255,220,128),
        32:(255,220,0),
        64:(255,190,0),
        128:(255,160,0),
        256:(255,130,0),
        512:(255,100,0),
        1024:(255,70,0),
        2048:(255,40,0),
        4096:(255,10,0),
}

#基础类，包含matrix，score，zerolist 3个属性。提供一个操控矩阵的方法，toSequence(matrix)
class UpdateNew:
    #初始化函数，类被实例化后自动执行此函数，但类调用不执行此函数。
    def __init__(self,matrix):
        super(UpdateNew, self).__init__()
        self.matrix = matrix
        self.score  = 0
        self.zerolist = []          #保存的为一个个元组，用于存放矩阵中0元素的位置坐标

    #私有函数，不对外提供，仅供removeZero()函数使用
    def __combineList(self,rowlist):          #合并相同的数字
        start_num = 0
        end_num = Size-rowlist.count(0)-1
        while start_num < end_num:
            if rowlist[start_num] == rowlist[start_num+1]:
                rowlist[start_num] *= 2
                self.score += int(rowlist[start_num])   #每次返回累加的分数
                rowlist[start_num+1:] = rowlist[start_num+2:]
                rowlist.append(0)
            start_num += 1
        return rowlist

    #私有方法，不对外提供，仅供toSequence()函数使用
    def __removeZero(self,rowlist):   #删除列表前面和中间的0，返回合并后的列表
        while True:
            mid = rowlist[:]                      #拷贝一份list
            try:
                rowlist.remove(0)           #remove，删除列表中第一个匹配项
                rowlist.append(0)           #append，在列表末尾添加元素
            except:         #如果没有0，抛出异常
                pass
            if rowlist == mid:
                break;
        return self.__combineList(rowlist)

    def toSequence(self,matrix):
    #去除矩阵中每一行前面与中间的0元素，获得矩阵中0元素位置，合并元素后返回添加一个2或4元素后的矩阵
        sound = pygame.mixer.Sound("sound.wav")     #导入音效文件
        lastmatrix = matrix.copy()
        m,n = matrix.shape      #获得矩阵的行数，列数
        for i in range(m):      #对于m行
            newList = self.__removeZero(list(matrix[i]))  #去除前面和中间的0后合并
            matrix[i] = newList
            for k in range(Size-1,Size-newList.count(0)-1,-1):#添加所有0元素的行列号
                self.zerolist.append((i,k))
        if matrix.min() == 0 and (matrix!=lastmatrix).any():
            #矩阵中有最小值0且移动后的矩阵不同，才可以添加0位置处添加随机数
            sound.play()        #每次有效移动播放一次音效
            GameInit.updateData(matrix,self.zerolist)
        return matrix
                          

#左移，继承基础类的属性和方法，提供一种处理数据的方法，handleData()
class LeftAction(UpdateNew):
    """docstring for LeftAction"""
    def __init__(self,matrix):
        super(LeftAction, self).__init__(matrix)
        #继承自父类的属性进行初始化。而且是用父类的初始化方法来初始化继承的属性。

    def handleData(self):
        matrix = self.matrix.copy()                     #获得一份矩阵的复制
        newmatrix = self.toSequence(matrix)
        return newmatrix,self.score
#右移
class RightAction(UpdateNew):
    """docstring for RightAction"""
    def __init__(self,matrix):
        super(RightAction, self).__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy()[:,::-1]         #翻转
        newmatrix = self.toSequence(matrix)
        return newmatrix[:,::-1],self.score
#上移
class UpAction(UpdateNew):
    """docstring for UpAction"""
    def __init__(self,matrix):
        super(UpAction, self).__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy().T               #转置
        newmatrix = self.toSequence(matrix)
        return newmatrix.T,self.score
#下移
class DownAction(UpdateNew):
    """docstring for DownAction"""
    def __init__(self,matrix):
        super(DownAction, self).__init__(matrix)

    def handleData(self):
        matrix = self.matrix.copy()[::-1].T         #翻转再转置
        newmatrix = self.toSequence(matrix)
        return newmatrix.T[::-1],self.score

#游戏初始化类
class GameInit:
    """docstring for GameInit"""
    def __init__(self):
        super(GameInit, self).__init__()

    #私有方法，仅供initData()函数使用
    def __getRandomLocal(zerolist = None):            #获得随机位置坐标
        if zerolist == None:
            a = random.randint(0,Size-1)
            b = random.randint(0,Size-1)
        else:
            a,b = random.sample(zerolist,1)[0]
        return a,b

    #私有方法，仅供initData()函数使用
    def __getNewNum():                             #随机返回2或者4
        n = random.random()
        if n > 0.8:
            n = 4
        else:
            n = 2
        return n

    #类方法方法，用类名调用函数，如：GameInit.initData()
    @classmethod
    #将合并后的数据在空白地方增加2或4
    def updateData(cls,matrix = None,zerolist = None):
        if matrix is None:
            matrix = Matrix.copy()
        a,b = cls.__getRandomLocal(zerolist)
        #zerolist空任意返回(x,y)位置，否则返回任意一个0元素位置
        n = cls.__getNewNum()
        matrix[a][b] = n
        return matrix                   #返回在空白位置加入2或4的矩阵

    @classmethod
    def drawSurface(cls,screen,matrix,score,types):
        #绘制界面
        #第一个参数是屏幕，第二个参数颜色，第三个参数rect大小，第四个默认参数
        pygame.draw.rect(screen,(250,248,239),Title_Rect)   #上半部分颜色
        pygame.draw.rect(screen,(146,132,119),Cube_Rect)    #下半部分颜色
        font1 = pygame.font.SysFont('stxingkai',32)
        font2 = pygame.font.SysFont('Chiller',48)
        #font.render第一个参数是文本内容，第二个参数是否抗锯齿，第三个参数字体颜色
        if types == -1:     #up,left,down,right字体颜色都为原始黄色
            screen.blit(font1.render('up',True,(0,0,0)),(95,20))
            screen.blit(font1.render('left  down  right',True,(0,0,0)),(30,50))
        elif types == 1:    #left为黑色
            screen.blit(font1.render('up',True,(0,0,0)),(95,20))
            screen.blit(font1.render('left  down  right',True,(0,0,0)),(30,50))
            screen.blit(font1.render('left',True,(51,136,255)),(30,50))
        elif types == 2:    #right为黑色
            screen.blit(font1.render('up',True,(0,0,0)),(95,20))
            screen.blit(font1.render('left  down  right',True,(0,0,0)),(30,50))
            screen.blit(font1.render('right',True,(51,136,255)),(145,50))
        elif types == 3:    #up为黑色
            screen.blit(font1.render('up',True,(51,136,255)),(95,20))
            screen.blit(font1.render('left  down  right',True,(0,0,0)),(30,50))
        elif types == 4:    #down为黑色
            screen.blit(font1.render('up',True,(0,0,0)),(95,20))
            screen.blit(font1.render('left  down  right',True,(0,0,0)),(30,50))
            screen.blit(font1.render('down',True,(51,136,255)),(79,50))
        screen.blit(font2.render('Score:',True,(0,0,0)),(260,25))
        screen.blit(font2.render('%s' % score,True,(0,0,0)),(360,25))
        a,b = matrix.shape      #读取行列值
        for i in range(a):
            for j in range(b):
                cls.__drawBlock(screen,i,j,Block_Color[matrix[i][j]],matrix[i][j])

    #私有方法，画方块,仅供drawSurface()函数使用
    def __drawBlock(screen,row,column,color,blocknum):
        font = pygame.font.SysFont('stxingkai',60)
        w = column*Block_WH+(column+1)*BLock_Space          #方块起始坐标
        h = row*Block_WH+(row+1)*BLock_Space+110
        pygame.draw.rect(screen,color,(w,h,110,110))
        if blocknum != 0:   #方块中有数字
            #数字居中
            fw,fh = font.size(str(int(blocknum)))       #获得数字的长度和宽度
            screen.blit(font.render(str(int(blocknum)),True,(0,0,0)),(w+(110-fw)/2,h+(110-fh)/2))

    @classmethod
    #游戏结束画面
    def drawResult(cls,screen,score,maxnum):
        #第一个参数是屏幕，第二个参数颜色，第三个参数rect大小，第四个默认参数
        pygame.draw.rect(screen,(250,248,239),Result_Rect)
        pygame.draw.rect(screen,(0,0,0),Restart_Rect)
        pygame.draw.rect(screen,(0,0,0),Exit_Rect)
        font1 = pygame.font.SysFont('stxingkai',80) #游戏结束字体
        font2 = pygame.font.SysFont('stxingkai',40) #得分字体
        #font.render第一个参数是文本内容，第二个参数是否抗锯齿，第三个参数字体颜色
        screen.blit(font1.render('游戏结束！',True,(255,127,0)),(70,70))
        screen.blit(font2.render('最大方块：%s' % maxnum,True,(255,127,0)),(120,240))
        screen.blit(font2.render('得分：%s' % score,True,(255,127,0)),(150,310))
        screen.blit(font2.render('重新开始',True,(255,127,0)),(160,430))
        screen.blit(font2.render('退出游戏',True,(255,127,0)),(160,480))
        x, y = pygame.mouse.get_pos()       #获得鼠标位置
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 153<=x<=328 and 430<=y<=470:         #重新开始
                    return 1
                elif 153<=x<=328 and 480<=y<=520:       #退出游戏
                    return 2
                else:
                    return 0

    @classmethod
    #游戏开始和介绍画面
    def drawWelcome(cls,screen):
        #第一个参数是屏幕，第二个参数颜色，第三个参数rect大小，第四个默认参数
        pygame.draw.rect(screen,(250,248,239),Result_Rect)
        pygame.draw.rect(screen,(0,0,0),Restart_Rect)
        pygame.draw.rect(screen,(0,0,0),Exit_Rect)
        font1 = pygame.font.SysFont('stxingkai',80) #游戏结束字体
        font2 = pygame.font.SysFont('stxingkai',40) #得分字体
        font3 = pygame.font.SysFont('stxingkai',25) #介绍字体
        #font.render第一个参数是文本内容，第二个参数是否抗锯齿，第三个参数字体颜色
        screen.blit(font1.render('2 0 4 8',True,(255,127,0)),(138,70))
        screen.blit(font3.render('键位介绍：使用上下左右方向键或',True,(0,0,0)),(45,230))
        screen.blit(font3.render('WASD键控制方块的移',True,(0,0,0)),(170,270))
        screen.blit(font3.render('动，R键可以撤回一步',True,(0,0,0)),(170,310))
        screen.blit(font2.render('开始游戏',True,(255,127,0)),(160,430))
        screen.blit(font2.render('退出游戏',True,(255,127,0)),(160,480))
        x, y = pygame.mouse.get_pos()       #获得鼠标位置
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 153<=x<=328 and 430<=y<=470:         #开始游戏
                    return 1
                if 153<=x<=328 and 480<=y<=520:       #退出游戏
                    return 2
                else:
                    return 0

    
    #静态方法，不能加self参数，可以直接用类名调用
    @staticmethod
    def keyDownPressed(keyvalue,matrix):
        if keyvalue == K_LEFT or keyvalue == K_a:
            return LeftAction(matrix),1
        elif keyvalue == K_RIGHT or keyvalue == K_d:
            return RightAction(matrix),2
        elif keyvalue == K_UP or keyvalue == K_w:   
            return UpAction(matrix),3
        elif keyvalue == K_DOWN or keyvalue == K_s:
            return DownAction(matrix),4
        elif keyvalue == K_r:
            return 1,-1
        else:       #按到其他键
            return -1,-1

    #类方法，必须加cls参数，可以直接用类名调用
    @classmethod
    def gameOver(cls,matrix):           #判断传入的矩阵，游戏是否结束
        testmatrix = matrix.copy()
        a,b = testmatrix.shape
        for i in range(a):
            for j in range(b-1):
                if testmatrix[i][j] == testmatrix[i][j+1]:
                    #如果有一行存在相邻两个数相同，则游戏没有结束
                    return False
        for i in range(b):
            for j in range(a-1):
                if testmatrix[j][i] == testmatrix[j+1][i]:
                    return False
        #print('游戏结束')
        return True

def main():
    pygame.init()               #初始化pygame库
    pygame.mixer.init()         #初始化声音模块
    screen = pygame.display.set_mode(Screen_Size,0,32)      #屏幕设置
    pygame.display.set_caption('2048小游戏')
    matrix = GameInit.updateData()        #更新矩阵的值
    oldmatrix = matrix
    currentscore = 0        #分数
    oldscore = currentscore
    GameInit.drawSurface(screen,matrix,currentscore,-1)
    pygame.display.update()     #必须有，每次画完要更新画面
    flag=0    #flag默认为0，为欢迎界面，flag为1时开始游戏
    while True:
        #开始和介绍界面
        flag = GameInit.drawWelcome(screen)    #flag为返回鼠标点击的选项
        pygame.display.update()  #更新画面
        if flag == 1:       #开始游戏，初始化界面
            GameInit.drawSurface(screen,matrix,currentscore,-1)
            pygame.display.update()     #必须有，每次画完要更新画面
        elif flag == 2:       #退出游戏
            pygame.quit()
            sys.exit(0)
        while flag==1:      #游戏主界面
            for event in pygame.event.get():
                if event.type == pygame.QUIT:       #退出游戏
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:      #按键按下
                    #创建各种动作类的对象，types代表按下的是哪个按键，从而让相应的字变黑色
                    actionObject,types = GameInit.keyDownPressed(event.key,matrix)
                    if actionObject != -1 and actionObject != 1:    #上下左右
                        oldmatrix = matrix  #保存上一个matrix，可以实现撤销功能
                        oldscore = currentscore
                        matrix,score = actionObject.handleData()    #处理数据，获得新矩阵与分数
                        currentscore += score
                        GameInit.drawSurface(screen,matrix,currentscore,types)        #重新绘制新矩阵
                        pygame.display.update()  #更新画面
                    if actionObject == 1:       #撤销一步
                        matrix = oldmatrix
                        currentscore = oldscore
                        GameInit.drawSurface(screen,matrix,currentscore,-1)
                        pygame.display.update()  #更新画面
                        #print(oldmatrix,oldscore)
                    if matrix.min() != 0:
                        while GameInit.gameOver(matrix) == True:   #判断游戏是否结束
                            f = GameInit.drawResult(screen,currentscore,int(matrix.max()))    #f为返回鼠标点击的选项
                            pygame.display.update()  #更新画面
                            if f == 1:      #重新开始游戏
                                screen = pygame.display.set_mode(Screen_Size,0,32)      #屏幕设置
                                matrix = GameInit.updateData()        #更新矩阵的值
                                currentscore = 0        #分数
                                GameInit.drawSurface(screen,matrix,currentscore,-1)
                                pygame.display.update()     #必须有，每次画完要更新画面
                                #f = 0
                                break       #跳出此循环，重新开始游戏
                            elif f == 2:    #结束，退出游戏
                                pygame.quit()
                                sys.exit(0)
                elif event.type == pygame.KEYUP:        #按键松开
                    if actionObject == 1:       #撤销
                        matrix = oldmatrix
                        currentscore = oldscore
                        GameInit.drawSurface(screen,matrix,currentscore,-1)
                        pygame.display.update()  #更新画面
                    GameInit.drawSurface(screen,matrix,currentscore,-1) #字体颜色恢复原来的黄色
                    pygame.display.update()  #更新画面
if __name__ == '__main__':
    main()
