from enum import Enum
from random import randint
import math
from screeninfo import get_monitors
import pygame as pg
import colors

monitor = get_monitors()[0]

pg.init()

pg.display.set_caption("test")

windowSize = [1000, 700]
windowPosition = [
    (monitor.width - windowSize[0]) / 2,
    (monitor.height - windowSize[1]) / 2,
]

screen = pg.display.set_mode(windowSize)


def distance(point1, point2) -> float:
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


class ObjectTypeEnum(Enum):
    CIRCLE = 1
    SQUARE = 2


ObjectType = Enum("ObjectTypeEnum", ["CIRCLE", "SQUARE"])

objectFuncs = []


def normalizeAngle(angle):
    if angle > math.pi * 2:
        return angle - math.pi * 2
    elif angle < 0:
        return angle + math.pi * 2

    return angle


def findQuarter(point1, point2):
    if point2[1] < point1[1]:
        return 1 if point2[0] > point1[0] else 2
    else:
        return 4 if point2[0] > point1[0] else 3


def square(position, size, color):
    halfSize = size / 2
    left = position[0] - halfSize
    right = position[0] + halfSize
    top = position[1] - halfSize
    bottom = position[1] + halfSize

    def func(point, tg):
        resultPoint = []

        if point[0] < left:
            y = (left - point[0]) * tg + point[1]

            if top <= y <= bottom:
                resultPoint = [left, y]
        elif point[0] > right:
            y = (right - point[0]) * tg + point[1]

            if top <= y <= bottom:
                resultPoint = [right, y]
        if point[1] < top:
            x = (top - point[1]) / tg + point[0]

            if left <= x <= right:
                resultPoint = [x, top]
        elif point[1] > bottom:
            x = (bottom - point[1]) / tg + point[0]

            if left <= x <= right:
                resultPoint = [x, bottom]

        if len(resultPoint) == 0:
            return False

        return [resultPoint, color]

    objectFuncs.append(func)


def ray(point, angle, maxDistance):
    tg = math.tan(angle) + 0.001

    p = [
        point[0] + math.cos(angle) * maxDistance,
        point[1] + math.sin(angle) * maxDistance,
    ]

    quarter = findQuarter(point, p)

    intersection = []
    minDistance = -1
    for func in objectFuncs:
        result = func(point, tg)

        if result and findQuarter(point, result[0]) == quarter:
            dist = distance(point, result[0])

            if (minDistance == -1 or dist < minDistance) and dist <= maxDistance:
                intersection = result
                minDistance = dist

    if minDistance != -1:
        return [minDistance, intersection[1]]
    else:
        return False


font = pg.font.Font("freesansbold.ttf", 12)

text = font.render("0", True, colors.green, colors.blue)

textRect = text.get_rect()

textRect.center = (windowSize[0] // 2, windowSize[1] // 2)

clock = pg.time.Clock()
deltaTime = 0.01

pressedKeys = []


def getKey(key):
    return key in pressedKeys


for i in range(50):
    square(
        [randint(-100, 100), randint(-100, 100)],
        randint(3, 9),
        (randint(0, 255), randint(0, 255), randint(0, 255)),
    )


# square([400, 250], 50)

cameraPosition = [0, 0]
cameraRotation = 0

cameraSpeed = 50
cameraRotationSpeed = 1.5


def Update():
    global cameraPosition
    global cameraRotation

    deltaTime = 1 / (clock.get_fps() + 1)

    cameraRotation += (
        (getKey(pg.K_RIGHT) - getKey(pg.K_LEFT)) * cameraRotationSpeed * deltaTime
    )

    cameraRotation = normalizeAngle(cameraRotation)
    right = [math.sin(cameraRotation), math.cos(cameraRotation)]
    forward = [
        math.sin(cameraRotation + math.pi / 2),
        math.cos(cameraRotation + math.pi / 2),
    ]

    deltaX = (getKey(pg.K_d) - getKey(pg.K_a)) * cameraSpeed * deltaTime
    deltaY = (getKey(pg.K_w) - getKey(pg.K_s)) * cameraSpeed * deltaTime

    if deltaX != 0 and deltaY != 0:
        deltaX *= 0.707
        deltaY *= 0.707

    cameraPosition = [
        cameraPosition[0] + forward[0] * deltaY - right[0] * deltaX,
        cameraPosition[1] - forward[1] * deltaY + right[1] * deltaX,
    ]


floorRect = pg.Rect(0, windowSize[1] * 0.6, windowSize[0], windowSize[1] * 0.4)

fov = math.pi / 3
rayCount = 200
rayWidth = windowSize[0] / rayCount
drawDistance = 500


def DrawFrame():
    screen.fill(colors.sky)

    pg.draw.rect(screen, colors.gray, floorRect)

    angle = cameraRotation - fov / 2
    step = fov / (rayCount - 1)

    for i in range(rayCount):
        intersection = ray(cameraPosition, normalizeAngle(angle), drawDistance)

        if intersection:
            height = 20000 / intersection[0]

            d = 1 - intersection[0] / drawDistance
            d = d**3

            intersection[1] = [
                intersection[1][0] * d,
                intersection[1][1] * d,
                intersection[1][2] * d,
            ]

            pg.draw.rect(
                screen,
                intersection[1],
                pg.Rect(
                    i * rayWidth, windowSize[1] * 0.6 - height / 2, rayWidth, height
                ),
            )
        angle += step

    fpsText = font.render(f"{clock.get_fps():.0f}", True, colors.black)

    fpsTextRect = fpsText.get_rect()

    screen.blit(fpsText, fpsTextRect)

    pg.display.flip()


running = True
while running:
    for e in pg.event.get():
        if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
            running = False
        if e.type == pg.KEYDOWN:
            pressedKeys.append(e.key)
        elif e.type == pg.KEYUP:
            pressedKeys.remove(e.key)

    Update()

    DrawFrame()

    clock.tick(120)


pg.quit()
