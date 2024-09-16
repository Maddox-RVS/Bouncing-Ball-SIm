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

AIR_DENSITY: float = 1.2
DYNAMIC_VISCOSITY: float = 1.8 * math.pow(10, -5)
METERS_TO_PIXELS: float = 1.0 / 1.0

class Vector2:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def getResultant(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

class Ball:
    def __init__(self, 
                 radius: int, 
                 x: int, y: int, 
                 velo: Vector2, 
                 userForceStrength: int,
                 color: str) -> None:
        self.radius: int = radius
        self.x: int = x
        self.y: int = y
        self.velo: Vector2 = velo
        self.gravitationalAcceleration: int = (9.81) * METERS_TO_PIXELS
        self.dragCoefficient: float = 0.5
        self.userForceStrength: int = userForceStrength
        self.color: str = color
        self.userInput: bool = False
        self.isOnFloor: bool = False

    def __draw(self):
        t.teleport(self.x, self.y)
        t.fillcolor(self.color)
        t.begin_fill()
        t.pencolor(self.color)
        t.dot(self.radius * 2.0)
        t.end_fill()
        t.up()

    def __checkForFloor(self):
        if self.y <= -1.0 * (CANVAS_HEIGHT / 2) + self.radius:
            self.isOnFloor = True
        else: self.isOnFloor = False

    def __putIntoBoundingScope(self):
        if self.x < -1.0 * (CANVAS_WIDTH / 2) + self.radius:
            self.x = -1.0 * (CANVAS_WIDTH / 2) + self.radius
        if self.x > (CANVAS_WIDTH / 2) - self.radius:
            self.x = (CANVAS_WIDTH / 2) - self.radius
        if self.y < -1.0 * (CANVAS_HEIGHT / 2) + self.radius: #floor
            self.y = -1.0 * (CANVAS_HEIGHT / 2) + self.radius
        if self.y > (CANVAS_HEIGHT / 2) - self.radius:
            self.y = (CANVAS_HEIGHT / 2) - self.radius

    def __handleUserInput(self):
        if keyboard.is_pressed('w') or keyboard.is_pressed('up'):
            self.velo.y += self.userForceStrength
            self.userInput = True
        if keyboard.is_pressed('s') or keyboard.is_pressed('down'):
            self.velo.y -= self.userForceStrength
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
    
    def getLeft(self) -> Vector2:
        return Vector2(self.x - self.radius, self.y)
    def getRight(self) -> Vector2:
        return Vector2(self.x + self.radius, self.y)
    def getTop(self) -> Vector2:
        return Vector2(self.x, self.y + self.radius)
    def getBottom(self) -> Vector2:
        return Vector2(self.x, self.y - self.radius)
    
    def collideBall(self, otherX: float, otherY: float, othrRadius: int) -> bool:
        xDiff: float = self.x - otherX
        yDiff: float = self.y - otherY
        distSq: float = xDiff**2 + yDiff**2
        totalRadius: float = self.radius + othrRadius
        radiusSq: float = totalRadius**2
        return distSq <= radiusSq
    
    def collisionResolutionVector(self, otherBall) -> Vector2:
        smol: float = 0.00001
        xDiff: int = abs(self.x - otherBall.x)
        yDiff: int = abs(self.y - otherBall.y)
        dist: Vector2 = Vector2(xDiff, yDiff)
        overlapResultant: float = (self.radius + otherBall.radius) - dist.getResultant()
        theta: float = math.asin(abs(dist.y + smol) / (dist.getResultant() + smol))
        if otherBall.x < self.x: dist.x *= -1.0
        if otherBall.y < self.y: dist.y *= -1.0
        solutionVector: Vector2 = Vector2(
            -1.0 * math.copysign(overlapResultant * math.cos(theta), dist.x),
            -1.0 * math.copysign(overlapResultant * math.sin(theta), dist.y)
        )
        return solutionVector
    
    def __updatePosition(self):
        self.x += self.velo.x
        self.y += self.velo.y

    def __updateVelocity(self):
        fNet: Vector2 = self.__getNetForce()
        self.velo.x += (fNet.x / self.getMass()) * GAMELOOP_PERIOD
        self.velo.y += (fNet.y / self.getMass()) * GAMELOOP_PERIOD
    
    def getMass(self):
        return (math.pi * self.radius**2)
    
    def __getDragForce(self) -> Vector2:
        return Vector2(
            0.5 * AIR_DENSITY * self.dragCoefficient * self.getMass() * (self.velo.x**2),
            0.5 * AIR_DENSITY * self.dragCoefficient * self.getMass() * (self.velo.y**2))
    
    def __getGravitationalForce(self) -> float:
        return self.getMass() * self.gravitationalAcceleration
    
    def __getPotentialEnergy(self) -> float:
        return self.getMass() * self.gravitationalAcceleration * (self.y - (-1.0 * (CANVAS_HEIGHT / 2)))
    def __getKeneticEnergy(self) -> float:
        return 0.5 * self.getMass() * self.velo.y**2

    def __getNetForce(self) -> Vector2:
        gravitationalForce: float = self.__getGravitationalForce()
        dragForce: Vector2 = self.__getDragForce()
        dragForce.x = -1.0 * math.copysign(dragForce.x, self.velo.x)
        dragForce.y = -1.0 * math.copysign(dragForce.y, self.velo.y)
        normalForce: float = 0
        if self.isOnFloor: normalForce = gravitationalForce
        netForce: Vector2 = Vector2(
            dragForce.x,
            dragForce.y - gravitationalForce + normalForce)
        return netForce
    
    def __getImpulseVelocity(self) -> Vector2:
        timeSecs: float = 1.0
        fNet: Vector2 = self.__getNetForce()
        p: Vector2 = Vector2(
            (self.getMass() * self.velo.x) * timeSecs,
            fNet.y * timeSecs)
        veloAfterP: Vector2 = Vector2(
            -1.0 * math.copysign(p.x / self.getMass(), self.velo.x),
            -1.0 * math.copysign(p.y / self.getMass(), self.velo.y))
        return veloAfterP

    # energyLoss: float = ((self.__getKeneticEnergy() - self.__getPotentialEnergy()) / self.__getKeneticEnergy()) * 100.0
    def __updateWallCollisionVelocity(self):
        self.__putIntoBoundingScope()
        if self.x <= (-1.0 * (CANVAS_WIDTH / 2)) + self.radius or self.x >= (CANVAS_WIDTH / 2) - self.radius:
            self.velo.x = self.__getImpulseVelocity().x
        if self.y <= (-1.0 * (CANVAS_HEIGHT / 2)) + self.radius or self.y >= (CANVAS_HEIGHT / 2) - self.radius:
            self.velo.y = self.__getImpulseVelocity().y

    def handleBallCollision(self, otherBall) -> Vector2:
        pass

    def update(self):
        t.down()
        self.userInput = False
        self.__checkForFloor()
        self.__handleUserInput()
        self.__updateVelocity()
        self.__updateWallCollisionVelocity()
        self.__updatePosition()
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
                    radius=random.randint(10, 40), 
                    x=random.randint(-50, 50), y=0, 
                    velo=Vector2(random.randint(-10, 10), random.randint(30, 31)),
                    userForceStrength=random.randint(1, 3),
                    color=random.choice(colors)))
    return balls

def main():
    init()
    gameLoop(generateBalls(1))

if __name__ == '__main__':
    main()