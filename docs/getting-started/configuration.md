# Configuration

Artistry can be configured from the Django admin panel. A settings instance will automatically be created when the package cog is loaded. If a settings instance doesn't exist yet, you can create one from the panel.

<!-- Decrease your zoom if you have difficulty reading the grid table. -->

+------------------------+-------------------------------------------------------------------------------------------------+
| Setting                | Details                                                                                         |
+========================+=================================================================================================+
| Spawn art channel      | The forum channel ID for generating spawn art threads in.                                       |
+------------------------+-------------------------------------------------------------------------------------------------+
| Card art channel       | The forum channel ID for generating card art threads in.                                        |
+------------------------+-------------------------------------------------------------------------------------------------+
| Emoji art channel      | The forum channel ID for generating emoji art threads in.                                       |
+------------------------+-------------------------------------------------------------------------------------------------+
| Accepted message       | The content of the message that will be sent to a user once their art gets accepted. If blank,  |
|                        | no message will be sent.                                                                        |
|                        | There are various keywords you can use to enhance your message:                                 |
|                        |                                                                                                 |
|                        | - `{user}` -- A mention of the user.                                                            |
|                        | - `{accepter}` -- A mention of the user who accepted.                                           |
|                        | - `{collectibles}` -- The plural collectible name from settings.                                |
|                        | - `{collectible}` -- The collectible name from settings.                                        |
|                        | - `{discord}` -- The Discord invite link from settings.                                         |
|                        | - `{bot}` -- The name of the bot from settings.                                                 |
|                        | - `{ball}` -- The ball's name.                                                                  |
|                        | - `{emoji}` -- The ball's emoji.                                                                |
|                        | - `{art_type}` -- The art type (spawn, card, or emoji).                                         |
+------------------------+-------------------------------------------------------------------------------------------------+
| Accepted emoji         | The reaction emoji used on a message that got accepted. If blank, no reaction will be added.    |
+------------------------+-------------------------------------------------------------------------------------------------+
| Safe thread IDs        | A list of thread IDs that will be excluded from deletion when generation occurs.                |
+------------------------+-------------------------------------------------------------------------------------------------+
