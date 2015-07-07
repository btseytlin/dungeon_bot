# The Idea

A dungeon crawling bot for telegram
The bot should be a simple dungeon crawling DnD-style game players can play alone or with friends.

Registering and characters

A player first creates a character throught a conversation with the bot that starts with `/register` command. Race, Class and Stats, character name can be customized. There is one character per player, characters are persisted in a serverside database.

Dungeons(Lobbies)

After that the player can join a new dungeon crawl either alone or by joining an existing one.

The player can use `/dungeon` command without arguments to join a singleplayer dungeon. `/dungeon x` creates a lobby for X players for a dungeon crawl. Every player that calls `/dungeon` in the same conversation after that will be added to the lobby. It's also possible to join a dungeon by a dungeon's id (printed after/dungeon xexecution, will be likedungeon#123). Calling `/dungeon dungeon#123` allows to join a dungeon by id, allowing to play with people outside of current conversation. That is only allowed in PM with the bot.

Dungeon crawling

The game itself begins with the players entering a dungeon. Then `N` rooms are generated. Each room has either loose loot, enemies or riddle. Players proceed throught each room until the last one is reached. The last room has a boss, after which the dungeon crawl ends.

The difficulty depends on the sum of player levels taking part.

Players can fight with enemies via a turn based combat system. The bot presents each player a list of commands they can call ( `/attack strike target` , `/attack throw target` , etc). A player has 5 minutes to acth is turn before the turn passes to the next player.

Combat consists of dice rolls mostly.

Upon defeating enemies players get loot and experience. Loot is randomly distributed between players. Experience allows to increase stats.

Riddles are simple: the players get a question or task and have to beat it in order to continue.

A player can use '/say' command to talk to his dungeon crawling mates (if he is not in a chat room with them).

If someone is inactive for 20 turns straight he gets banished from the dungeon.

If a character dies he remains inactive until the dungeon crawl ends.

Loot doesn't get distributed to dead players.

If all chracters die the dungeon crawl ends.

Finishing a dungeon earns competition exp to everyone alive.
