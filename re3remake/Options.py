from dataclasses import dataclass
from Options import (Choice, OptionList, OptionGroup, NamedRange, 
    StartInventoryPool,
    PerGameCommonOptions, DeathLinkMixin)

class Difficulty(Choice):
    """Assisted: ... Okay, fine. No judgment here. :)
    Standard: Most people should play on this.
    Hardcore: Slightly tougher, but not by much. 
    Nightmare: It actually rains zombies, Kappa.
    Inferno: Hope your name isn't Gohan, because you need to dodge.. a lot."""
    display_name = "Difficulty to Play On"
    option_assisted = 0
    option_standard = 1
    option_hardcore = 2
    option_nightmare = 3
    option_inferno = 4
    default = 1

# Typewriter teleports are intentionally disabled in RE3.
# class UnlockedTypewriters(OptionList):
#     """Specify exact typewriter names to unlock as teleport destinations."""
#     display_name = "Unlocked Typewriters"

class AllowMissableLocations(Choice):
    """Accidentally skipping item locations early can lead to softlocking as certain story triggers make it impossible to backtrack. 
    This option seeks to avoid that by limiting item placements.

    False: (Default) Will place items so they are not permanently missable.
    This severely limits where progression can be to prevent softlocking of any kind. 
    Will also remove progression for others if multiworld.
    Enemies will not have progression at all if this is off, as well.
    
    True: Progression can be placed in locations that can be missed if story progresses too far, including enemies, which may require you to reload an older save or restart if you skip any.. You've been warned.

    NOTE - This option only affects *YOUR* game. Your progression can still be in someone else's if they have this option enabled."""
    display_name = "Allow Missable Locations"
    option_false = 0
    option_true = 1
    default = 0
    
class AllowProgressionInNEST(Choice):
    """While next to impossible to skip anything in NEST, it would certainly feel bad if someone's Morph Ball ended up there.
    This option will completely remove progression from being at your end game, including the ten locations in Nemesis Final Fight. 

    False: (Default) Will place useful/junk items into NEST, including enemies, the non-randomized locations will stay the same.

    True: Progression can be placed in NEST, including enemies there, remind everyone it was your fault when you are holding them hostage."""
    display_name = "Allow Progression in NEST"
    option_false = 0
    option_true = 1
    default = 0

class AddFilesAsLocations(Choice):
    """Adds the 52 collectible documents found throughout the game as checks.
    This is only adds filler to the item pool, as documents do nothing for you.

    None: Keep vanilla file behavior.
    All: Randomize every collectible document (map pickups excluded).
    """
    display_name = "Add Files as Locations"
    option_none = 0
    option_all = 1
    default = 0
	
class AddEnemyKillsAsLocations(Choice):
    """When enabled, multiworld items are also placed on the enemies in your world. Killing those enemies gives the item.

    Currently only supports Assisted / Standard difficulty / Hard difficulty.

    The available options are:

    None: You decided not to add hundreds of enemy locations to your world. Probably a good idea tbh.
    All: Every interactable enemy from the Subway Station to the end of the game now gives an item when killed.
    """
    display_name = "Add Enemy Kills as Locations"
    option_none = 0
    option_all = 1
    default = 0

class EnemyKillItems(Choice):
    """While the Add Enemy Kills as Locations option is enabled, this option specifies the items that each kill adds to the item pool.

    (The items you choose here are STILL randomized. It's just that enemies don't drop items at all in RE3R, so we have to ask what they should have *vanilla*.)

    The available options are:

    Mixed: A mix of combat-related items (healing, ammo, subweapons, gunpowder) is added to the pool in equal parts.
    All Weapon Related: Like Mixed, but healing items are not added. Ammo, subweapons, and gunpowder are still added. 
    Ammo Related: Like Mixed, but healing items and subweapons are not added. Ammo and gunpowder are still added.
    Ammo: Only ammo is added.
    Gunpowder: Only gunpowder is added.
    Healing: Only healing items are added.
    Trash: Only filler items are added.
    """
    display_name = "Enemy Item Kills"
    option_mixed = 0
    option_all_weapon_related = 1
    option_ammo_related = 2
    option_ammo = 3
    option_gunpowder = 4
    option_healing = 5
    default = 3

class EnemyBehavior(Choice):
    """Changes how aggressively enemies behave.

    Off: Vanilla enemy behavior.
    Doors: Enemies can interact with more doors and pursue more aggressively.
    Unsafe Rooms: Includes Doors, and safe rooms are no longer treated as safe for normal enemies.
    Full: Includes Unsafe Rooms, and Nemesis is also allowed through more doors.
    """
    display_name = "Enemy Behavior"
    option_off = 0
    option_doors = 1
    option_unsafe_rooms = 2
    option_full = 3
    default = 0

