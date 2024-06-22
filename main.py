import pygame
import random
import math

pygame.init()

FPS = 60  ## frames per second

HEIGHT, WIDTH = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS  ## height of each square
RECT_WIDTH = WIDTH // COLS  ## width of each square

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20  ## velocity at which tiles will move

WINDOW = pygame.display.set_mode((HEIGHT, WIDTH))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [
        (237, 229, 218),  ## 2
        (238, 225, 201),  ## 4
        (243, 178, 122),  ## 8
        (246, 150, 101),  ## 16
        (247, 124, 95),  ## 32
        (247, 95, 59),  ## 64
        (237, 208, 115),  ## 128
        (237, 204, 99),  ## 256
        (236, 202, 80),  ## 512
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row  ## starts from 0
        self.col = col  ## starts from 0
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT
        ## for row = 0, col = 0, (x,y)=(0,0), for row = 0, col = 1, (x,y)=(200,0) and so on

    def get_color(self):
        ## for value 2 we want index 0, for value 4 index 1 ...
        ## log2(2) = 1, log2(4) = 2, so subtract 1 from these log2 values
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    ## draw color and the value of the number on that tile
    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        ## place this text in the middle of the tile
        window.blit(
            text,
            (
                self.x
                + (
                    RECT_WIDTH / 2 - text.get_width() / 2
                ),  ## text.get_width() get the width of the text box
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    ## drawing the horizontal lines, line starting from x = 0 and changing the y coordinate
    ## line ending at the WIDTH (800) and y coordinate
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    ## drawing the vertical lines, line starting from x = changing and y = 0
    ## line ending at the x coordinates and HEIGHT (800)
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    ## here (0,0) is the top left corner
    pygame.draw.rect(
        window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), width=OUTLINE_THICKNESS
    )


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window=window)
    pygame.display.update()  ## this will update the window based on the code we write above


## return row, col at random which does not exist already in tiles dictionary
def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)  ## between 0 to ROWS-1
        col = random.randrange(0, COLS)  ## between 0 to COLS-1

        if f"{row}{col}" not in tiles:
            break
    return row, col


def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False  ## sort in ascending order
        delta = (-MOVE_VEL, 0)  ## - as we are moving in left direction
        boundary_check = (
            lambda tile: tile.col == 0
        )  ## to check if we are already at the boundary
        get_next_tile = lambda tile: tiles.get(
            f"{tile.row}{tile.col-1}"
        )  ## get the next tile (to left in this case) if exists
        merge_check = (
            lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        )  ## to check if merge has fully occured
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True  ## round up while determining the position of the tile

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True  ## sort in descending order
        delta = (MOVE_VEL, 0)  ## - as we are moving in left direction
        boundary_check = (
            lambda tile: tile.col == COLS - 1
        )  ## to check if we are already at the boundary
        get_next_tile = lambda tile: tiles.get(
            f"{tile.row}{tile.col+1}"
        )  ## get the next tile if exists
        merge_check = (
            lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        )  ## to check if merge has fully occured
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x 
        )
        ceil = False  ## round down while determining the position of the tile
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False  ## sort in ascending order
        delta = (0, -MOVE_VEL)  ## - as we are moving in left direction
        boundary_check = (
            lambda tile: tile.row == 0
        )  ## to check if we are already at the boundary
        get_next_tile = lambda tile: tiles.get(
            f"{tile.row-1}{tile.col}"
        )  ## get the next tile (to left in this case) if exists
        merge_check = (
            lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        )  ## to check if merge has fully occured
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_WIDTH + MOVE_VEL
        )
        ceil = True  ## round up while determining the position of the tile

    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True  ## sort in descending order
        delta = (0, MOVE_VEL)  ## - as we are moving in left direction
        boundary_check = (
            lambda tile: tile.row == ROWS - 1
        )  ## to check if we are already at the boundary
        get_next_tile = lambda tile: tiles.get(
            f"{tile.row+1}{tile.col}"
        )  ## get the next tile if exists
        merge_check = (
            lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        )  ## to check if merge has fully occured
        move_check = (
            lambda tile, next_tile: tile.y + RECT_WIDTH + MOVE_VEL < next_tile.y 
        )
        ceil = False  ## round down while determining the position of the tile

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                ## skip the remainig code since it is already at boundary
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)

            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    ## change the value of next_tile
                    next_tile.value *= 2
                    ## remove the tile from sorted_tile
                    sorted_tiles.pop(i)
                    ## add next_tile to blocks so that it doesnt merge again
                    blocks.add(next_tile)

            ## if value is not same as the next_tile then we should move the tile until it reaches the border
            ## Here border is the boundary or a tile with different value
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                ## no update or move occurs
                ## skip the remaining code
                continue

            tile.set_pos(ceil)
            updated = True
        ## since we removed some tiles (from the sorted_tiles) we have to remove that tiles from the main tiles dictonary as well
        ## or just copy the keys and values to main tiles dictionary
        update_tiles(window, tiles, sorted_tiles)

    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"

    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"

def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)


## generate two random tiles with value 2 to start the game
def generate_tiles():
    tiles = {}
    for _ in range(2):
        ## _ is used if we dont want to use the variable
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles


def main(window):
    clock = pygame.time.Clock()  ## regulate speed of the loop
    run = True  ## will change to false on exiting the loop

    tiles = generate_tiles()

    while run:
        clock.tick(
            FPS
        )  ## run at most FPS so that every system will run this game at same speed

        for event in pygame.event.get():
            ## if quit button is pressed break the loop and close the program
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, "left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")
        draw(window=window, tiles=tiles)
    pygame.quit()


## we use the following if condition so that no other file that imports this main function can run it.
## This function will only run if this file is run directly
if __name__ == "__main__":
    main(WINDOW)
