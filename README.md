# Pokemon Yellow XP Router

This is a tool that is intended to allow easy experience routing of Solo Pokemon playthroughs of Pokemon Yellow.
It keeps track of the experience and stat experience gained over the course of a run, as well as your moveset.
It also tracks your inventory, and your money.
While it will allow you to route any item usage, and any purchases, if it detects an invalid game state, it will flag events (e.g. using items you don't have, using money you don't have).
It is not intended to route the game for you, merely allow you to quickly test out ideas without requiring you replay large chunks of the game.
It assumes that a single pokemon has been injected to Pokemon Yellow as your starter, via the Universal Pokemon Randomizer, and that the pokemon will be receiving 100% of the experience over the course of the run.

**NOTE:** This is a solo project done over a couple of weekends, so there are definitely some rough edges, and while I have manually verified the accuracy with several routes myself, I cannot guarantee 100% accuracy yet.
I recommend playing through the route once after mapping it out with this tool (or even playing it alongside the tool as you map it out) to guarantee its accuracy.

## Capabilities

This tool lets you easily define and reorder all the following events that take place over the course of a run:

- Trainer Battles
- Fighting Wild Pokemon (some limitations apply)
- Rare Candies
- Using Vitamins
- Learning moves through level up
- Learning moves through TM/HM
- Picking up items/Acquiring items for free
- Purchasing items
- Using/dropping items
- Selling items

The tool tells you, for any given event:

- Solo Pokemon stats prior to the event (taking badge boosts into account)
- Solo Pokemon stats after the event (taking badge boosts into account)
- Amount of experience gained in the event
- Stats of all enemy pokemon relevant to the current event
- Which enemy pokemon you will be presented with after a mid-battle level up occurs

The tool will also restrict you from fighting the same trainer multiple times, to prevent accidents in routing that are impossible in reality.

## Limitations

This tool, however does have the following limitations:

- When routing in wild pokemon battles, a specific species/level must be chosen
- When fighting wild pokemon, the wild pokemon is assumed to have perfect IVs (instead of the random IVs it would actually have)
- Evolving the solo pokemon is not currently supported
- This tool does not tell you whether a fight is possible to win, just assumes you _do_ win the fight, and tracks the XP/stat XP you get from it
- This tool does not prevent you from selecting an impossible order of battles
- This tool does not attempt to time anything, or track movement between locations in any way
- This tool does not yet do any battle calculations
- 2 trainer classes (Juggler and Agatha) are capable of switching pokemon mid-battle, which effectively negates out this tool's ability to predict mid-battle level ups. These edge cases are ignored entirely, and up to the user to handle appropriately

## Using the tool

### Starting a new route

When starting a new route from scratch, first, select the Solo Pokemon to route from the dropdown at the top of the window. This dropdown initially contains all 151 pokemon in RBY, so it is recommended to start typing the pokemon's name in the filter input box first, then selecting from the dropdown.

**NOTE:** Any time you pick from this dropdown, or type in the filter box, the event list will reset entirely, under the assumption you are starting a new route. Make sure your current route is saved first, if needed!

Once you have selected a Solo Pokemon, select the Eevee-lution you are planning your rival to have from the final dropdown on the first row.
This will populate the route with only the minimum battles required to beat the game, with the rival fights picked appropriately for the Eevee-lution you picked.
Note that this dropdown is populated from normal routes that have been saved in a particular location ("raw_pkmn_data/min_battles", relative to main executable).
So if you have a favorite route that you'd prefer to use as the default, save that route, copy the file into that folder, and restart the program.
It will appear as a new option in the minimum battles dropdown.

### Checking important battles

One thing that's very important in routing is making sure you have the appropriate level/stats before major battles.
This can be easily checked by clicking on a particular Trainer Fight that is important.
This will show you not only the stats of your pokemon going into that fight, but also the stats, level, and moveset of all enemy pokemon for that fight.
Important battles are highlighted in gray.

### Mid-battle level ups

On the list view, the second column, "LevelUpsInto" tells you which pokemon will be *entering* the battle for a given trainer fight, when a level up occurs.
For example, against the Jolteon Rival in Silph Co., you might see the following value: "#1 kadabra, after_final_pkmn".
This indicates that you level up twice.
After you defeat Cloyster, the 3rd pokemon on his team, you level up, and the first (and only) Kadabra comes out.
After you defeat Jolteon, you level up a second time at the end of the battle.

If you were to level up against second Oddish from the Lass immediately prior to Bill's House, you would see "#2 oddish"

### Other columns

The remaining columns on the list view, "Level", "Total XP", "XP Gain", and "NextLevel" all tell you the status of your pokemon _after_ the event in question has finished.

### Saving routes

Once you have a route that you'd like to save and be able to revisit later, name it in the "Route Name" text box in the top box, then click the "Save Route" button.
This will save the current route in a json file on disk (you must have write permissions where the program is stored to save).
If you happen to save a route multiple times (or in general, save a route with the same name as one that already exists), then the older version of the route will be backed up by appending a "_#" to the end of the route, and the new version you are saving now will be saved to the name specified.
This versioning easily allows older versions of the same route to be revisited as necessary.