class SpeedyEnemyMode(Choice):
    """Controls whether enemies are speedy speed boys. Gasolines burning...

    If option is on, enemies can be much quicker than before and Nemesis can be included.

    This can be used in conjunction with Invisible Enemies.. 
    Although I highly recommend that you don't do that...

    Off: Vanilla enemy movement speed.
    Enemies Only: Applies the chosen speed to all enemies except Nemesis.
    Including Nemesis: Applies the chosen speed to all enemies, including Nemesis.
    """
    display_name = "Speedy Enemy Mode"
    option_off = 0
    option_enemies_only = 1
    option_including_nemesis = 2
    default = 0

class SpeedyEnemyMultiplier(Choice):
    """Sets the speed of enemy movement when Speedy Boy Mode is not 'Off'.

    The option choices should be pretty self explanatory.. but don't use "Extreme".
    It's not fun, and likely unbeatable on harder difficulties. You've been warned.

    Slow: 0.5x
    Normal: 1.0x
    Fast: 1.5x
    Very Fast: 2.0x
    Extreme: 3.0x
    """
    display_name = "Speedy Enemy Multiplier"
    option_slow = 0
    option_normal = 1
    option_fast = 2
    option_very_fast = 3
    option_extreme = 4
    default = 1

class InvisibleEnemyMode(Choice):
    """Make enemies invisible. 

    This option is a bad idea to turn on in multiworld settings.

    This option is a worse idea to use with 'Enemy Behavior' on 'Full' and likely 
    impossible and an even worser idea with 'Enemy Movement Speed' cranked up 

    You don't want to turn this on.

    This isn’t like that time in Guitar Hero where they ask if you want to play Free Bird, 
    you say yes and then they ask if you’re sure, and you say yes again.

    Invisible Enemy Mode means exactly what it says. 
    The enemies are invisible. 
    All of them. 
    You will not see them.
    But they can most certainly see you.

    Are you absolutely sure you want to enable it?
 
    'Man, you must really like Invisible Enemy Mode.'

    Off: Vanilla visible enemies.
    Enemies Only: All enemies except Nemesis are invisible.
    Including Nemesis: All enemies including Nemesis are invisible. Likely impossible to beat.
    """
    display_name = "Invisible Enemies"
    option_off = 0
    option_enemies_only = 1
    option_including_nemesis = 2
    default = 0

class EarlyFireHose(Choice):
    """Receiving Fire Hose late can lead to some intense BK.
    This option will place it early to lower the odds of BK.

    False: Normal, will place it anywhere in the world and you may be waiting a bit to progress.
    True: Will place it in Sphere 1 of the world, and should prevent lengthy BK."""
    display_name = "Early Fire Hose"
    option_false = 0
    option_true = 1
    default = 0

class ExtraSewerItems(Choice):
    """Not getting Battery Pack or Kendo Gate Key early can lead to the same situation.
    This option adds an extra set of these items so the odds of BK are lower.

    False: Normal, only 1 of each are in the item pool.
    True: Now, 2 of each are in the item pool."""
    display_name = "Extra Sewer Items"
    option_false = 0
    option_true = 1
    default = 0

class StartingHipPouches(Choice):
    """The number of hip pouches you want to start the game with, to a max of 3. 
    Any that you start with are taken out of the item pool and replaced with junk.
    
    Pockets: Equivalent of zero starting hip pouches. 
    Fanny pack: Equivalent of one starting hip pouch. 
    Purse: Equivalent of two starting hip pouches.
    Backpack: Equivalent of three starting hip pouches."""
    display_name = "Starting Hip Pouches"
    option_pockets = 0
    option_fanny_pack = 1
    option_purse = 2
    option_backpack = 3
    default = 0

class BonusStart(Choice):
    """Some players might want to start with a little help in the way of a few extra heal items and packs of ammo.
    This will give you grenades instead of ammo if Oops All Grenades option is set.

    False: Normal, don't start with extra heal items and packs of ammo.
    True: Start with those helper items."""
    display_name = "Bonus Start"
    option_false = 0
    option_true = 1
    default = 0
	
class LocalWeapons(Choice):
    """Enabling this ensures that all of your weapons are placed in your own world instead of other players' worlds."""
    display_name = "Local Weapons"
    option_false = 0
    option_true = 1
    default = 0

