"""
 * Limon Bot for Discord
 * Copyright (C) 2022 AbdurrahmanCosar
 * This software is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
 * For more information, see README.md and LICENSE
"""

from asyncio import sleep
from discord import app_commands, Interaction
from discord.ext import commands
from cogs.utils.database.fetchdata import create_inventory_data
from cogs.utils.cooldown import cooldown_for_jobs
from cogs.utils.functions import add_xp
from cogs.utils.constants import Emojis
from yaml import Loader, load
from random import choice, randint

hunts_files = open("cogs/assets/yaml_files/job_yamls/hunts.yml", "rb")
hunts = load(hunts_files, Loader=Loader)

items_file = open("cogs/assets/yaml_files/market_yamls/basic_items.yml", "rb")
market_items = load(items_file, Loader = Loader) 

class Hunting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def hunt_prey(self):
        hunt = choice(list(hunts.keys()))
        name = hunts[hunt]["name"]

        return name, hunt

    @app_commands.command(name = "hunting", description = "Go hunting!")
    @app_commands.checks.dynamic_cooldown(cooldown_for_jobs())
    async def hunting(self, interaction: Interaction):

        user = interaction.user
        inventory, collection = await create_inventory_data(self.bot, user.id)

        weapon = inventory["items"]["hunting"]
        required_ammo = market_items["hunting"][weapon]["ammo"]
        weapon["durability"] -= 4

        
        
        if weapon["custom_id"] == "trap":
            trap_count = randint(2,4)
            preyed_hunts = []

            for _ in range(trap_count):
                name, hunt = self.hunt_prey()
                preyed_hunts.append(name)
                inventory["jobs_results"]["hunts"].append(hunt)

            preyed_hunts = [f":deer: {name}\n" for name in preyed_hunts]
            first_mesage = f":mouse_trap: Av için **{trap_count}** tane kapan kuruldu!"
            message = f":mouse_trap: Kapanları kontrol ettik ve işte yakaladıklarımız:\n{preyed_hunts}"

        else:
            name, hunt = self.hunt_prey()
            first_mesage = ":bow_and_arrow: Av aranıyor.."
            message = f":bow_and_arrow: Harika! Bir {name} avladık."
            inventory["ammo"][required_ammo] -= 1
            inventory["jobs_results"]["hunts"].append(hunt)

        await add_xp(self.bot, user.id, "hunter_xp")
        await collection.replace_one({"_id": user.id}, inventory)
        await interaction.response.send_message(content = first_mesage)
        await sleep(4)
        await interaction.edit_original_response(content = message)

async def setup(bot: commands.Bot):
    await bot.add_cog(Hunting(bot))