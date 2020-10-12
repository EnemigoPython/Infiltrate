import pygame as pg, load_art as art


class GridObject:
    # xy always a tuple
    def __init__(self, xy, team, game_id, static, w, h):
        if team is None:
            self.image = art.image_lib.get(game_id)
        else:
            self.image = art.image_lib.get(f'{team}{game_id}')
        if w > 1 or h > 1:
            self.multi_cell = True
            self.xy = []
            for cx in range(w):
                self.xy.append(((xy[0] + cx), xy[1]))
                for cy in range(h - 1):
                    self.xy.append(((xy[0] + cx), (xy[1] + cy + 1)))
        else:
            self.multi_cell = False
            self.xy = xy
        self.team = team
        self.game_id = game_id
        self.static = static
        self.w = w
        self.h = h

    def scale_image(self, size):
        if self.multi_cell:
            self.image = pg.transform.scale(self.image, (size * self.w, size * self.h))
        else:
            self.image = pg.transform.scale(self.image, (size, size))

    def check_death(self):
        if self.current_hp <= 0:
            return True
        else:
            return False

    def refresh(self):
        if not self.static:
            if self.game_id == 'Sniper' and self.special_used:
                self.range /= 2
            if self.game_id == 'Engineer' and self.building_timer > 1:
                self.building_timer -= 1
            else:
                self.steps_remaining = self.speed
                if not self.game_id == 'Spy':
                    self.special_condition = True
                    self.special_used = False
                self.has_attacked = False
                if self.game_id == 'Spy' and self.activities[2] == 1:
                    self.activities = [0, 0, 1]
                else:
                    self.activities = [0, 0, 0]
                if self.game_id == 'Soldier':
                    self.turn_attacks = 0
                if self.game_id == 'Engineer':
                    self.activities[1] = 1

    def generic_description(self):
        if self.game_id == 'Secret Lab':
            return ['Documents are extracted from here. They appear', 'every five rounds.']
        elif self.game_id == 'Boulder':
            return ''
        elif self.game_id == 'Collection Post':
            return ['Bring secret documents here to collect them', 'and unlock new technologies.']
        elif self.game_id == 'Wild Berries':
            return ['Berries that grow on the battlefield and will', 'heal a unit for 15 health.']
        elif self.game_id == 'Alchemist Crystal':
            return ['This crystal will instantly heal and double the', 'health of any unit.']
        elif self.game_id == 'Secret Document':
            return 'Bring this back to a collection post to advance.'


class Unit(GridObject):
    def __init__(self, xy, team, game_id):
        static = False
        # move, attack, special
        self.activities = [0, 0, 0]
        self.can_attack = True
        self.has_attacked = False
        self.special_move = None
        self.special_condition = True
        self.special_used = False
        self.manual_special = False
        self.hp = 100
        self.damage = 20
        self.speed = 5
        self.range = 6
        if game_id == 'Soldier':
            self.special_move = 'Burst Fire'
            self.turn_attacks = 0
        if game_id == 'Scout':
            self.special_move = 'Nomad'
            self.manual_special = True
            self.hp -= 25
            self.damage -= 5
            self.speed += 3
        if game_id == 'Engineer':
            self.special_move = 'Build'
            self.manual_special = True
            self.can_attack = False
            self.speed -= 2
            self.range = 1
            self.build_menu = False
            self.building_timer = 0
        if game_id == 'Spy':
            self.special_move = 'Blend'
            self.hp -= 25
            self.damage += 40
            self.speed += 2
            self.range -= 4
        if game_id == 'Sniper':
            self.special_move = 'Entrenched'
            self.manual_special = True
            self.hp -= 25
            self.damage += 20
            self.speed -= 3
            self.range += 2
        self.current_hp = self.hp
        self.steps_remaining = self.speed
        self.flipped = False
        self.carrying = False
        super().__init__(xy, team, game_id, static, w=1, h=1)

    def special_move_description(self):
        if self.game_id == 'Soldier':
            return 'Soldier can attack twice per turn.'
        elif self.game_id == 'Scout':
            return ['Scout can sacrifice his attack to double', 'his speed.']
        elif self.game_id == 'Engineer':
            return 'Engineer can build structures.'
        elif self.game_id == 'Spy':
            return ['Spy can only be attacked by the enemy', 'if he has himself made an attack.']
        elif self.game_id == 'Sniper':
            return ['Sniper can sacrifice his movement to', 'double his range.']

    def use_special(self):
        if self.game_id == 'Engineer' and not self.special_used:
            self.build_menu = True
        elif self.special_condition and not self.special_used:
            self.special_used = True
            if self.game_id == 'Scout':
                self.steps_remaining += self.speed
                self.has_attacked = True
                self.activities[0] = 0
            if self.game_id == 'Sniper':
                self.range *= 2
                self.steps_remaining = 0

    def flip_unit(self):
        self.image = art.return_flipped(self.image)
        self.flipped = not self.flipped