class DoubleWeapons(Choice):
    """Enabling this ensures that a duplicate of each weapon is in the item pool, increasing the chances that you find more weapons early. 
    If a weapon already has a duplicate (like the shotgun / grenade launcher), this option doesn't add any additional copies of that weapon."""
    display_name = "Double Weapons"
    option_false = 0
    option_true = 1
    default = 0

class AmmoPackModifier(Choice):
    """This option, when set, will modify the quantity of ammo in each ammo pack. This can make the game easier or much, much harder.
    The available options are:

    None: You realized that consistency in ammo pack quantities is one of the few true joys in life, and this causes you to not modify them at all.
    Max: Each ammo pack will contain the maximum amount of ammo that the game allows. (i.e., you will never, ever run out of ammo.)
    Double: Each ammo pack will contain twice as much ammo as it normally contains.
    Half: Each ammo pack will contain half as much ammo as it normally contains.
    Only Three: Each ammo pack will have an ammo count of 3.
    Only Two: Each ammo pack will have an ammo count of 2.
    Only One: Each ammo pack will have an ammo count of 1. (Yes, your Handgun Ammo pack will have a single bullet in it.)
    Random By Type: Each ammo type's ammo pack will have a random quantity of ammo, and you will get that same quantity of ammo from every pack for that ammo type.
        (For example, you receive a Shotgun Shells pack that has a random quantity of 7 ammo. All Shotgun Shells packs will have a quantity of 7.)
    Random Always: Each ammo pack will have a random quantity of ammo, and that quantity will be randomized every time.
        (For example, you receive a Shotgun Shells pack that has a random quantity of 7 ammo. Your next Shotgun Shells pack has a quantity of 4, next has 2, etc.)

    NOTE: The options for "Only Three", "Only Two", "Only One", "Random By Type", and "Random Always" are not guaranteed to be reasonably beatable."""
    display_name = "Ammo Pack Modifier"
    option_none = 0
    option_max = 1
    option_double = 2
    option_half = 3
    option_only_three = 4
    option_only_two = 5
    option_only_one = 6
    option_random_by_type = 7
    option_random_always = 8
	
class OopsAllGrenades(Choice):
    """Enabling this swaps all weapons, ammo, subweapons, upgrades and explosive/gunpowder to Grenades.
    (Except your starting weapon)"""
    display_name = "Oops! All Grenades"
    option_false = 0
    option_true = 1
    default = 0
    
class OopsAllHandguns(Choice):
    """Enabling this swaps all weapons, ammo, subweapons, upgrades and explosive/gunpowder to Handgun Ammo.
    (Except your starting weapon and it's upgrades, and the G18 Handgun)"""
    display_name = "Oops! All Handguns"
    option_false = 0
    option_true = 1
    default = 0
	
class NoFirstAidSpray(Choice):
    """Enabling this swaps all first aid sprays to filler or less useful items. 
    """
    display_name = "No First Aid Spray"
    option_false = 0
    option_true = 1
    default = 0

class NoGreenHerb(Choice):
    """Enabling this swaps all green herbs to filler or less useful items. 
    """
    display_name = "No Green Herbs"
    option_false = 0
    option_true = 1
    default = 0

class NoRedHerb(Choice):
    """Enabling this swaps all red herbs to filler or less useful items. 
    """
    display_name = "No Red Herbs"
    option_false = 0
    option_true = 1
    default = 0

class NoGunpowder(Choice):
    """Enabling this swaps all gunpowder of all types to filler or less useful items. 
    """
    display_name = "No Gunpowder"
    option_false = 0
    option_true = 1
    default = 0
    
class AddDamageTraps(Choice):
    """Enabling this adds traps to your game that, when received, deal 1 health state of damage to you. e.g., if you're "Fine", first one puts you in "Caution". 
    By default, these traps cannot kill you, but the "Damage Traps Can Kill" option can make them lethal.
    """
    display_name = "Add Damage Traps"
    option_false = 0
    option_true = 1
    default = 0

class DamageTrapCount(NamedRange):
    """While the "AddDamageTraps" option is enabled, this option specifies how many of this trap should be placed.
    """
    default = 10
    range_start = 0
    range_end = 30 
    display_name = "Damage Trap Count"
    special_range_names = {
        "disabled": 0,
        "half": 15,
        "all": 30,
    }

class DamageTrapsCanKill(Choice):
    """Enabling this while "Add Damage Traps" is enabled will allow the damage traps to drop your health state below "Danger". As in, they can kill you. 
    """
    display_name = "Damage Traps Can Kill"
    option_false = 0
    option_true = 1
    default = 0

