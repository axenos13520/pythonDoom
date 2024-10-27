from enum import Enum
import math
import pygame as pg
from pygame.math import clamp
import colors

pg.init()

pg.display.set_caption("test")

windowSize = [1000, 700]

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


def rectangle(topLeft, bottomRight, color):
    top = topLeft[1]
    left = topLeft[0]
    bottom = bottomRight[1]
    right = bottomRight[0]

    position = [(left + right) / 2, (top + bottom) / 2]
    diag = math.sqrt((right - left) ** 2 + (bottom - top) ** 2)

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

        if resultPoint[0] == left or resultPoint[0] == right:
            mult = bottom - top - abs(resultPoint[1] - position[1])

            if mult <= 3:
                mult = 1 - (mult / 3)
            else:
                mult = 1

        else:
            mult = 1 - abs(resultPoint[0] - position[0]) / (right - left) / 5
        return [
            resultPoint,
            [
                clamp(color[0] * mult, 0, 255),
                clamp(color[1] * mult, 0, 255),
                clamp(color[2] * mult, 0, 255),
            ],
        ]

    objectFuncs.append(func)


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

        mult = 1 - distance(resultPoint, position) / size * 0.3

        return [resultPoint, [color[0] * mult, color[1] * mult, color[2] * mult]]

    objectFuncs.append(func)


def ray(point, angle, maxDistance):
    tg = math.tan(angle)

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
            dist = intersection[0] * math.cos(step * (abs(rayCount / 2 - i)))

            height = 20000 / dist

            d = 1 - dist / drawDistance
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
                    i * rayWidth,
                    windowSize[1] * 0.6 - height / 16,
                    rayWidth,
                    height / 8,
                ),
            )
        angle += step

    fpsText = font.render(
        f"{clock.get_fps():.0f}",
        True,
        colors.black,
    )

    fpsTextRect = fpsText.get_rect()

    screen.blit(fpsText, fpsTextRect)

    pg.display.flip()


mapRows = [
    ".------.",
    "|......|",
    ".--.---.",
    "|......|",
    "|..+...|",
    "|......|",
    "|......|",
    ".------.",
]

mapSize = 5
mapSizeHalf = mapSize / 2

cameraSpeed = 5
cameraRotationSpeed = 1.5

cameraPosition = [0, 0]
cameraRotation = 0

obtained = []

for y in range(len(mapRows)):
    for x in range(len(mapRows[y])):
        if mapRows[y][x] == "+":
            cameraPosition = [x * mapSize + mapSizeHalf, y * mapSize + mapSizeHalf]
        elif [x, y] not in obtained:
            topLeft = []
            bottomRight = []

            current = mapRows[y][x]

            if current == "-":
                curX = x
                while current == "-":
                    bottomRight = [
                        curX * mapSize + mapSizeHalf,
                        y * mapSize + mapSizeHalf,
                    ]

                    curX += 1
                    current = mapRows[y][curX]

                    obtained.append([curX, y])
            elif current == "|":
                curY = y
                while current == "|":
                    bottomRight = [
                        x * mapSize + mapSizeHalf,
                        curY * mapSize + mapSizeHalf,
                    ]

                    curY += 1
                    current = mapRows[curY][x]

                    obtained.append([x, curY])

            if len(bottomRight) > 0:
                topLeft = [x * mapSize - mapSizeHalf, y * mapSize - mapSizeHalf]

                rectangle(topLeft, bottomRight, colors.gray)


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
