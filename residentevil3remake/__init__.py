import re
import typing

from typing import Dict, Any, TextIO
from Utils import visualize_regions

from BaseClasses import ItemClassification, Item, Location, Region, CollectionState
from worlds.AutoWorld import World
from ..generic.Rules import set_rule
from Fill import fill_restrictive

from .Data import Data
from .Options import RE3ROptions


Data.load_data('jill', 'a')


class RE3RLocation(Location):
    def stack_names(*area_names):
        return " - ".join(area_names)
    
    def stack_names_not_victory(*area_names):
        if area_names[-1] == "Victory": return area_names[-1]

        return RE3RLocation.stack_names(*area_names)

    def is_item_allowed(item, location_data, current_item_rule):
        return current_item_rule and ('allow_item' not in location_data or item.name not in location_data['allow_item'])


class ResidentEvil3Remake(World):
    """
    'Jill, I am your father.' - Nemesis, probably
    """
    game: str = "Resident Evil 3 Remake"

    data_version = 2
    required_client_version = (0, 5, 0)
    apworld_release_version = "0.1.3" # defined to show in spoiler log

    item_id_to_name = { item['id']: item['name'] for item in Data.item_table }
    item_name_to_id = { item['name']: item['id'] for item in Data.item_table }
    item_name_to_item = { item['name']: item for item in Data.item_table }
    location_id_to_name = { loc['id']: RE3RLocation.stack_names(loc['region'], loc['name']) for loc in Data.location_table }
    location_name_to_id = { RE3RLocation.stack_names(loc['region'], loc['name']): loc['id'] for loc in Data.location_table }
    location_name_to_location = { RE3RLocation.stack_names(loc['region'], loc['name']): loc for loc in Data.location_table }
    source_locations = {} # this is used to seed the initial item pool from original items, and is indexed by player as lname:loc locations

    # de-dupe the item names for the item group name
    item_name_groups = { key: set(values) for key, values in Data.item_name_groups.items() }

    options_dataclass = RE3ROptions
    options: RE3ROptions

    def generate_early(self): # check weapon randomization before locations and items are processed, so we can swap non-randomized items as well
        # start with the normal locations per player for pool, then overwrite with weapon rando if needed
        self.source_locations[self.player] = self._get_locations_for_scenario(self._get_character(), self._get_scenario()) # id:loc combo
        self.source_locations[self.player] = { 
            RE3RLocation.stack_names(l['region'], l['name']): { **l, 'id': i } 
                for i, l in self.source_locations[self.player].items() 
        } # turn it into name:loc instead

    def create_regions(self): # and create locations
        scenario_locations = { l['id']: l for _, l in self.source_locations[self.player].items() }
        scenario_regions = self._get_region_table_for_scenario(self._get_character(), self._get_scenario())

        regions = [
            Region(region['name'], self.player, self.multiworld) 
                for region in scenario_regions
]
        added_regions = []

        for region in regions:
            if region.name in added_regions:
             print("Skipping duplicate region {}...".format(region.name))
             continue

            added_regions.append(region.name)
            region.locations = [
                RE3RLocation(self.player, RE3RLocation.stack_names_not_victory(region.name, location['name']), location['id'], region) 
                    for _, location in scenario_locations.items() if location['region'] == region.name
            ]
            region_data = [scenario_region for scenario_region in scenario_regions if scenario_region['name'] == region.name][0]
            
            for location in region.locations:
                location_data = scenario_locations[location.address]
                
                # if location has an item that should be forced there, place that. for cases where the item to place differs from the original.
                if 'force_item' in location_data and location_data['force_item']:
                    location.place_locked_item(self.create_item(location_data['force_item']))
                # if location is marked not rando'd, place its original item. 
                # if/elif here allows force_item + randomized=0, since a forced item is technically not randomized, but don't need to trigger both.
                elif 'randomized' in location_data and location_data['randomized'] == 0:
                    location.place_locked_item(self.create_item(location_data["original_item"]))
                # if location is not force_item'd or not not randomized, check for Downtown progression option and apply
                # since Downtown progression option doesn't matter for force_item'd or not randomized locations
                # we check for zone id 1 because Downtown; Sewers and beyond is able to be gotten again minus a few locations.
                elif self._format_option_text(self.options.allow_progression_downtown) == 'False' and region_data['zone_id'] == 1:
                    location.item_rule = lambda item: item.classification != ItemClassification.progression and item.classification != ItemClassification.progression_skip_balancing
                # we check for zone id 6 because Labs; progression being here is just a feelsbad.    
                elif self._format_option_text(self.options.allow_progression_in_labs) == 'False' and region_data['zone_id'] == 6:
                    location.item_rule = lambda item: item.classification != ItemClassification.progression and item.classification != ItemClassification.progression_skip_balancing
                # END

                if 'allow_item' in location_data and location_data['allow_item']:
                    current_item_rule = location.item_rule or None

                    if not current_item_rule:
                        current_item_rule = lambda x: True

                    location.item_rule = lambda item: RE3RLocation.is_item_allowed(item, location_data, current_item_rule)

                # now, set rules for the location access
                if "condition" in location_data and "items" in location_data["condition"]:
                    set_rule(location, lambda state, loc=location, loc_data=location_data: self._has_items(state, loc_data["condition"].get("items", [])))

            self.multiworld.regions.append(region)
                
        for connect in self._get_region_connection_table_for_scenario(self._get_character(), self._get_scenario()):
            # skip connecting on a one-sided connection because this should not be reachable backwards (and should be reachable otherwise)
            if 'limitation' in connect and connect['limitation'] in ['ONE_SIDED_DOOR']:
                continue

            from_name = connect['from'] if 'Menu' not in connect['from'] else 'Menu'
            to_name = connect['to'] if 'Menu' not in connect['to'] else 'Menu'

            region_from = self.multiworld.get_region(from_name, self.player)
            region_to = self.multiworld.get_region(to_name, self.player)
            ent = region_from.connect(region_to)

            if "condition" in connect and "items" in connect["condition"]:
                set_rule(ent, lambda state, en=ent, conn=connect: self._has_items(state, conn["condition"].get("items", [])))

        # Uncomment the below to see a connection of the regions (and their locations) for any scenarios you're testing.
        # visualize_regions(self.multiworld.get_region("Menu", self.player), "region_uml")

        # Place victory and set the completion condition for having victory
        self.multiworld.get_location("Victory", self.player) \
            .place_locked_item(self.create_item("Victory"))

        self.multiworld.completion_condition[self.player] = lambda state: self._has_items(state, ['Victory'])

    def create_items(self):
        scenario_locations = self.source_locations[self.player]

        pool = [
            self.create_item(item['name'] if item else None) for item in [
                self.item_name_to_item[location['original_item']] if location.get('original_item') else None
                    for _, location in scenario_locations.items()
            ]
        ]

        pool = [item for item in pool if item is not None] # some of the locations might not have an original item, so might not create an item for the pool

        # remove any already-placed items from the pool (forced items, etc.)
        for filled_location in self.multiworld.get_filled_locations(self.player):
            if filled_location.item.code and filled_location.item in pool: # not id... not address... "code"
                pool.remove(filled_location.item)

        # check the starting hip pouches option and add as precollected, removing from pool and replacing with junk
        starting_hip_pouches = int(self.options.starting_hip_pouches)

        if starting_hip_pouches > 0:
            hip_pouches = [item for item in pool if item.name == 'Hip Pouch'] # 6 total in every campaign, I think

            # if the hip pouches option exceeds the number of hip pouches in the pool, reduce it to the number in the pool
            if starting_hip_pouches > len(hip_pouches):
                starting_hip_pouches = len(hip_pouches)
                self.options.starting_hip_pouches = len(hip_pouches)

            for x in range(starting_hip_pouches):
                self.multiworld.push_precollected(hip_pouches[x]) # starting inv
                pool.remove(hip_pouches[x])

        # check infinity gauntlet option and precollect if true 
        # if self._format_option_text(self.options.infinity_gauntlet) == 'True':
            # for x in range(1): self.multiworld.push_precollected(self.create_item('Infinity Gauntlet'))

        # check the bonus start option and add some heal items and ammo packs as precollected / starting items
        if self._format_option_text(self.options.bonus_start) == 'True' and self._format_option_text(self.options.oops_all_grenades) == 'True':
            for x in range(3): self.multiworld.push_precollected(self.create_item('First Aid Spray'))
            for x in range(3): self.multiworld.push_precollected(self.create_item('Hand Grenade'))
            
        if self._format_option_text(self.options.bonus_start) == 'True' and self._format_option_text(self.options.oops_all_grenades) == 'False':
            for x in range(3): self.multiworld.push_precollected(self.create_item('First Aid Spray'))
            for x in range(4): self.multiworld.push_precollected(self.create_item('Handgun Ammo'))

        # do all the "no X" options here so we have more empty spots to use for traps, if needed
        if self._format_option_text(self.options.no_first_aid_spray) == 'True':
            pool = self._replace_pool_item_with(pool, 'First Aid Spray', 'Flash Grenade')

        if self._format_option_text(self.options.no_green_herb) == 'True':
            pool = self._replace_pool_item_with(pool, 'Green Herb', 'Flash Grenade')

        if self._format_option_text(self.options.no_red_herb) == 'True':
            pool = self._replace_pool_item_with(pool, 'Red Herb', 'Flash Grenade')
        
        if self._format_option_text(self.options.no_gunpowder) == 'True':
            replaceables = set(item.name for item in pool if 'Gunpowder' in item.name or 'Explosive' in item.name)
            less_useful_items = set(
                item.name for item in pool 
                    if item.name == 'Flash Grenade' or 'Herb' in item.name
            )

            for from_item in replaceables:
                to_item = self.random.choice(list(less_useful_items))
                pool = self._replace_pool_item_with(pool, from_item, to_item)

        # figure out which traps are enabled, then swap them in for low-priority items
        # do this before the "oops all X" options so we can make use of extra Handgun Ammo spots before they get replaced out
        traps = []

        if self._format_option_text(self.options.add_damage_traps) == 'True':
            for x in range(int(self.options.damage_trap_count)):
                traps.append(self.create_item("Damage Trap"))
                
        # if self._format_option_text(self.options.add_parasite_traps) == 'True':
            # for x in range(int(self.options.parasite_trap_count)):
                # traps.append(self.create_item("Parasite Trap"))
                
        # if self._format_option_text(self.options.add_puke_traps) == 'True':
            # for x in range(int(self.options.puke_trap_count)):
                # traps.append(self.create_item("Puke Trap"))
                
        if len(traps) > 0:
            # use these spots for replacement first, since they're entirely non-essential
            available_spots = [
                item for item in pool 
                    if 'Explosive' in item.name or 'Gunpowder' in item.name
            ]
            self.random.shuffle(available_spots)

            # use these spots for replacement next, since they're lower priority
            extra_spots = [
                item for item in pool 
                    if 'Herb' in item.name or 'Ammo' in item.name or 'Rounds' in item.name or 'Grenade' in item.name
            ]
            self.random.shuffle(extra_spots)
               
            for spot in available_spots:
                if len(traps) == 0: break

                trap_to_place = traps.pop()
                pool.remove(spot)
                pool.append(trap_to_place)
                
            for spot in extra_spots:
                if len(traps) == 0: break

                trap_to_place = traps.pop()
                pool.remove(spot)
                pool.append(trap_to_place)
				
	# Add option for early/extras for Downtown items or Sewer Stuff, if configured
        # doing this before "oops all X" to make use of extra Handgun Ammo spots, too
        if self._format_option_text(self.options.early_fire_hose) == 'True':
            early_items = {}  
            early_items["Fire Hose"] = len([i for i in pool if i.name == "Fire Hose"])     

            for item_name, item_qty in early_items.items():
                if item_qty > 0:
                    self.multiworld.early_items[self.player][item_name] = item_qty

        if self._format_option_text(self.options.extra_sewer_items) == 'True':
            replaceables = [item for item in pool if item.name == 'Green Herb' or item.name == 'Handgun Ammo']
            
            for x in range(2):
                pool.remove(replaceables[x])

            pool.append(self.create_item('Battery Pack'))
            pool.append(self.create_item('Kendo Gate Key'))

        # check the "Oops! All Grenades" option. From the option description:
        #     Enabling this swaps all weapons, weapon ammo, and subweapons to Grenades. 
        #     (Except progression weapons, of course.)
        if self._format_option_text(self.options.oops_all_grenades) == 'True':
            items_to_replace = [
                item for item in self.item_name_to_item.values() 
                if 'type' in item and item['type'] in ['Weapon', 'Ammo', 'Crafting']
            ]
            to_item_name = 'Hand Grenade'

            for from_item in items_to_replace:
                pool = self._replace_pool_item_with(pool, from_item['name'], to_item_name)
                
        # check the "Oops! All Handguns" option. From the option description:
        #     Enabling this swaps all weapons, weapon ammo, and subweapons to Handgun Ammo. 
        #     (Except handguns, of course.)
                
        if self._format_option_text(self.options.oops_all_handguns) == 'True':
            items_to_replace = [
                item for item in self.item_name_to_item.values() 
                if 'type' in item and item['type'] in ['Weapon', 'Subweapon', 'Ammo', 'Crafting'] and item['name'] != 'G18'
            ]
            to_item_name = 'Handgun Ammo'

            for from_item in items_to_replace:
                pool = self._replace_pool_item_with(pool, from_item['name'], to_item_name)

        # if the number of unfilled locations exceeds the count of the pool, fill the remainder of the pool with extra maybe helpful items
        missing_item_count = len(self.multiworld.get_unfilled_locations(self.player)) - len(pool)

        if missing_item_count > 0:
            for x in range(missing_item_count):
                pool.append(self.create_item('Flash Grenade'))

        self.multiworld.itempool += pool
            
    def create_item(self, item_name: str) -> Item:
        if not item_name: return

        item = self.item_name_to_item[item_name]

        if item.get('progression', False):
            classification = ItemClassification.progression
        elif item.get('type', None) not in ['Trap']:
            classification = ItemClassification.useful
        elif item.get('type', None) == 'Trap':
            classification = ItemClassification.trap
        else: # it's Filler
            classification = ItemClassification.filler

        return Item(item['name'], classification, item['id'], player=self.player)

    def get_filler_item_name(self) -> str:
        return "Flash Grenade"

    def fill_slot_data(self) -> Dict[str, Any]:
        slot_data = {
            "character": self._get_character(),
            "scenario": self._get_scenario(),
            "difficulty": self._get_difficulty(),
            "unlocked_typewriters": self._format_option_text(self.options.unlocked_typewriters).split(", "),
            "damage_traps_can_kill": self._format_option_text(self.options.damage_traps_can_kill) == 'True',
            "death_link": self._format_option_text(self.options.death_link) == 'Yes' # why is this yes? lol
        }

        return slot_data
    
    def write_spoiler_header(self, spoiler_handle: TextIO):
        spoiler_handle.write(f"RE3R_AP_World version: {self.apworld_release_version}\n")
        # print (self._output_items_and_locations_as_text()) - For printing item locations out during generation of a seed.

    def _has_items(self, state: CollectionState, item_names: list) -> bool:
        # if it requires all unique items, just do a state has all
        if len(set(item_names)) == len(item_names):
            return state.has_all(item_names, self.player)
        # else, it requires some duplicates, so let's group them up and do some has w/ counts
        else:
            item_counts = {
                item_name: len([i for i in item_names if i == item_name]) for item_name in item_names # e.g., { Spare Key: 2 }
            }

            for item_name, count in item_counts.items():
                if not state.has(item_name, self.player, count):
                    return False
                
            return True

    def _format_option_text(self, option) -> str:
        return re.sub('\w+\(', '', str(option)).rstrip(')')
    
    def _get_locations_for_scenario(self, character, scenario) -> dict:
        locations_pool = {
            loc['id']: loc for _, loc in self.location_name_to_location.items()
                if loc['character'] == character and loc['scenario'] == scenario
        }
        
        if self._format_option_text(self.options.difficulty) == 'Inferno':
            locations_pool = { id: loc for id, loc in locations_pool.items() if loc['difficulty'] != 'hardcore' and loc['difficulty'] != 'nightmare'}

            for inferno_loc in [loc for loc in locations_pool.values() if loc['difficulty'] == 'inferno']:
                check_loc_region = re.sub('I\)$', ')', inferno_loc['region']) # take the Inferno off the region name
                check_loc_name = inferno_loc['name']

                # if there's a location with matching name and region, remove it
                matching_locs = [id for id, loc in locations_pool.items() if loc['region'] == check_loc_region and loc['name'] == check_loc_name and loc['difficulty'] != 'inferno']

                if len(matching_locs) > 0:
                    del locations_pool[matching_locs[0]]

        elif self._format_option_text(self.options.difficulty) == 'Nightmare':
            locations_pool = { id: loc for id, loc in locations_pool.items() if loc['difficulty'] != 'hardcore' and loc['difficulty'] != 'inferno'}

            for nightmare_loc in [loc for loc in locations_pool.values() if loc['difficulty'] == 'nightmare']:
                check_loc_region = re.sub('N\)$', ')', nightmare_loc['region']) # take the Nightmare off the region name
                check_loc_name = nightmare_loc['name']

                # if there's a location with matching name and region, remove it
                matching_locs = [id for id, loc in locations_pool.items() if loc['region'] == check_loc_region and loc['name'] == check_loc_name and loc['difficulty'] != 'nightmare']

                if len(matching_locs) > 0:
                    del locations_pool[matching_locs[0]]
                        
        elif self._format_option_text(self.options.difficulty) == 'Hardcore':
            locations_pool = { id: loc for id, loc in locations_pool.items() if loc['difficulty'] != 'nightmare' and loc['difficulty'] != 'inferno'}

            for hardcore_loc in [loc for loc in locations_pool.values() if loc['difficulty'] == 'hardcore']:
                check_loc_region = re.sub('H\)$', ')', hardcore_loc['region']) # take the Hardcore off the region name
                check_loc_name = hardcore_loc['name']

                # if there's a location with matching name and region, remove it
                matching_locs = [id for id, loc in locations_pool.items() if loc['region'] == check_loc_region and loc['name'] == check_loc_name and loc['difficulty'] != 'hardcore']

                if len(matching_locs) > 0:
                    del locations_pool[matching_locs[0]]

        # else, the player is still playing standard, take out all of the matching difficulty locations
        else:
            locations_pool = {
                id: loc for id, loc in locations_pool.items() if loc['difficulty'] != 'hardcore' and loc['difficulty'] != 'nightmare' and loc['difficulty'] != 'inferno'
            }
     
        # now that we've factored in swaps, remove any locations that were just there for removing unused standard ones
        locations_pool = { id: loc for id, loc in locations_pool.items() if 'remove' not in loc }
        
        return locations_pool

    def _get_region_table_for_scenario(self, character, scenario) -> list:
        return [
            region for region in Data.region_table 
                if region['character'] == character and region['scenario'] == scenario
        ]
    
    def _get_region_connection_table_for_scenario(self, character, scenario) -> list:
        return [
            conn for conn in Data.region_connections_table
                if conn['character'] == character and conn['scenario'] == scenario
        ]
    
    def _get_character(self) -> str:
        return self._format_option_text(self.options.character).lower()
    
    def _get_scenario(self) -> str:
        return self._format_option_text(self.options.scenario).lower()
    
    def _get_difficulty(self) -> str:
        return self._format_option_text(self.options.difficulty).lower()
    
    def _replace_pool_item_with(self, pool, from_item_name, to_item_name) -> list:
        items_to_remove = [item for item in pool if item.name == from_item_name]
        count_of_new_items = len(items_to_remove)

        for item in items_to_remove:
            pool.remove(item)

        for x in range(count_of_new_items):
            pool.append(self.create_item(to_item_name))

        return pool

    # def _output_items_and_locations_as_text(self):
    #     my_locations = [
    #         {
    #             'id': loc.address,
    #             'name': loc.name,
    #             'original_item': self.location_name_to_location[loc.name]['original_item'] if loc.name != "Victory" else "(Game Complete)"
    #         } for loc in self.multiworld.get_locations() if loc.player == self.player
    #     ]

    #     my_locations = set([
    #         "{} | {} | {}".format(loc['id'], loc['name'], loc['original_item'])
    #         for loc in my_locations
    #     ])
        
    #     my_items = [
    #         {
    #             'id': item.code,
    #             'name': item.name
    #         } for item in self.multiworld.get_items() if item.player == self.player
    #     ]

    #     my_items = set([
    #         "{} | {}".format(item['id'], item['name'])
    #         for item in my_items
    #     ])

    #     print("\n".join(sorted(my_locations)))
    #     print("\n".join(sorted(my_items)))

    #     raise BaseException("Done with debug output.")