class AddParasiteTraps(Choice):
    """Enabling this adds traps that infect Jill with parasites.
    It's the same status that the Deimos can give you.
    It applies damage over time until cured like the poison status from RE2. 
    It is Jill only, Carlos cannot puke — so they're ignored while playing as Carlos.
    """
    display_name = "Add Parasite Traps"
    option_false = 0
    option_true = 1
    default = 0

class ParasiteTrapCount(NamedRange):
    """While "Add Parasite Traps" is enabled, how many of this trap to place.
    """
    default = 10
    range_start = 0
    range_end = 30
    display_name = "Parasite Trap Count"
    special_range_names = {
        "disabled": 0,
        "half": 15,
        "all": 30,
    }

class AddPukeTraps(Choice):
    """Enabling this adds traps that make Jill vomit (same animation as curing parasites).
    Mostly a nuisance, but can be disruptive during combat. 
    It is Jill only, Carlos cannot puke — so they're ignored while playing as Carlos.
    """
    display_name = "Add Puke Traps"
    option_false = 0
    option_true = 1
    default = 0

class PukeTrapCount(NamedRange):
    """While "Add Puke Traps" is enabled, how many of this trap to place.
    """
    default = 10
    range_start = 0
    range_end = 30
    display_name = "Puke Trap Count"
    special_range_names = {
        "disabled": 0,
        "half": 15,
        "all": 30,
    }

re3remake_option_groups = [
    OptionGroup("Gameplay Options", [
        Difficulty,
        AllowMissableLocations,
        AllowProgressionInNEST,
        AddFilesAsLocations,
        AddEnemyKillsAsLocations,
        EnemyKillItems,
    ]),
    OptionGroup("Enemy Options", [
        EnemyBehavior,
        SpeedyEnemyMode,
        SpeedyEnemyMultiplier,
        InvisibleEnemyMode,
    ]),
    OptionGroup("Helpful Options", [
        EarlyFireHose,
        ExtraSewerItems,
        StartingHipPouches,
        BonusStart,
    ]),
    OptionGroup("Weapon Options", [
        LocalWeapons,
        DoubleWeapons,
        AmmoPackModifier,
        OopsAllGrenades,
        OopsAllHandguns,
    ]),
    OptionGroup("Troll Options", [
        NoFirstAidSpray,
        NoGreenHerb,
        NoRedHerb,
        NoGunpowder,
    ]),
    OptionGroup("Trap Options", [
        AddDamageTraps,
        DamageTrapCount,
        DamageTrapsCanKill,
        AddParasiteTraps,
        ParasiteTrapCount,
        AddPukeTraps,
        PukeTrapCount,
    ]),
]

# making this mixin so we can keep actual game options separate from AP core options that we want enabled
# not sure why this isn't a mixin in core atm, anyways
@dataclass
class StartInventoryFromPoolMixin:
    start_inventory_from_pool: StartInventoryPool

@dataclass
class RE3ROptions(StartInventoryFromPoolMixin, DeathLinkMixin, PerGameCommonOptions):
    difficulty: Difficulty
    # unlocked_typewriters: UnlockedTypewriters
    allow_missable_locations: AllowMissableLocations
    allow_progression_in_nest: AllowProgressionInNEST
    add_files_as_locations: AddFilesAsLocations
    add_enemy_kills_as_locations: AddEnemyKillsAsLocations
    enemy_kill_items: EnemyKillItems
    enemy_behavior: EnemyBehavior
    speedy_enemy_mode: SpeedyEnemyMode
    speedy_enemy_multiplier: SpeedyEnemyMultiplier
    invisible_enemy_mode: InvisibleEnemyMode
    early_fire_hose: EarlyFireHose
    extra_sewer_items: ExtraSewerItems
    starting_hip_pouches: StartingHipPouches
    bonus_start: BonusStart
    local_weapons: LocalWeapons
    double_weapons: DoubleWeapons
    ammo_pack_modifier: AmmoPackModifier
    oops_all_grenades: OopsAllGrenades
    oops_all_handguns: OopsAllHandguns
    no_first_aid_spray: NoFirstAidSpray
    no_green_herb: NoGreenHerb
    no_red_herb: NoRedHerb
    no_gunpowder: NoGunpowder
    add_damage_traps: AddDamageTraps
    damage_trap_count: DamageTrapCount
    damage_traps_can_kill: DamageTrapsCanKill
    add_parasite_traps: AddParasiteTraps
    parasite_trap_count: ParasiteTrapCount
    add_puke_traps: AddPukeTraps
    puke_trap_count: PukeTrapCount