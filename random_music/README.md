# ED8 Music Randomizer
A script to quickly randomize music tracks, based on a list of options.  Comes with a template (made for Trails into Reverie) - replace with your own options!

## Credits:
I am very grateful to Lukas Himbert's [tbled editor](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md), for both t_bgm.tbl schemas and just for it being a very handy tool that I used extensively in writing this script, thank you!

## Requirements:
1. Python 3.9 and newer is required for use of these scripts.  It is free from the Microsoft Store, for Windows users.  For Linux users, please consult your distro.

## CS1 / CS2 / CS3 / CS4 / Reverie

### Usage:
1. *Randomizing:*

Place t_bgm_randomize.py in *{Trails of Cold Steel folder}*/data/text/dat_en along with t_bgm_options.json, and execute t_bgm_randomize.py.  It will replace the tracks that you indicate with one of the options you put in t_bgm_options.json.

*Note: This has only been tested with Trails into Reverie.  But it should work with other games.  The sample .json file was made for The Reverie Corridor; it is only a sample and you will need to make your own list of songs.*

2. *Making your own list:*

The t_bgm_options.json file is a list of entries that you want to randomize.  Here is a sample entry:

```
    {
        "name": "TRC Lobby",
        "id": 100,
        "options": [
            "ed81009",
            "ed8150",
            "ed8151"
        ]
    },
```

- `"name"` - Give your entry a name so you can find it later.  *This is NOT used by the script at all.  It is only for your reference!*
- `"id"` - This number should be the row you want to change.  For example, id 100 is the music to the Reverie Corridor lobby.
- `"options"` - This is a list of tracks that the randomizer should choose from for this row.

3. *Figuring out the id numbers*

There are several ways to do this, none of them are very easy.  The second method is by far my favorite.

- Go into {Trails}/data/bgm/opus and play every track until you find the track you want.  Open t_bgm.tbl in [tbled](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md), and look up the id number corresponding to that track.
- Download [Process Explorer from Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer) and run it.  Set the lower pane view to Handles.  Get the game to play the bgm track you want to replace.  Select the game process in Process Explorer, and look at the files that are open by the game in the lower pane (Scroll through the "Types" until you get to "Files").  The current track should be shown in the window.  Open t_bgm.tbl in [tbled](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md), and look up the id number corresponding to that track.
- Decompile the scena script for the map or battle you want to change the music to.  Find the OP code that loads the track you want, and note which `id` it is calling.  (I find this method very unreliable, I recommend Process Explorer instead!)