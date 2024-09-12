import turtle as t
import keyboard
import random
import time
import math

GAMELOOP_PERIOD: float = 0.02
CANVAS_TITLE: str = 'Bounce Sim'
CANVAS_WIDTH: int = 500
CANVAS_HEIGHT: int = 500
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
        self.isCollidingWithObject: bool = False

    def __updateGravity(self):
        if self.y >= -1.0 * (CANVAS_HEIGHT / 2) + self.radius and not self.userInput and not self.isCollidingWithObject:
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
    
    def __calculateSystemVelocity(self, otherVelocity: Vector, otherRadius: int, otherMass: float):
        selfMass: float = self.getMass()
        selfVelo: Vector = Vector(self.velo.x * 60.0, self.velo.y * 60.0)
        otherVelo: Vector = Vector(otherVelocity.x * 60.0, otherVelocity.y * 60.0)
        newXVelo: float = ((selfMass * selfVelo.x)+(otherMass * otherVelo.x))/(selfMass + otherMass)
        newYVelo: float = ((selfMass * selfVelo.y)+(otherMass * otherVelo.y))/(selfMass + otherMass)
        return Vector(newXVelo / 60.0, newYVelo / 60.0)

    def handleBallCollision(self, otherX: int, otherY: int, otherRadius: int, otherVelo: Vector, otherMass: float) -> Vector:
        smol: float = 0.00001
        xDiff: int = abs(self.x - otherX)
        yDiff: int = abs(self.y - otherY)
        dist: Vector = Vector(xDiff, yDiff)
        if dist.getResultant() > (self.radius + otherRadius):
            self.isCollidingWithObject = False
            return Vector(0, 0)
        else: self.isCollidingWithObject = True
        overlapResultant: float = (self.radius + otherRadius) - dist.getResultant()
        theta: float = math.asin(abs(dist.y + smol) / (dist.getResultant() + smol))
        if otherX < self.x: dist.x *= -1.0
        if otherY < self.y: dist.y *= -1.0
        solutionVector: Vector = Vector(
            math.copysign(overlapResultant * math.cos(theta), dist.x),
            math.copysign(overlapResultant * math.sin(theta), dist.y)
        )
        self.velo = self.__calculateSystemVelocity(otherVelo, otherRadius, otherMass)
        return solutionVector

    def update(self):
        t.down()
        self.userInput = False
        self.__updatePosition()
        self.__handleWallCollision()
        self.__applyFrictionForce()
        self.__handleUserInput()
        self.__updateGravity()
        self.__draw()

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
        for ball in balls:
            for b in balls:
                if b != ball:
                    solutionVector: Vector = ball.handleBallCollision(b.x, b.y, b.radius, b.velo, b.getMass())
                    b.x += solutionVector.x
                    b.y += solutionVector.y
            ball.update()
        t.update()
        time.sleep(GAMELOOP_PERIOD)
        t.clear()

def generateBalls(ballNum: int) -> list[Ball]:
    colors = ('red', 'blue', 'green', 'yellow', 'pink', 'cyan', 'orange')
    balls = []
    for i in range(ballNum):
        balls.append(Ball(
                    radius=random.randint(3, 40), 
                    x=random.randint(-150, 50), y=0, 
                    velo=Vector(random.randint(-10, 10), random.randint(-10, 10)), 
                    frictionForcePercent=0.992,
                    userForceStrength=random.randint(1, 3),
                    color=random.choice(colors)))
    return balls

def main():
    init()
    gameLoop(generateBalls(5))

if __name__ == '__main__':
    main()