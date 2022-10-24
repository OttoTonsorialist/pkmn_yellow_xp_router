import os

from utils.constants import const

class GenOneConstants:
    def __init__(self):
        self.GEN_ONE_DATA_PATH = os.path.join(const.POKEMON_RAW_DATA, "gen_one")
        self.ITEM_DB_PATH = os.path.join(self.GEN_ONE_DATA_PATH, "items.json")
        self.MOVE_DB_PATH = os.path.join(self.GEN_ONE_DATA_PATH, "moves.json")

        self.YELLOW_ASSETS_PATH = os.path.join(self.GEN_ONE_DATA_PATH, "yellow")
        self.YELLOW_POKEMON_DB_PATH = os.path.join(self.YELLOW_ASSETS_PATH, "pokemon.json")
        self.YELLOW_TRAINER_DB_PATH = os.path.join(self.YELLOW_ASSETS_PATH, "trainers.json")
        self.YELLOW_MIN_BATTLES_DIR = os.path.join(self.YELLOW_ASSETS_PATH, "min_battles")

        self.RB_ASSETS_PATH = os.path.join(self.GEN_ONE_DATA_PATH, "red_blue")
        self.RB_POKEMON_DB_PATH = os.path.join(self.RB_ASSETS_PATH, "pokemon.json")
        self.RB_TRAINER_DB_PATH = os.path.join(self.RB_ASSETS_PATH, "trainers.json")
        self.RB_MIN_BATTLES_DIR = os.path.join(self.RB_ASSETS_PATH, "min_battles")

        self.BOULDER_BADGE = "boulder"
        self.CASCADE_BADGE = "cascade"
        self.THUNDER_BADGE = "thunder"
        self.RAINDBOW_BADGE = "rainbow"
        self.SOUL_BADGE = "soul"
        self.MARSH_BADGE = "marsh"
        self.VOLCANO_BADGE = "volcano"
        self.EARTH_BADGE = "earth"

        self.BAG_LIMIT = 20

        self.MAJOR_FIGHTS = [
            "Brock 1",
            "Misty 1",
            "LtSurge 1",
            "Erika 1",
            "Koga 1",
            "Sabrina 1",
            "Blaine 1",
            "Giovanni 3",
            "Agatha 1",
            "Bruno 1",
            "Lorelei 1",
            "Lance 1",
            "Rival3 Jolteon",
            "Rival3 Flareon",
            "Rival3 Vaporeon",
            "Rival3 Squirtle",
            "Rival3 Bulbasaur",
            "Rival3 Charmander",
        ]

        self.MINOR_FIGHTS = [
            "Giovanni 1",
            "Giovanni 2",
            # rb yival fights
            "Rival1 Squirtle 1",
            "Rival1 Bulbasaur 1",
            "Rival1 Charmander 1",
            "Rival1 Squirtle 2",
            "Rival1 Bulbasaur 2",
            "Rival1 Charmander 2",
            "Rival1 Squirtle 3",
            "Rival1 Bulbasaur 3",
            "Rival1 Charmander 3",
            "Rival2 Squirtle 1",
            "Rival2 Bulbasaur 1",
            "Rival2 Charmander 1",
            "Rival2 Squirtle 2",
            "Rival2 Bulbasaur 2",
            "Rival2 Charmander 2",
            "Rival2 Squirtle 3",
            "Rival2 Bulbasaur 3",
            "Rival2 Charmander 3",
            "Rival2 Squirtle 4",
            "Rival2 Bulbasaur 4",
            "Rival2 Charmander 4",
            # yellow rival fights
            "Rival1 1",
            "Rival1 2",
            "Rival1 3",
            "Rival2 1",
            "Rival2 2 Jolteon",
            "Rival2 2 Flareon",
            "Rival2 2 Vaporeon",
            "Rival2 3 Jolteon",
            "Rival2 3 Flareon",
            "Rival2 3 Vaporeon",
            "Rival2 4 Jolteon",
            "Rival2 4 Flareon",
            "Rival2 4 Vaporeon",
        ]

        self.BADGE_REWARDS = {
            "Brock 1": self.BOULDER_BADGE,
            "Misty 1": self.CASCADE_BADGE,
            "LtSurge 1": self.THUNDER_BADGE,
            "Erika 1": self.RAINDBOW_BADGE,
            "Koga 1": self.SOUL_BADGE,
            "Sabrina 1": self.MARSH_BADGE,
            "Blaine 1": self.VOLCANO_BADGE,
            "Giovanni 3": self.EARTH_BADGE,
        }

        self.FIGHT_REWARDS = {
            "Brock 1": "TM34 Bide",
            "Misty 1": "TM11 Bubblebeam",
            "LtSurge 1": "TM24 Thunderbolt",
            "Erika 1": "TM21 Mega Drain",
            "Koga 1": "TM06 Toxic",
            "Sabrina 1": "TM46 Psywave",
            "Blaine 1": "TM38 Fire Blast",
            "Giovanni 3": "TM27 Fissure",
            "SuperNerd 2": "Helix Fossil",
            "Rocket 6": "Nugget",
            "Rocket 5": "TM28 Dig",
            "Rocket 28": "Card Key",
            "Jessie & James 3": "Poke Flute",
        }

        self.SPECIAL_TYPES = [
            "Water",
            "Grass",
            "Fire",
            "Ice",
            "Electric",
            "Psychic",
            "Dragon"
        ]

        self.TYPE_CHART = {
            const.TYPE_NORMAL: {
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.IMMUNE
            },
            const.TYPE_FIGHTING: {
                const.TYPE_NORMAL: const.SUPER_EFFECTIVE,
                const.TYPE_FLYING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_POISON: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_BUG: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.IMMUNE,
                const.TYPE_PSYCHIC: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ICE: const.SUPER_EFFECTIVE,
            },
            const.TYPE_FLYING: {
                const.TYPE_FIGHTING: const.SUPER_EFFECTIVE,
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_ELECTRIC: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_POISON: {
                const.TYPE_POISON: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GROUND: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_GHOST: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
            },
            const.TYPE_GROUND: {
                const.TYPE_FLYING: const.IMMUNE,
                const.TYPE_POISON: const.SUPER_EFFECTIVE,
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_BUG: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.SUPER_EFFECTIVE,
                const.TYPE_GRASS: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ELECTRIC: const.SUPER_EFFECTIVE,
            },
            const.TYPE_ROCK: {
                const.TYPE_FIGHTING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FLYING: const.SUPER_EFFECTIVE,
                const.TYPE_GROUND: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_FIRE: const.SUPER_EFFECTIVE,
                const.TYPE_ICE: const.SUPER_EFFECTIVE,
            },
            const.TYPE_BUG: {
                const.TYPE_FIGHTING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FLYING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_POISON: const.SUPER_EFFECTIVE,
                const.TYPE_GHOST: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_PSYCHIC: const.SUPER_EFFECTIVE,
            },
            const.TYPE_GHOST: {
                const.TYPE_NORMAL: const.IMMUNE,
                const.TYPE_GHOST: const.SUPER_EFFECTIVE,
                const.TYPE_PSYCHIC: const.IMMUNE,
            },
            const.TYPE_FIRE: {
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_FIRE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_WATER: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_ICE: const.SUPER_EFFECTIVE,
                const.TYPE_DRAGON: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_WATER: {
                const.TYPE_GROUND: const.SUPER_EFFECTIVE,
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_FIRE: const.SUPER_EFFECTIVE,
                const.TYPE_WATER: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DRAGON: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_GRASS: {
                const.TYPE_FLYING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_POISON: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GROUND: const.SUPER_EFFECTIVE,
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_BUG: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_WATER: const.SUPER_EFFECTIVE,
                const.TYPE_GRASS: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DRAGON: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_ELECTRIC: {
                const.TYPE_FLYING: const.SUPER_EFFECTIVE,
                const.TYPE_GROUND: const.IMMUNE,
                const.TYPE_WATER: const.SUPER_EFFECTIVE,
                const.TYPE_GRASS: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ELECTRIC: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DRAGON: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_PSYCHIC: {
                const.TYPE_FIGHTING: const.SUPER_EFFECTIVE,
                const.TYPE_POISON: const.SUPER_EFFECTIVE,
                const.TYPE_PSYCHIC: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_ICE: {
                const.TYPE_FLYING: const.SUPER_EFFECTIVE,
                const.TYPE_GROUND: const.SUPER_EFFECTIVE,
                const.TYPE_WATER: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_ICE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DRAGON: const.SUPER_EFFECTIVE,
            },
            const.TYPE_DRAGON: {
                const.TYPE_DRAGON: const.SUPER_EFFECTIVE,
            },
        }

gen_one_const = GenOneConstants()