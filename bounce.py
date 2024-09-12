import turtle as t
import keyboard
import random
import time
import math

GAMELOOP_PERIOD: float = 0.02
CANVAS_TITLE: str = 'Bounce Sim'
CANVAS_WIDTH: int = 1000
CANVAS_HEIGHT: int = 800
PENSIZE: int = 3

class Vector:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def getResultant(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

class Ball:
    def __init__(self, 
                 radius: int, 
                 x: int, y: int, 
                 velo: Vector, 
                 frictionForcePercent: int, 
                 userForceStrength: int,
                 color: str) -> None:
        self.radius: int = radius
        self.x: int = x
        self.y: int = y
        self.velo: Vector = velo
        self.gravitationalPull: int = 2
        self.frictionForcePercent: int = frictionForcePercent
        self.userForceStrength: int = userForceStrength
        self.downStrengthMultipler: float = 3.0
        self.massMultiplier: float = 0.1
        self.color: str = color
        self.userInput: bool = False
        self.isOnFloor: bool = False

    def __updateGravity(self):
        if self.y >= -1.0 * (CANVAS_HEIGHT / 2) + self.radius and not self.userInput:
            self.velo.y -= self.gravitationalPull

    def __updatePosition(self):
        self.x += self.velo.x
        self.y += self.velo.y

    def __draw(self):
        t.teleport(self.x, self.y - self.radius)
        t.fillcolor(self.color)
        t.begin_fill()
        t.pencolor(self.color)
        t.circle(self.radius)
        t.end_fill()
        t.up()

    def __handleWallCollision(self):
        if self.x <= -1.0 * (CANVAS_WIDTH / 2) + self.radius:
            self.velo.x *= -1.0
            self.x = -1.0 * (CANVAS_WIDTH / 2) + self.radius
        if self.x >= (CANVAS_WIDTH / 2) - self.radius:
            self.velo.x *= -1.0
            self.x = (CANVAS_WIDTH / 2) - self.radius
        if self.y <= -1.0 * (CANVAS_HEIGHT / 2) + self.radius: #floor
            self.velo.y *= -1.0
            self.y = -1.0 * (CANVAS_HEIGHT / 2) + self.radius
            self.isOnFloor = True
        else: self.isOnFloor = False
        if self.y >= (CANVAS_HEIGHT / 2) - self.radius:
            self.velo.y *= -1.0
            self.y = (CANVAS_HEIGHT / 2) - self.radius

    def __applyFrictionForce(self):
        self.velo.x *= self.frictionForcePercent
        self.velo.y *= self.frictionForcePercent

    def __handleUserInput(self):
        if keyboard.is_pressed('w') or keyboard.is_pressed('up'):
            self.velo.y += self.userForceStrength
            self.userInput = True
        if keyboard.is_pressed('s') or keyboard.is_pressed('down'):
            self.velo.y -= self.userForceStrength * self.downStrengthMultipler
        if keyboard.is_pressed('d') or keyboard.is_pressed('right'):
            self.velo.x += self.userForceStrength
            self.userInput = True
        if keyboard.is_pressed('a') or keyboard.is_pressed('left'):
            self.velo.x -= self.userForceStrength
            self.userInput = True
        if keyboard.is_pressed('space'):
            self.velo.x = 0
            self.velo.y = 0
            self.userInput = True

    def getMass(self):
        return (math.pi * self.radius**2) * self.massMultiplier
    
    def getLeft(self) -> Vector:
        return Vector(self.x - self.radius, self.y)
    def getRight(self) -> Vector:
        return Vector(self.x + self.radius, self.y)
    def getTop(self) -> Vector:
        return Vector(self.x, self.y + self.radius)
    def getBottom(self) -> Vector:
        return Vector(self.x, self.y - self.radius)
    
    def collideBall(self, otherX: float, otherY: float, othrRadius: int) -> bool:
        xDiff: float = self.x - otherX
        yDiff: float = self.y - otherY
        distSq: float = xDiff**2 + yDiff**2
        totalRadius: float = self.radius + othrRadius
        radiusSq: float = totalRadius**2
        return distSq <= radiusSq
    
    def __calculateSystemVelocity(self, otherBall) -> list[Vector]:
        smol: float = 0.00001
        selfMass: float = self.getMass()
        otherMass: float = otherBall.getMass()
        dist: float = math.sqrt((self.x - otherBall.x)**2 + (self.y - otherBall.y)**2) + smol
        normX: float = (otherBall.x - self.x) / dist
        normY: float = (otherBall.y - self.y) / dist 
        p: float = 2.0 * (self.velo.x * normX + self.velo.y * normY - otherBall.velo.x * normX - otherBall.velo.y * normY) / (selfMass + otherMass) 
        vx1 = self.velo.x - p * selfMass * normX 
        vy1 = self.velo.y - p * selfMass * normY
        vx2 = otherBall.velo.x + p * otherMass * normX 
        vy2 = otherBall.velo.y + p * otherMass * normY
        return [Vector(vx1, vy1), Vector(vx2, vy2)]
    
    def collisionResolutionVector(self, otherBall) -> Vector:
        smol: float = 0.00001
        xDiff: int = abs(self.x - otherBall.x)
        yDiff: int = abs(self.y - otherBall.y)
        dist: Vector = Vector(xDiff, yDiff)
        overlapResultant: float = (self.radius + otherBall.radius) - dist.getResultant()
        theta: float = math.asin(abs(dist.y + smol) / (dist.getResultant() + smol))
        if otherBall.x < self.x: dist.x *= -1.0
        if otherBall.y < self.y: dist.y *= -1.0
        solutionVector: Vector = Vector(
            -1.0 * math.copysign(overlapResultant * math.cos(theta), dist.x),
            -1.0 * math.copysign(overlapResultant * math.sin(theta), dist.y)
        )
        return solutionVector

    def handleBallCollision(self, otherBall) -> Vector:
        resolutionVector: Vector = self.collisionResolutionVector(otherBall)
        self.x += resolutionVector.x
        self.y += resolutionVector.y
        momentum: list[Vector] = self.__calculateSystemVelocity(otherBall)
        self.velo.x = momentum[0].x
        self.velo.y = momentum[0].y
        otherBall.velo.x = momentum[1].x
        otherBall.velo.y = momentum[1].y

    def update(self):
        t.down()
        self.userInput = False
        self.__updatePosition()
        self.__handleWallCollision()
        self.__applyFrictionForce()
        self.__handleUserInput()
        self.__updateGravity()
        self.__draw()

def partition(arr: list[Ball], low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j].getLeft().x < pivot.getLeft().x:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
def quickSort(arr: list, low: int, high: int):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)