class Building(GridObject):
    def __init__(self, xy, team, game_id, con_type=None):
        static = True
        self.produce = None
        self.produce_time = 2
        self.range = None
        self.hp = 200
        self.con_type = con_type
        if game_id == 'Secret Lab':
            w, h = 2, 2
        if game_id == 'Construction':
            w, h = 2, 2
            self.construct_timer = 2
            if con_type == 'Tower':
                w, h = 2, 4
            if con_type == 'Quarters':
                self.construct_timer = 3
            if con_type == 'Med Bay':
                w, h = 3, 3
                self.construct_timer = 3
            if con_type == 'Institute':
                self.construct_timer = 4
            if con_type == 'Teleporter':
                w, h = 1, 1
                self.construct_timer = 3
            self.hp = 50
        if game_id == 'HQ':
            w, h = 4, 4
            self.hp = 500
            self.produce = 'Engineer'
            self.produce_time = 1
        if game_id == 'Tower':
            w, h = 2, 4
            self.hp = 250
            self.range = 2
            self.damage = 40
        if game_id == 'Academy':
            w, h = 2, 2
            self.produce = 'Soldier', 'Scout'
        if game_id == 'Institute':
            w, h = 2, 2
            self.produce = 'Spy', 'Sniper'
            self.produce_time = 3
        if game_id == 'Med Bay':
            w, h = 3, 3
            self.hp = 150
            self.range = 4
            self.healing = 20
        if game_id == 'Quarters':
            w, h = 2, 2
        if game_id == 'Teleporter':
            w, h = 1, 1
            self.hp = 100
            self.range = 1
        self.current_hp = self.hp
        self.queue = None
        self.queue_timer = self.produce_time
        super().__init__(xy, team, game_id, static, w, h)

    def production(self):
        self.queue_timer -= 1
        if self.queue_timer == 0:
            self.queue_timer = self.produce_time
            return True
        else:
            return False

    def construct_finished(self):
        self.construct_timer -= 1
        if self.construct_timer == 0:
            return True
        else:
            return False

    def building_description(self):
        if self.game_id == 'HQ':
            return ['The HQ produces engineers. Also, the', 'enemy will win if they destroy it.']
        if self.game_id == 'Academy':
            return 'The academy produces soldiers and scouts.'
        if self.game_id == 'Tower':
            return ['The tower will do 40 damage to any type', 'of enemy in its range at the end of the round.']
        if self.game_id == 'Quarters':
            return 'The quarters increase the unit limit by 5.'
        if self.game_id == 'Institute':
            return 'The institute produces snipers and spies.'
        if self.game_id == 'Med Bay':
            return ['The med bay will heal 20 damage to', 'units and buildings within its range.']
        if self.game_id == 'Teleporter':
            return ['The teleporter allows a unit to teleport', 'instantly to another point on the map.']

    def button_1(self):
        if type(self.produce) == tuple:
            return art.return_button(art.image_lib.get(f'{self.team}{self.produce[0]}'))
        else:
            return art.return_button(art.image_lib.get(f'{self.team}{self.produce}'))

    def button_2(self):
        return art.return_button(art.image_lib.get(f'{self.team}{self.produce[1]}'))


class PowerUp(GridObject):
    def __init__(self, xy, game_id):
        static = True
        team = None
        if game_id == 'Wild Berries':
            self.heal = 15
        self.range = None
        super().__init__(xy, team, game_id, static, w=1, h=1)

    def use_power(self, unit):
        if self.game_id == 'Wild Berries' and unit.current_hp < unit.hp:
            if self.heal + unit.current_hp >= unit.hp:
                unit.current_hp = unit.hp
            else:
                unit.current_hp += self.heal
        if self.game_id == 'Alchemist Crystal':
            unit.hp *= 2
            unit.current_hp = unit.hp
        if self.game_id == 'Secret Document':
            unit.carrying = True


class Terrain(GridObject):
    def __init__(self, xy, game_id):
        static = True
        team = None
        if game_id == 'Collection Post':
            self.range = 1
        else:
            self.range = None
        super().__init__(xy, team, game_id, static, w=1, h=1)
