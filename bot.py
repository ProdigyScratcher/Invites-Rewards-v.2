import discord
from discord.ext import commands
from discord.ui import Button, View
import aiofiles
import os
import random

intents = discord.Intents.default()
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

user_invites = {}
invite_cache = {}

ACCOUNTS_FILE = "accounts.txt"  # File with your account list

async def get_account():
    if not os.path.exists(ACCOUNTS_FILE):
        return None
    async with aiofiles.open(ACCOUNTS_FILE, mode='r') as f:
        lines = await f.readlines()
    if not lines:
        return None
    account = random.choice(lines).strip()  # pick random account
    # remove the chosen account from the list
    lines = [line for line in lines if line.strip() != account]
    async with aiofiles.open(ACCOUNTS_FILE, mode='w') as f:
        await f.writelines(lines)
    return account

# ...existing code...

@bot.command(name="gen")
async def gen_command_text(ctx):
    view = InviteView()
    embed = discord.Embed(
        title="INVITES REWARDS V.2",
        description="""
   3 INVITES = 3 ACCOUNTS

   UNCHECKED ACCOUNTS
""",
        color=discord.Color.from_rgb(5, 5, 5)
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1396726913845690380/1398399248919429120/IMG_2055.png?ex=68853849&is=6883e6c9&hm=11a579303fed172b1106afcfbb69f8b587563f28650b9da34232344209e959e6&")
    embed.set_footer(text="FAONTOP", icon_url="https://cdn.discordapp.com/icons/YOUR_SERVER_ICON.png")
    await ctx.send(embed=embed, view=view)
import discord
from discord.ext import commands
from discord.ui import Button, View
import aiofiles
import os
import random

intents = discord.Intents.default()
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

user_invites = {}
invite_cache = {}

ACCOUNTS_FILE = "accounts.txt"  # File with your account list

async def get_account():
    if not os.path.exists(ACCOUNTS_FILE):
        return None
    async with aiofiles.open(ACCOUNTS_FILE, mode='r') as f:
        lines = await f.readlines()
    if not lines:
        return None
    account = random.choice(lines).strip()  # pick random account
    # remove the chosen account from the list
    lines = [line for line in lines if line.strip() != account]
    async with aiofiles.open(ACCOUNTS_FILE, mode='w') as f:
        await f.writelines(lines)
    return account


last_reload_channel_id = None

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🔧 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    # Register persistent view for buttons
    bot.add_view(InviteView())

    for guild in bot.guilds:
        invite_cache[guild.id] = await guild.invites()

    # If reloaded, send confirmation message in the last reload channel
    global last_reload_channel_id
    if last_reload_channel_id:
        channel = bot.get_channel(last_reload_channel_id)
        if channel:
            try:
                await channel.send("Bot is successfully reloaded")
            except Exception:
                pass
        last_reload_channel_id = None

@bot.event
async def on_member_join(member):
    invites_before = invite_cache.get(member.guild.id, [])
    invites_after = await member.guild.invites()

    for new_inv in invites_after:
        for old_inv in invites_before:
            if new_inv.code == old_inv.code and new_inv.uses > old_inv.uses:
                inviter = new_inv.inviter
                user_invites[inviter.id] = user_invites.get(inviter.id, 0) + 1
                break
    invite_cache[member.guild.id] = invites_after

class InviteView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 Claim Account", style=discord.ButtonStyle.blurple, custom_id="claim_account")
    async def claim_account(self, interaction: discord.Interaction, button: Button):
        count = user_invites.get(interaction.user.id, 0)
        if count >= 3:
            accounts = []
            for _ in range(3):
                acc = await get_account()
                if acc:
                    accounts.append(acc)
            if accounts:
                accounts_str = '\n'.join(f'`{a}`' for a in accounts)
                await interaction.user.send(f"🎉 Here are your accounts:\n{accounts_str}")
                await interaction.response.send_message(f"✅ {len(accounts)} account(s) sent to your DMs!", ephemeral=True)
                user_invites[interaction.user.id] = 0
            else:
                await interaction.response.send_message("❌ No accounts left in stock.", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"❌ You need at least **3 invites** to claim 3 accounts. You have **{count}**.",
                ephemeral=True
            )

    @discord.ui.button(label="👥 Check Invites", style=discord.ButtonStyle.green, custom_id="check_invites")
    async def check_invites(self, interaction: discord.Interaction, button: Button):
        count = user_invites.get(interaction.user.id, 0)
        await interaction.response.send_message(f"📨 You currently have **{count} invites**.", ephemeral=True)

@tree.command(name="gen", description="Open the account generation panel")
async def gen_command(interaction: discord.Interaction):
    view = InviteView()

    embed = discord.Embed(
        title="INVITES REWARDS V.2",
        description="""
   3 INVITES = 3 ACCOUNTS

   UNCHECKED ACCOUNTS
""",
        color=discord.Color.from_rgb(5, 5, 5)
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1396726913845690380/1398399248919429120/IMG_2055.png?ex=68853849&is=6883e6c9&hm=11a579303fed172b1106afcfbb69f8b587563f28650b9da34232344209e959e6&")
    embed.set_footer(text="FAONTOP", icon_url="https://cdn.discordapp.com/icons/YOUR_SERVER_ICON.png")

    await interaction.response.send_message(embed=embed, view=view)



# Role IDs
OWNER_ROLE_ID = 1396244673898483813
MANAGER_ROLE_ID = 1397284079375745185
COOWNER_ROLE_ID = 1397237990924881940
MEMBER_ROLE_ID = 1397292663547494400

@tree.command(name="invitesplus", description="[Admin] Set a user's invite count.")
@discord.app_commands.describe(user="The user to set invites for", count="The number of invites to set")
async def invites_plus(interaction: discord.Interaction, user: discord.Member, count: int):
    author = interaction.user
    author_roles = [role.id for role in author.roles] if hasattr(author, 'roles') else []


    # If member role, show not authorized message (ephemeral), except for Owner
    if MEMBER_ROLE_ID in author_roles and OWNER_ROLE_ID not in author_roles:
        await interaction.response.send_message(f"{author.mention} is not authorised to use this command.", ephemeral=True)
        return

    # Only allow Owner, Manager, Co-Owner
    allowed_roles = {OWNER_ROLE_ID, MANAGER_ROLE_ID, COOWNER_ROLE_ID}
    if not any(role_id in allowed_roles for role_id in author_roles):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    # Only allow positive numbers for count
    if not isinstance(count, int) or count < 0:
        await interaction.response.send_message("❌ Please enter a valid number for invites.", ephemeral=True)
        return

    user_invites[user.id] = count

    await interaction.response.send_message("Fake invites successfully sent!", ephemeral=True)


# /reloadb command for bot reload (restart)
@tree.command(name="reloadb", description="[Admin] Reload the bot (restart process)")
async def reloadb(interaction: discord.Interaction):
    author = interaction.user
    author_roles = [role.id for role in author.roles] if hasattr(author, 'roles') else []
    allowed_roles = {OWNER_ROLE_ID, MANAGER_ROLE_ID, COOWNER_ROLE_ID}
    if not any(role_id in allowed_roles for role_id in author_roles):
        await interaction.response.send_message("❌ You do not have permission to reload the bot.", ephemeral=True)
        return
    global last_reload_channel_id
    last_reload_channel_id = interaction.channel_id
    await interaction.response.send_message("♻️ Bot is reloading...", ephemeral=True)
    import sys, os
    os.execv(sys.executable, [sys.executable] + sys.argv)

bot.run("MTM5ODM5MjA5MzczMDI3NTM0OA.GLzD_m.ZTE1nreI-gfv0dJrzlVCtNUbYGGJpJUbpavwuk")
