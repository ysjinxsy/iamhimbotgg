import nextcord
from nextcord.ext import commands 
from nextcord import Interaction, SelectOption, ui, TextInputStyle
from nextcord.ui import Button, View, Modal, TextInput
import aiosqlite 
import re
from nextcord.utils import utcnow 
from db import get_config, get_teams
import logging
import aiohttp
import datetime
from shared import guild_id
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.StreamHandler()          # Log to console
    ]
)

intents = nextcord.Intents.all()
guild_id = 1221092843288920065
client = commands.Bot(command_prefix="?", intents=intents)
DATABASE_PATH = "database.db"
async def ensure_config_exists(guild_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.cursor() as cursor:
            # Check if the config for this guild_id exists
            await cursor.execute("SELECT * FROM config WHERE guild_id = ?", (guild_id,))
            config = await cursor.fetchone()
            
            # If not found, insert default values
            if config is None:
                await cursor.execute(
                    "INSERT INTO config (guild_id, manager_role_id, assistant_manager_role_id, channel_id, roster) VALUES (?, NULL, NULL, NULL, NULL)",
                    (guild_id,)
                )
                await db.commit()

@client.command(name="2ndsetupsecret")
async def setup(ctx):
    guild_id = ctx.guild.id
        
        # Ensure the config exists
    await ensure_config_exists(guild_id)
        
    await ctx.send("Configuration has been initialized for this server.")

@client.command(name="secret1412szw")
async def secret1412szw(ctx):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER, 
                    guild INTEGER
                )
            ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    roleid INTEGER, 
                    emoji TEXT, 
                    server_id INTEGER
                )
            ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    guild_id INTEGER PRIMARY KEY, 
                    manager_role_id INTEGER, 
                    assistant_manager_role_id INTEGER, 
                    channel_id INTEGER, 
                    roster TEXT
                )
            ''')
            await db.commit()
            await ctx.send("Databases Created!")
        
@client.event
async def on_ready():
    print(f'{client.user} is online and ready!')
    print(f'Bot ID: {client.user.id}')
    print(f'Bot Name: {client.user.name}')
    print(f'Bot Discriminator: {client.user.discriminator}')


class SetupView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.set_roster_button = Button(
            label="Set Roster",
            style=nextcord.ButtonStyle.primary,
            custom_id="set_roster_button_789"
        )
        self.set_roster_button.callback = self.set_roster_callback
        self.add_item(self.set_roster_button)

        # Role Select for Assistant Manager Role
        self.assistant_manager_role_select = nextcord.ui.RoleSelect(
            placeholder="Select Assistant Manager Role",
            custom_id="assistant_manager_role_select_321"
        )
        self.assistant_manager_role_select.callback = self.assistant_manager_role_select_callback
        self.add_item(self.assistant_manager_role_select)

        # Role Select for Manager Role
        self.manager_role_select = nextcord.ui.RoleSelect(
            placeholder="Select Manager Role",
            custom_id="manager_role_select_654"
        )
        self.manager_role_select.callback = self.manager_role_select_callback
        self.add_item(self.manager_role_select)

        # Channel Select
        self.channel_select = nextcord.ui.ChannelSelect(
            placeholder="Select a channel",
            custom_id="channel_select_987"
        )
        self.channel_select.callback = self.channel_select_callback
        self.add_item(self.channel_select)

    async def set_roster_callback(self, interaction: Interaction):
        modal = SetRosterModal()
        await interaction.response.send_modal(modal)

    async def assistant_manager_role_select_callback(self, interaction: Interaction):
        selected_role = self.assistant_manager_role_select.values[0]  # Get the selected role object
        role_id = selected_role.id  # Get the role ID
        print(f'{role_id}')  # Print the role ID for debugging
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "UPDATE config SET assistant_manager_role_id = ? WHERE guild_id = ?",
                    (role_id, interaction.guild.id)
                )
                await db.commit()
        
        await interaction.response.send_message(f"Assistant Manager role set to <@&{role_id}>.", ephemeral=True)

    async def manager_role_select_callback(self, interaction: Interaction):
        selected_role = self.manager_role_select.values[0]  # Get the selected role object
        role_id = selected_role.id  # Get the role ID
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "UPDATE config SET manager_role_id = ? WHERE guild_id = ?",
                    (role_id, interaction.guild.id)
                )
                await db.commit()
        
        await interaction.response.send_message(f"Manager role set to <@&{role_id}>.", ephemeral=True)

    async def channel_select_callback(self, interaction: Interaction):
        selected_channel = self.channel_select.values[0]  # Get the selected channel object
        channel_id = selected_channel.id  # Get the channel ID
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "UPDATE config SET channel_id = ? WHERE guild_id = ?",
                    (channel_id, interaction.guild.id)
                )
                await db.commit()
        
        await interaction.response.send_message(f"Channel set to <#{channel_id}>.", ephemeral=True)

# Define the SetRosterModal class
class SetRosterModal(Modal):
    def __init__(self):
        super().__init__("Set Roster Modal")
        self.roster_input = TextInput(
            label="Enter Roster",
            style=TextInputStyle.paragraph,
            placeholder="Type the roster here...",
            required=True,
            max_length=2000
        )
        self.add_item(self.roster_input)

    async def callback(self, interaction: Interaction):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "UPDATE config SET roster = ? WHERE guild_id = ?",
                    (self.roster_input.value, interaction.guild.id)
                )
                await db.commit()
        await interaction.response.send_message(f"Roster has been set to:\n{self.roster_input.value}", ephemeral=True)

# Define the setup command
@client.slash_command(name="setup", description="Set up roles and channels for the bot.", guild_ids=[guild_id])
async def setup_command(inter: Interaction):
    view = SetupView()
    await inter.response.send_message("Please select the Assistant Manager role, Manager role, and a channel from the dropdowns below, and then set the roster if needed.", view=view, ephemeral=True)
    async def ping(ctx):
        await ctx.send("Pong!")

@client.slash_command(name="say", description="Say a text",guild_ids=[guild_id])
async def say(inter: nextcord.Interaction, text: str):
    await inter.response.send_message('Message Sent', ephemeral=True)
    await inter.channel.send(text)

@client.slash_command(name="ban", description="ban a member",guild_ids=[guild_id])
async def ban(inter: nextcord.Interaction, member: nextcord.Member, reason: str = None):
    await member.ban(reason=reason)
    await inter.response.send_message(f"Banned {member} for reason: {reason}")
@client.slash_command(name="customize", description="Customize the bot's profile picture and banner.",guild_ids=[guild_id])
async def customize(inter: Interaction, profile_picture_url: str = None, banner_url: str = None):
    if not inter.user.guild_permissions.administrator:
        await inter.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if profile_picture_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(profile_picture_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        await inter.client.user.edit(avatar=image_data)
                        await inter.response.send_message("Profile picture updated successfully.", ephemeral=True)
                    else:
                        await inter.response.send_message("Failed to fetch the profile picture from the URL.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"An error occurred: {e}", ephemeral=True)

    if banner_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(banner_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        # Note: Updating the bot's banner is not supported through the Discord API
                        # Therefore, this part of the code is omitted. 
                        await inter.response.send_message("Banner update is not supported by the API.", ephemeral=True)
                    else:
                        await inter.response.send_message("Failed to fetch the banner from the URL.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"An error occurred: {e}", ephemeral=True)


@client.slash_command(name="kick", description="kick a member",guild_ids=[guild_id])
async def kick(inter: nextcord.Interaction, member: nextcord.Member, reason: str = None):
    await member.kick(reason=reason)
    await inter.response.send_message(f"Kicked {member} for reason: {reason}")

@client.slash_command(name="mute", description="Mute a user",guild_ids=[guild_id])
async def mute(interaction: nextcord.Interaction, member: nextcord.Member):
    muted_role = nextcord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        await interaction.response.send_message("Muted role not found.")
        return
    await member.add_roles(muted_role)
    await interaction.response.send_message(f"Muted {member}.")

@client.slash_command(name="lock", description="Lock a channel",guild_ids=[guild_id])
@commands.has_permissions(manage_channels=True)
async def lock(interaction: nextcord.Interaction):
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f"Channel {channel.mention} has been locked.")

@client.slash_command(name="unlock", description="Unlock a channel",guild_ids=[guild_id])
@commands.has_permissions(manage_channels=True)
async def unlock(interaction: nextcord.Interaction):
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message(f"Channel {channel.mention} has been unlocked.")

@client.slash_command(name="server_info", description="info about server",guild_ids=[guild_id])
async def server_info(inter: nextcord.Interaction):
    guild = inter.guild
    embed = nextcord.Embed(title=f"Server Info: {guild.name}", description=guild.description)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    await inter.response.send_message(embed=embed)

@client.slash_command(name="botinfo", description="Displays information about the bot.",guild_ids=[guild_id])
async def bot_info(inter: nextcord.Interaction):
    embed = nextcord.Embed(title="Bot Information")
    embed.add_field(name="Bot Name", value=client.user.name)
    embed.add_field(name="Bot ID", value=client.user.id)
    await inter.response.send_message(embed=embed)

@client.slash_command(name="addteam", description="Add a team with its role and emoji.",guild_ids=[guild_id])
async def add_team(inter: nextcord.Interaction, role: nextcord.Role, emoji: str):
    async with aiosqlite.connect("database.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('INSERT INTO teams (roleid, emoji,server_id) VALUES (?, ?, ?)', (role.id, emoji, guild_id))
            await db.commit()
    await inter.response.send_message(f"Added team with role {role.name} and emoji {emoji}.")

@client.slash_command(name="removeteam", description="Remove a team by its role.", guild_ids=[guild_id])
async def remove_team(inter: nextcord.Interaction, role: nextcord.Role):
    async with aiosqlite.connect("database.db") as db:
        async with db.cursor() as cursor:
            # Check if the team exists
            await cursor.execute('SELECT roleid FROM teams WHERE roleid = ? AND server_id = ?', (role.id, str(inter.guild.id)))
            team = await cursor.fetchone()

            if team:
                # Delete the team from the database
                await cursor.execute('DELETE FROM teams WHERE roleid = ? AND server_id = ?', (role.id, str(inter.guild.id)))
                await db.commit()
                await inter.response.send_message(f"Removed team with role {role.name}.")
            else:
                await inter.response.send_message("Team not found.")

@client.slash_command(name="view_team", description="View all teams with their emojis and roles.", guild_ids=[guild_id])
async def view_team(inter: nextcord.Interaction):
    async with aiosqlite.connect("database.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT roleid, emoji FROM teams WHERE server_id = ?', (str(inter.guild.id),))
            teams = await cursor.fetchall()

    embed = nextcord.Embed(title="Teams")
    for roleid, emoji in teams:
        role = inter.guild.get_role(roleid)
        if role:
            embed.add_field(name=role.name, value=emoji)
        else:
            embed.add_field(name=f"Unknown Role ({roleid})", value=emoji)
    
    await inter.response.send_message(embed=embed)


@client.slash_command(name="release", description="Release a player from your team", guild_ids=[guild_id])
async def release(interaction: Interaction, player: nextcord.Member):
    server_id = interaction.guild.id  # Get the server ID
    user = interaction.user
    print(f"Server ID: {server_id}")
    server_name = interaction.guild.name
    server_icon_url = interaction.guild.icon.url

    config = await get_config(server_id)  # Fetch the config for this server
    print(f"Config: {config}")

    if config is None:
        await interaction.response.send_message("No configuration found for this server.", ephemeral=True)
        return

    manager_role_id = config.get('manager_role_id')
    assistant_manager_role_id = config.get('assistant_manager_role_id')
    roster = config.get('roster')

    # Check if the user has the manager or assistant manager role
    user_roles = [role.id for role in interaction.user.roles]
    print(f"User Roles: {user_roles}")

    if manager_role_id not in user_roles or assistant_manager_role_id not in user_roles:
        await interaction.response.send_message("You don't have the required roles to perform this action.", ephemeral=True)
        return

    # Get teams and find the team role id
    teams = await get_teams(server_id)
    print(f"Teams: {teams}")

    user_team_role_id = None
    team_emoji = None

    # Check if the interaction user has a team role
    for team in teams:
        if team[0] in user_roles:  # Check if user has the team role
            user_team_role_id = team[0]
            team_emoji = team[1]
            print(user_team_role_id,team_emoji)
            break

    if user_team_role_id is None:
        await interaction.response.send_message("You don't have a team role that matches the player’s team role!", ephemeral=True)
        return

    # Check if the player has the same team role
    player_team_role_ids = [role.id for role in player.roles]
    if user_team_role_id not in player_team_role_ids:
        await interaction.response.send_message(f"{player.mention} is not signed to your team or team not found!", ephemeral=True)
        return

    # Remove the team role from the player
    team_role = interaction.guild.get_role(user_team_role_id)
    if team_role:
        await player.remove_roles(team_role)
        members_with_role = team_role.members
        # Count the number of members
        count = len(members_with_role)
        role_color = team_role.color
    
    # Convert color to hex string
    def get_emoji_image_url(team_emoji):
        # Check if it's a Unicode emoji
        if team_emoji.startswith('<:') or team_emoji.startswith('<a:'):
            # Extract the emoji ID from custom emoji format
            emoji_id = team_emoji.split(':')[2].strip('>')
            return f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        else:
            # Handle Unicode emojis (not using an image URL)
            return None

    farewell_channel_id = config.get('channel_id')
    print(f"Farewell channel ID: {farewell_channel_id}")

    farewell_channel = interaction.guild.get_channel(farewell_channel_id)
    if farewell_channel:
        await interaction.response.send_message(f"{player.name} got released from your team.")
    else:
        print(f"Channel with ID {farewell_channel_id} not found.")


    embed = nextcord.Embed(title="Release",
                        description=f"{team_emoji} {team_role.mention} Have released {player.mention} ``{player.name}``\n\n<:file:1271976313456033896> **Roster:** {count}/{roster}\n<:manager:1271976436307066931> **Coach:** <@&{manager_role_id}> <@{user.id}> ``{user.name}``",
                        colour=role_color,
                        timestamp=datetime.now())

    embed.set_author(name=f"{server_name} Transactions",
                    icon_url=f"{server_icon_url}")

    embed.set_thumbnail(url=get_emoji_image_url(team_emoji))

    embed.set_footer(text=f"{user.name}",
                    icon_url=f"{user.avatar.url}")
    await farewell_channel.send(embed=embed)


@client.slash_command(name="sign", description="Send a player a contract.", guild_ids=[guild_id])
async def sign(interaction: nextcord.Interaction, player: nextcord.Member):
    guild_id = interaction.guild.id
    server_name = interaction.guild.name
    server_icon_url = interaction.guild.icon.url
    user = interaction.user
    server_id = interaction.guild.id

    # Fetch config data from the database
    config = await get_config(guild_id)
    if not config:
        await interaction.response.send_message("No teams have been set up yet.", ephemeral=True)
        return

    # Retrieve data from config
    manager_id = config['manager_role_id']
    assistant_manager_role_id = config['assistant_manager_role_id']
    channel_id = config['channel_id']

    # Convert max_roster to integer
    try:
        max_roster = int(config['roster'])
    except ValueError:
        await interaction.response.send_message("Invalid roster limit configured.", ephemeral=True)
        return

    # Check if the command user has the necessary permissions
    user_roles = [role.id for role in interaction.user.roles]
    if interaction.user.id != manager_id or assistant_manager_role_id not in user_roles:
        await interaction.response.send_message("Only the team manager or assistant manager can use this command.", ephemeral=True)
        return

    # Fetch teams data from the database using the guild_id
    teams = await get_teams(guild_id)
    if not teams:
        await interaction.response.send_message("No teams have been set up yet.", ephemeral=True)
        return

    # Check if user has a team role
    user_team_role_id = None
    team_emoji = None

    for team in teams:
        if len(team) >= 2:  # Ensure there are at least 2 elements in the tuple
            if team[0] in user_roles:  # Check if the interaction user has the team role
                user_team_role_id = team[0]
                team_emoji = team[1]
                break
        else:
            print("Team tuple does not have enough elements:", team)

    if user_team_role_id is None:
        await interaction.response.send_message("You do not have a valid team role.", ephemeral=True)
        return

    # Find the team info for the user's team role
    team_info = next((team for team in teams if team[0] == user_team_role_id), None)
    if not team_info:
        await interaction.response.send_message("Team data is incomplete or role does not match.", ephemeral=True)
        return

    team_role_id, emoji = team_info
    team_role = interaction.guild.get_role(team_role_id)

    updates_channel = client.get_channel(channel_id)

    if not team_role or not updates_channel:
        await interaction.response.send_message("Team data is incomplete or channel not found.", ephemeral=True)
        return

    if team_role in player.roles:
        await interaction.response.send_message("This player is already signed to a team.", ephemeral=True)
        return

    # Check if the roster is full
    current_roster = len(team_role.members)
    if current_roster >= max_roster:
        await interaction.response.send_message("The team's roster is full.", ephemeral=True)
        return
    
    def get_emoji_image_url(team_emoji):
        # Check if it's a Unicode emoji
        if team_emoji.startswith('<:') or team_emoji.startswith('<a:'):
            # Extract the emoji ID from custom emoji format
            emoji_id = team_emoji.split(':')[2].strip('>')
            return f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        else:
            # Handle Unicode emojis (not using an image URL)
            return None

    username_with_discriminator = f"{player.name}#{player.discriminator}"

    # Create the embed as before
    offer_embed = nextcord.Embed(title="Franchise Signing",
                        description=f"You have been signed by the {team_emoji} {team_role.name} and have joined their franchise, do you accept? \n\n<:manager:1271976436307066931> **Coach:**<@{interaction.user.id}>**{interaction.user}**",
                        colour=team_role.color)

    offer_embed.set_author(name=f"{interaction.guild.name} Transactions",
                    icon_url=server_icon_url)

    offer_embed.set_thumbnail(url=get_emoji_image_url(team_emoji))

    offer_embed.set_footer(text=f"{user.name}",
                    icon_url=f"{user.avatar.url}")

    # Define the buttons
    accept_button = Button(label="Accept", style=nextcord.ButtonStyle.success)
    decline_button = Button(label="Decline", style=nextcord.ButtonStyle.danger)

    # Define the view with the buttons
    view = View(timeout=86400)  # Timeout for the view (24 hours)

    # Add buttons to the view
    view.add_item(accept_button)
    view.add_item(decline_button)

    async def accept_callback(interaction: nextcord.Interaction):
        await player.add_roles(team_role)
        accept_embed = nextcord.Embed(
            title="Contract Signed!",
            description=f"You have joined **{team_role.name}**!",
            color=team_role.color
        )
        await interaction.response.edit_message(embed=accept_embed, view=None)  # Update the original message

        update_embed = nextcord.Embed(title="Offer Accepted",
                            description=f"{player.mention} `{username_with_discriminator}` has **accepted** the offer to\n{team_emoji} {team_role.mention}\n\n<:file:1271976313456033896> **Roster:** {len(team_role.members)}/{max_roster}\n<:manager:1271976436307066931> **Coach:** <@&{manager_id}> <@{user.id}> `{user.name}`",
                            colour=team_role.color,
                            timestamp=datetime.now())

        update_embed.set_author(name=f"{server_name} Transactions",
                        icon_url=f"{server_icon_url}")

        update_embed.set_thumbnail(url=get_emoji_image_url(team_emoji))

        update_embed.set_footer(text=f"{user.name}",
                        icon_url=f"{user.avatar.url}")

        await updates_channel.send(embed=update_embed)

    async def decline_callback(interaction: nextcord.Interaction):
        decline_embed = nextcord.Embed(
            title="Contract Declined",
            description=f"You have declined the offer from **{team_role.name}**.",
            color=nextcord.Color.red()
        )
        await interaction.response.edit_message(embed=decline_embed, view=None)  # Update the original message

        update_embed = nextcord.Embed(title="Offer Declined",
                            description=f"{player.mention} `{username_with_discriminator}` has **declined** the offer to\n{team_emoji} {team_role.mention}\n\n<:file:1271976313456033896> **Roster:** {len(team_role.members)}/{max_roster}\n<:manager:1271976436307066931> **Coach:** <@&{manager_id}> <@{user.id}> `{user.name}`",
                            colour=team_role.color,
                            timestamp=datetime.now())

        update_embed.set_author(name=f"{server_name} Transactions",
                        icon_url=f"{server_icon_url}")

        update_embed.set_thumbnail(url=get_emoji_image_url(team_emoji))

        update_embed.set_footer(text=f"{user.name}",
                        icon_url=f"{user.avatar.url}")
        await updates_channel.send(embed=update_embed)

    # Assign callbacks to buttons
    accept_button.callback = accept_callback
    decline_button.callback = decline_callback

    # Send the offer embed to the player with the buttons
    await player.send(embed=offer_embed, view=view)

    # Acknowledge the command in the server
    await interaction.response.send_message(f"Sent offer to {player.mention}", ephemeral=True)
