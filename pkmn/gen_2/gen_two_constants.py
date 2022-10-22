import os

from utils.constants import const

class GenTwoConstants:
    def __init__(self):
        self.GEN_TWO_DATA_PATH = os.path.join(const.POKEMON_RAW_DATA, "gen_two")
        self.ITEM_DB_PATH = os.path.join(self.GEN_TWO_DATA_PATH, "items.json")
        self.MOVE_DB_PATH = os.path.join(self.GEN_TWO_DATA_PATH, "moves.json")
        self.MIN_BATTLES_DIR = os.path.join(self.GEN_TWO_DATA_PATH, "min_battles")

        self.CRYSTAL_POKEMON_PATH = os.path.join(self.GEN_TWO_DATA_PATH, "crystal", "pokemon.json")
        self.CRYSTAL_TRAINER_DB_PATH = os.path.join(self.GEN_TWO_DATA_PATH, "crystal", "trainers.json")
        self.GS_POKEMON_PATH = os.path.join(self.GEN_TWO_DATA_PATH, "gold_silver", "pokemon.json")
        self.GS_TRAINER_DB_PATH = os.path.join(self.GEN_TWO_DATA_PATH, "gold_silver", "trainers.json")

        self.ZEPHYR_BADGE = "zephyr"
        self.HIVE_BADGE = "hive"
        self.PLAIN_BADGE = "plain"
        self.FOG_BADGE = "fog"
        self.STORM_BADGE = "storm"
        self.MINERAL_BADGE = "mineral"
        self.GLACIER_BADGE = "glacier"
        self.RISING_BADGE = "rising"

        # kind of janky, but we need to track type boosts in the badge data structure
        # and there aren't any "real" badges for the four
        # So just make some fake ones to serve as flags
        self.EFOUR_WILL_BOOST = "efour_will"
        self.EFOUR_KOGA_BOOST = "efour_koga"
        self.EFOUR_BRUNO_BOOST = "efour_bruno"
        self.EFOUR_KAREN_BOOST = "efour_karen"
        self.EFOUR_LANCE_BOOST = "efour_lance"

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
            "Leader Falkner",
            "Leader Whitney",
            "Leader Bugsy",
            "Leader Morty",
            "Leader Pryce",
            "Leader Jasmine",
            "Leader Chuck",
            "Leader Clair",
            "Elite Four Will",
            "Elite Four Koga",
            "Elite Four Bruno",
            "Elite Four Karen",
            "Champion Lance",
            "Leader Brock",
            "Leader Misty",
            "Leader Lt.surge",
            "Leader Erika",
            "Leader Janine",
            "Leader Sabrina",
            "Leader Blaine",
            "Leader Blue",
            "Leader Red",
        ]

        # TODO: what are the appropriate minor fights for gen 2?
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
            "Leader Falkner": self.ZEPHYR_BADGE,
            "Leader Bugsy": self.HIVE_BADGE,
            "Leader Whitney": self.PLAIN_BADGE,
            "Leader Morty": self.FOG_BADGE,
            "Leader Chuck": self.STORM_BADGE,
            "Leader Jasmine": self.MINERAL_BADGE,
            "Leader Pryce": self.GLACIER_BADGE,
            "Leader Clair": self.RISING_BADGE,

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

        self.NO_BONUS = "No Bonus"
        self.DIG_BONUS = "Dig Bonus"
        self.FLY_BONUS = "Fly Bonus"
        self.SWITCH_BONUS = "Switch Bonus"
        self.MINIMIZE_BONUS = "Minimize Bonus"

        self.MAGNITUDE_MOVE_NAME = "Magnitude"
        self.MAGNITUDE_4 = "Mag 4"
        self.MAGNITUDE_5 = "Mag 5"
        self.MAGNITUDE_6 = "Mag 6"
        self.MAGNITUDE_7 = "Mag 7"
        self.MAGNITUDE_8 = "Mag 8"
        self.MAGNITUDE_9 = "Mag 9"
        self.MAGNITUDE_10 = "Mag 10"

        self.FLAIL_FULL_HP = "100-69 % HP"
        self.FLAIL_HALF_HP = "69-35 % HP"
        self.FLAIL_QUARTER_HP = "35-20 % HP"
        self.FLAIL_TEN_PERCENT_HP = "20-10 % HP"
        self.FLAIL_FIVE_PERCENT_HP = "10-4 % HP"
        self.FLAIL_MIN_HP = "4-0 % HP"

        self.FURY_CUTTER_MOVE_NAME = "Fury Cutter"
        self.ROLLOUT_MOVE_NAME = "Rollout"
        self.TRIPLE_KICK_MOVE_NAME = "Triple Kick"
        self.RAGE_MOVE_NAME = "Rage"

        self.PURSUIT_MOVE_NAME = "Pursuit"
        self.STOMP_MOVE_NAME = "Stomp"
        self.GUST_MOVE_NAME = "Gust"
        self.TWISTER_MOVE_NAME = "Twister"
        self.EARTHQUAKE_MOVE_NAME = "Earthquake"

        self.CUSTOM_MOVE_DATA = {
            self.MAGNITUDE_MOVE_NAME: [
                self.MAGNITUDE_7, self.MAGNITUDE_7 + " " + self.DIG_BONUS,
                self.MAGNITUDE_4, self.MAGNITUDE_4 + " " + self.DIG_BONUS,
                self.MAGNITUDE_5, self.MAGNITUDE_5 + " " + self.DIG_BONUS,
                self.MAGNITUDE_6, self.MAGNITUDE_6 + " " + self.DIG_BONUS,
                self.MAGNITUDE_8, self.MAGNITUDE_8 + " " + self.DIG_BONUS,
                self.MAGNITUDE_9, self.MAGNITUDE_9 + " " + self.DIG_BONUS,
                self.MAGNITUDE_10, self.MAGNITUDE_10 + " " + self.DIG_BONUS,
            ],
            const.FLAIL_MOVE_NAME: [
                self.FLAIL_FULL_HP,
                self.FLAIL_HALF_HP,
                self.FLAIL_QUARTER_HP,
                self.FLAIL_TEN_PERCENT_HP,
                self.FLAIL_FIVE_PERCENT_HP,
                self.FLAIL_MIN_HP,
            ],
            const.REVERSAL_MOVE_NAME: [
                self.FLAIL_FULL_HP,
                self.FLAIL_HALF_HP,
                self.FLAIL_QUARTER_HP,
                self.FLAIL_TEN_PERCENT_HP,
                self.FLAIL_FIVE_PERCENT_HP,
                self.FLAIL_MIN_HP,
            ],
            self.FURY_CUTTER_MOVE_NAME: ["1", "2", "3", "4", "5", "6"],
            self.ROLLOUT_MOVE_NAME: ["1", "2", "3", "4", "5", "5 + DefenseCurl"],
            self.TRIPLE_KICK_MOVE_NAME: ["1", "2", "3"],
            self.RAGE_MOVE_NAME: ["1", "2", "3", "4", "5", "6"],

            self.PURSUIT_MOVE_NAME: [self.NO_BONUS, self.SWITCH_BONUS],
            self.STOMP_MOVE_NAME: [self.NO_BONUS, self.MINIMIZE_BONUS],
            self.GUST_MOVE_NAME: [self.NO_BONUS, self.FLY_BONUS],
            self.TWISTER_MOVE_NAME: [self.NO_BONUS, self.FLY_BONUS],
            self.EARTHQUAKE_MOVE_NAME: [self.NO_BONUS, self.DIG_BONUS],
        }

        self.HELD_ITEM_BOOSTS = {
            "Black Belt": const.TYPE_FIGHTING,
            "BlackGlasses": const.TYPE_DARK,
            "Charcoal": const.TYPE_FIGHTING,
            "Dragon Scale": const.TYPE_DRAGON,
            "Hard Stone": const.TYPE_ROCK,
            "Magnet": const.TYPE_ELECTRIC,
            "Metal Coat": const.TYPE_STEEL,
            "Miracle Seed": const.TYPE_GRASS,
            "Mystic Water": const.TYPE_WATER,
            "Pink Bow": const.TYPE_NORMAL,
            "Polkadot Bow": const.TYPE_NORMAL,
            "Poison Barb": const.TYPE_POISON,
            "Sharp Beak": const.TYPE_FLYING,
            "SilverPowder": const.TYPE_BUG,
            "Soft Sand": const.TYPE_GROUND,
            "Spell Tag": const.TYPE_GHOST,
            "TwistedSpoon": const.TYPE_PSYCHIC,
        }

        self.STAT_INCREASE_MOVES = {
            "Growth": [(const.SPA, 1), (const.SPD, 1)],
            "Swords Dance": [(const.ATK, 2)],
            "Meditate": [(const.ATK, 1)],
            "Agility": [(const.SPE, 2)],
            "Double Team": [(const.EV, 1)],
            "Harden": [(const.DEF, 1)],
            "Minimize": [(const.EV, 1)],
            "Withdraw": [(const.DEF, 1)],
            "Barrier": [(const.DEF, 2)],
            "Amnesia": [(const.SPA, 2), (const.SPD, 2)],
            "Acid Armor": [(const.DEF, 2)],
            "Sharpen": [(const.ATK, 1)],
        }

        # still source of badge boost, but not controlled by player
        self.STAT_DECREASE_MOVES = {
            "Sand Attack": [(const.ACC, -1)],
            "Smokescreen": [(const.ACC, -1)],
            "Kinesis": [(const.ACC, -1)],
            "Flash": [(const.ACC, -1)],
            "Tail Whip": [(const.DEF, -1)],
            "Leer": [(const.DEF, -1)],
            "Growl": [(const.ATK, -1)],
            "String Shot": [(const.SPE, -1)],
            "Screech": [(const.DEF, -2)],
            "Acid": [(const.DEF, -1)],
            "BubbleBeam": [(const.SPE, -1)],
            "Bubble": [(const.SPE, -1)],
            "Constrict": [(const.SPE, -1)],
            "Aurora Beam": [(const.ATK, -1)],
            "Psychic": [(const.SPA, -1), (const.SPD, -1)],
        }

        self.SPECIAL_TYPES = [
            "Water",
            "Grass",
            "Fire",
            "Ice",
            "Electric",
            "Psychic",
            "Dragon",
            "Dark"
        ]

        self.TYPE_CHART = {
            const.TYPE_TYPELESS: {},
            const.TYPE_NORMAL: {
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.IMMUNE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE
            },
            const.TYPE_FIGHTING: {
                const.TYPE_NORMAL: const.SUPER_EFFECTIVE,
                const.TYPE_FLYING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_POISON: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_BUG: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.IMMUNE,
                const.TYPE_STEEL: const.SUPER_EFFECTIVE,
                const.TYPE_PSYCHIC: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ICE: const.SUPER_EFFECTIVE,
                const.TYPE_DARK: const.SUPER_EFFECTIVE,
            },
            const.TYPE_FLYING: {
                const.TYPE_FIGHTING: const.SUPER_EFFECTIVE,
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_ELECTRIC: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_POISON: {
                const.TYPE_POISON: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GROUND: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.NOT_VERY_EFFECTIVE,
                const.TYPE_STEEL: const.IMMUNE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
            },
            const.TYPE_GROUND: {
                const.TYPE_FLYING: const.IMMUNE,
                const.TYPE_POISON: const.SUPER_EFFECTIVE,
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_BUG: const.NOT_VERY_EFFECTIVE,
                const.TYPE_STEEL: const.SUPER_EFFECTIVE,
                const.TYPE_FIRE: const.SUPER_EFFECTIVE,
                const.TYPE_GRASS: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ELECTRIC: const.SUPER_EFFECTIVE,
            },
            const.TYPE_ROCK: {
                const.TYPE_FIGHTING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FLYING: const.SUPER_EFFECTIVE,
                const.TYPE_GROUND: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.SUPER_EFFECTIVE,
                const.TYPE_ICE: const.SUPER_EFFECTIVE,
            },
            const.TYPE_BUG: {
                const.TYPE_FIGHTING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FLYING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_POISON: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.NOT_VERY_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_PSYCHIC: const.SUPER_EFFECTIVE,
                const.TYPE_DARK: const.SUPER_EFFECTIVE,
            },
            const.TYPE_GHOST: {
                const.TYPE_NORMAL: const.IMMUNE,
                const.TYPE_GHOST: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_PSYCHIC: const.SUPER_EFFECTIVE,
                const.TYPE_DARK: const.NOT_VERY_EFFECTIVE,
            },
            const.TYPE_STEEL: {
                const.TYPE_ROCK: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_WATER: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ELECTRIC: const.NOT_VERY_EFFECTIVE,
                const.TYPE_ICE: const.SUPER_EFFECTIVE,
            },
            const.TYPE_FIRE: {
                const.TYPE_ROCK: const.NOT_VERY_EFFECTIVE,
                const.TYPE_BUG: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.SUPER_EFFECTIVE,
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
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
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
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_PSYCHIC: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DARK: const.IMMUNE,
            },
            const.TYPE_ICE: {
                const.TYPE_FLYING: const.SUPER_EFFECTIVE,
                const.TYPE_GROUND: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_FIRE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_WATER: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GRASS: const.SUPER_EFFECTIVE,
                const.TYPE_ICE: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DRAGON: const.SUPER_EFFECTIVE,
            },
            const.TYPE_DRAGON: {
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_DRAGON: const.SUPER_EFFECTIVE,
            },
            const.TYPE_DARK: {
                const.TYPE_FIGHTING: const.NOT_VERY_EFFECTIVE,
                const.TYPE_GHOST: const.SUPER_EFFECTIVE,
                const.TYPE_STEEL: const.NOT_VERY_EFFECTIVE,
                const.TYPE_PSYCHIC: const.SUPER_EFFECTIVE,
                const.TYPE_DARK: const.NOT_VERY_EFFECTIVE,
            },
        }

gen_two_const = GenTwoConstants()