import pygame as pg, os, random

# define colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (215, 0, 0)
MAROON = (102, 0, 0)
PURPLE = (204, 0, 102)
GREEN = (0, 255, 0)
TITLE_GREY = (142, 142, 142)
GREY = (128, 128, 128)
DARK_GREY = (108, 108, 108)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 200, 240)
LIGHT_GREEN = (102, 255, 102)
YELLOW = (255, 255, 54)
DARK_GREEN = (42, 197, 42)
ORANGE = (255, 69, 0)


class MenuAsteroid():
    def __init__(self, aw, ah, ascreen):
        place = random.randint(0, 3)
        if place == 0:
            self.x = 5
            self.vx = random.randint(4, 11)
            self.vy = random.randint(-6, 6)
            self.y = random.randint(50, ah - 50)
        elif place == 1:
            self.x = aw - 5
            self.vx = random.randint(-11, -4)
            self.vy = random.randint(-6, 6)
            self.y = random.randint(50, ah - 50)
        elif place == 2:
            self.x = random.randint(50, aw - 50)
            self.vx = random.randint(-6, 6)
            self.vy = random.randint(4, 11)
            self.y = 5
        else:
            self.x = random.randint(50, aw - 50)
            self.vx = random.randint(-6, 6)
            self.vy = random.randint(-11, -4)
            self.y = ah - 5
        self.size = random.randint(30, 140)
        self.screen = ascreen

    def draw(self):
        pg.draw.rect(self.screen, DARK_GREY, (self.x, self.y, self.size, self.size))
        self.x += self.vx
        self.y += self.vy

    def destroy(self):
        del self


def draw_menu_border(aw, ah, screen):
    pg.draw.line(screen, DARK_GREY, (0, 5), (aw, 5), 20)
    pg.draw.line(screen, DARK_GREY, (0, ah - 5), (aw, ah - 5), 20)
    pg.draw.line(screen, DARK_GREY, (5, 0), (5, ah), 20)
    pg.draw.line(screen, DARK_GREY, (aw - 5, 0), (aw - 5, ah), 20)


def display_border(window, aw, ah):
    pg.draw.line(window, BLACK, (0, 0), (aw, 0), 8)
    pg.draw.line(window, BLACK, (0, 0), (0, ah), 8)
    pg.draw.line(window, BLACK, (aw, 0), (aw, ah), 11)
    pg.draw.line(window, BLACK, (0, ah), (aw, ah), 11)


def draw_game_over_border(window, x, y, w, h):
    pg.draw.line(window, BLACK, (x, y), (x + w, y), 8)
    pg.draw.line(window, BLACK, (x, y), (x, y + h), 8)
    pg.draw.line(window, BLACK, (x + w, y), (x + w, y + h), 8)
    pg.draw.line(window, BLACK, (x, y + h), (x + w, y + h), 8)


def draw_health_bar(window, w, h, current, total):
    pg.draw.line(window, BLACK, (int(w / 6) - 2, 25), (w - int(w / 6) + 2, 25), 3)
    pg.draw.line(window, BLACK, (int(w / 6) - 2, 40), (w - int(w / 6) + 2, 40), 3)
    pg.draw.line(window, BLACK, (int(w / 6) - 3, 25), (int(w / 6) - 3, 40), 3)
    pg.draw.line(window, BLACK, (w - int(w / 6) + 3, 25), (w - int(w / 6) + 3, 40), 3)
    full_length = (w / 3) * 2
    bar_length = (current / total) * full_length
    hp_percent = (current / total) * 100
    if hp_percent > 80:
        pg.draw.line(window, GREEN, (int(w / 6) - 1, 32), (int(w / 6) + int(bar_length) + 1, 32), 12)
    elif hp_percent > 60:
        pg.draw.line(window, LIGHT_GREEN, (int(w / 6) - 1, 32), (int(w / 6) + int(bar_length) + 1, 32), 12)
    elif hp_percent > 40:
        pg.draw.line(window, YELLOW, (int(w / 6) - 1, 32), (int(w / 6) + int(bar_length) + 1, 32), 12)
    elif hp_percent > 20:
        pg.draw.line(window, ORANGE, (int(w / 6) - 1, 32), (int(w / 6) + int(bar_length) + 1, 32), 12)
    else:
        pg.draw.line(window, RED, (int(w / 6) - 1, 32), (int(w / 6) + int(bar_length) + 1, 32), 12)