### Loading routes

To load a route, just select a value from the "Previous Routes" dropdown in the top box.
On selection, the route will automatically be loaded.
If your list of old routes is getting excessively long and you would like to clean it up, this can easily be done since it is all driven by files on disk.
In the folder where the executable lives, there should be a directory, "saved_routes".
Inside, you can manually delete any old routes that are no longer relevant anymore.

### Exporting routes

This tool supports some integration with RouteOne, which provides very in-depth battle calculations.
Once you have a route defined that you'd like to get battle calculations for, click the "Export to RouteOne" button in the top.
This will immediately generate the config file and route file needed to run RouteOne.
The paths of these files will be shown in a pop-up.
If RouteOne is fully configured on your machine, you click on the "Set R1 jar path" button, and navigate to the "RouteOne.jar" file on your machine.
After setting the path (the tool will remember your path between restarts), you can click the "Run RouteOne" button, and it will automatically run RouteOne on the file generated from your route.
The final output path will be displayed.in the pop-up as well.
Note that you should _always_ double-check the top of the RouteOne output, and make sure it completed without errors.

### Adding a trainer battle to your route

Now that you have the basis for the playthrough that you want to route, it's time to add in optional battles.
If you have a specific point in the route that you want to add it, select the event that occurs _after_ you want your trainer battle to be added.
Then click the "New Event" button, which will pop up a new window.
"Fight Trainer" should be the default option selected for the event type, leave it as is.
Below are two optional dropw downs that let you filter the final drop down, "Trainer Name".

"Trainer Location Filter" lets you select a particular location in the game, and will filter the entries in "Trainer Name" so that only trainers at that location appear

"Trainer Class Filter" lets you select a particular trainer class, and will also filter all the entries in "Trainer Name" appropriately.

If no valid trainers exist for the filters applied, it will say as such, and you should reset one of your filters.
Otherwise, the trainer list should now be (relatively) short.
Select trainers manually from the list to see their full team populated.
Once you have found the correct trainer, then click "Add Event".
The boxes will be colored based on comparing the speed of your pokemon to the enemy pokemon.
Green indicates you outspeed, yellow is a speed tie, and red means the enemy outspeed.

### Adding other events to your route

Additionally, by selecting other values from the drop downs, you can add other event types.
These are much simpler, however, so I will not describe them here.

### Learning moves through level-up

Most events are controlled directly by the user.
However, moves learned through level-up are controlled by the tool itself.
This allows the tool to automatically place the learn move event at the correct location, including in the middle of a battle.
This also means that any time you change your route, the timing of any level-up learn move events will be updated automatically as well.
While the tool completely controls the placement of the event, the user can select the event in question, and update the outcome of the learn move event.
By default, all level-up learn move events will learn the move if there is space (since the game forces that behavior), or chooses not to learn the move if the slots are full.
When you choose to change the behavior of a given event, it will remember your choice, even when moving around.
Note that it remembers specifically the slot it overwrites, not the move.

### Reordering/Removing Events

If the events are not in the order you desire, then select an event you'd like to move, and by clicking the "Move Up" or "Move Down" button on the bottom of the window, you can reorder events.
Similarly, if you'd like to delete an event entirely, there's a button for that as well.

### Event Warnings

The tool will notice certain "invalid" events, and in cases where an event is determined to be invalid, it will flag the event in yellow, and mark the whole run as "invalid" in the top.
The effects of the event in question will still apply, despite the error.
This allows for quick testing.

NOTE! There is one exception to this.
Any attempt to add an item to your inventory will fail, and the tool will not track it at all.
This is because the tool keeps track of only 20 spaces for your inventory, and has nowhere to put the extra item, so it does not track the item that exceeds the inventory space.

The other errors that it tracks:
- Using/Selling an item that is not in your bag
- Spending money you do not have
- Using a vitamin when past the vitamin cap

If a folder has any events in it that have a warning, it will be highlighted in yellow as well.

### Event Folders

You can also group events into folders, for easier management.
By default, there is only one folder, "Main".
You can easily just add all events into this folder and not use folders at all, if desired.
Folders can be renamed, reordered, and new folders can be created. Folders can only be deleted when they are fully empty.
In order to perform any actions on folders, you must select a folder in the list, and then use the buttons at the bottom of the screen.
Note that moving events up and down can only done within a folder.
To move an event to a new folder, select the desired event, and click the "Transfer Event" button at the bottom of the screen.
Then, from the pop-up, select the destination folder desired, and click "Update Folder".
Doing so will _always_ move the event to the very end of the destination folder.

## Final Notes

This is largely just a personal project that I thought some other people might want to play around with.
If you find any issues feel free to contact me, but I make no promises that this project will be maintainned in the future.
Use/reuse/steal any code, as you wish!
Or maybe don't, it's kinda hacky :)