def init():
    t.title(CANVAS_TITLE)
    t.pensize(PENSIZE)
    t.up()
    t.setup(CANVAS_WIDTH, CANVAS_HEIGHT)
    t.tracer(False)
    t.hideturtle()
    t.bgcolor('black')

def gameLoop(balls: list[Ball]):
    while True:
        quickSort(balls, 0, len(balls) - 1)
        for i in range(len(balls)):
            balls[i].update()
            for j in range(i + 1, len(balls)):
                if balls[j].getLeft().x > balls[i].getRight().x:
                    break
                if balls[i].collideBall(balls[j].x, balls[j].y, balls[j].radius):
                    balls[i].handleBallCollision(balls[j])
        t.update()
        time.sleep(GAMELOOP_PERIOD)
        t.clear()

def generateBalls(ballNum: int) -> list[Ball]:
    colors = ('red', 'blue', 'green', 'yellow', 'pink', 'cyan', 'orange')
    balls = []
    for i in range(ballNum):
        balls.append(Ball(
                    radius=random.randint(3, 40), 
                    x=random.randint(-50, 50), y=0, 
                    velo=Vector(random.randint(-10, 10), random.randint(-10, 10)), 
                    frictionForcePercent=0.992,
                    userForceStrength=random.randint(1, 3),
                    color=random.choice(colors)))
    return balls

def main():
    init()
    gameLoop(generateBalls(10))

if __name__ == '__main__':
    main()