# font types
if __name__ == '__main__':
    for font in pg.font.get_fonts():
        print(font)


def render_text(text, type, size, colour):
    new_font = pg.font.SysFont(type, size)
    new_text = new_font.render(text, True, colour)
    return new_text


# load assets
BlueSoldierIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueSoldier.png'))
BlueScoutIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueScout.png'))
BlueSpyIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueSpy.png'))
BlueEnginnerIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueEngineer.png'))
BlueSniperIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueSniper.png'))

RedSoldierIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedSoldier.png'))
RedScoutIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedScout.png'))
RedSpyIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedSpy.png'))
RedEngineerIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedEngineer.png'))
RedSniperIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedSniper.png'))

BlueHQIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueHQ.png'))
BlueTowerIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueTower.png'))
BlueAcademyIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueAcademy.png'))
BlueConstructionIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueConstruction.png'))
BlueQuartersIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Blue Quarters.png'))
BlueInstituteIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'BlueInstitute.png'))
BlueMedBayIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Blue Med Bay.png'))

RedHQIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedHQ.png'))
RedTowerIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedTower.png'))
RedAcademyIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedAcademy.png'))
RedConstructionIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedConstruction.png'))
RedQuartersIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Red Quarters.png'))
RedInstituteIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedInstitute.png'))
RedMedBayIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Red Med Bay.png'))

LabIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Secret Lab.png'))
PostIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Post.png'))

InfiltrateTEXT = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Infiltrate.png'))
TitleWidth = InfiltrateTEXT.get_width()

SecretDocIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'SecretDocument.png'))
WildBerryIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'WildBerries.png'))
TeleIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Teleporter.png'))
RedTeleIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedTeleporter.png'))
CrystalIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Alchemist Crystal.png'))

BoulderIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'Boulder.png'))
RiverIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'River.png'))

RedArrowIMG = pg.image.load(os.path.join(os.path.dirname(__file__), 'art', 'RedArrow.png'))

# get window logo
WindowLogo = RedScoutIMG

# 'image' variable dictionary:
image_lib = {
    'BlueSoldier': BlueSoldierIMG, 'BlueScout': BlueScoutIMG, 'BlueSpy': BlueSpyIMG,
    'BlueEngineer': BlueEnginnerIMG,
    'BlueSniper': BlueSniperIMG,
    'RedSoldier': RedSoldierIMG, 'RedScout': RedScoutIMG, 'RedSpy': RedSpyIMG, 'RedEngineer': RedEngineerIMG,
    'RedSniper': RedSniperIMG,
    'PowSecret': SecretDocIMG, 'PowBerry': WildBerryIMG, 'PowTele': TeleIMG,
    'BlueHQ': BlueHQIMG, 'BlueTower': BlueTowerIMG, 'BlueAcademy': BlueAcademyIMG, 'BlueQuarters': BlueQuartersIMG,
    'BlueConstruction': BlueConstructionIMG, 'BlueInstitute': BlueInstituteIMG, 'BlueMed Bay': BlueMedBayIMG,
    'RedHQ': RedHQIMG, 'RedTower': RedTowerIMG, 'RedAcademy': RedAcademyIMG, 'RedQuarters': RedQuartersIMG,
    'RedConstruction': RedConstructionIMG, 'RedInstitute': RedInstituteIMG, 'RedMed Bay': RedMedBayIMG,
    'Secret Lab': LabIMG, 'Collection Post': PostIMG,
    'Secret Document': SecretDocIMG, 'Wild Berries': WildBerryIMG, 'RedTeleporter': RedTeleIMG,
    'BlueTeleporter': TeleIMG,
    'Alchemist Crystal': CrystalIMG,
    'Boulder': BoulderIMG, 'River': RiverIMG
}


# return icon (B or 'big' images)
def return_icon(image):
    icon_img = pg.transform.scale(image, (200, 200))
    return icon_img


def return_button(image):
    icon_img = pg.transform.scale(image, (75, 75))
    return icon_img


def return_flipped(image):
    flipped_img = pg.transform.flip(image, True, False)
    return flipped_img
