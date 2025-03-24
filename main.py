try:
    import asyncio
    import logging
    from typing import Tuple, Optional
    from PIL import Image, ImageGrab
    import pydirectinput
    from ctypes import windll
    import ctypes
    import json
    import os
    from io import BytesIO
    from discord_webhook import DiscordWebhook, DiscordEmbed
    import pygetwindow as gw
    import time
    import discord
    import datetime
    from discord.ext import commands
    from discord import app_commands
except ImportError:
    os.system("pip install pillow discord-webhook pygetwindow pydirectinput pydirectinput-rgx discord")


# os.system("pip install pydirectinput-rgx")
# import tkinter as tk

user32 = windll.user32
user32.SetProcessDPIAware()

with open("settings.json", "r") as config_file:
    config = json.load(config_file)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

coords = {
    1: (820, 420),
    2: (1140, 420),
}

valid_scales = {
    1: 1,
    1.5: 1.5
}

display_scale = ctypes.windll.shcore.GetScaleFactorForDevice(0)/100
logging.info(f"Display Scale: {display_scale}x")

if display_scale not in valid_scales:
    input(f"Display Scale not supported, please use a supported display scale such as 150% or 100% (preferably)")
    exit()

is_clicking_afk_screen = False
is_clicking_character_screen = False

Pixels_var = config["Pixels"]
Webhook_var = config["Webhook"]
Bot_var = config["Bot"]
Other_var = config["Other"]

tolerance = Pixels_var.get("color_tolerance", 13)
pixel_radius = Pixels_var.get("pixel_radius", 27)
search_delay = Pixels_var.get("search_delay", 0.25)

anti_denji_random = Pixels_var.get("anti_random",False)
anti_random_debounce = Pixels_var.get("anti_random_debounce",60)
anti_random_delay  = Pixels_var.get("anti_random_delay",10)
anti_random_character = Pixels_var.get("anti_random_character","Enel").lower()

auto_update_display_scale_var = Pixels_var.get("auto_update_display_scale",False)

other_clicking = Pixels_var.get("other_clicking",False)
other_clicking_delay = Pixels_var.get("other_clicking_delay",5)
anti_purchase_prompt = Pixels_var.get("anti_purchase_prompt",True)
anti_main_menu = Pixels_var.get("anti_main_menu",True)

enable_webhooks = Webhook_var.get("enable_webhooks", False)
show_full_screen = Webhook_var.get("screenshot_full_screen", False)
ping_players = Webhook_var.get("ping_players", False)
player_ids = Webhook_var.get("player_id_to_ping", [])
send_webhook_delay = Webhook_var.get("send_every_minutes", 15)
webhook_urls = Webhook_var.get("discord_webhooks", [])

enable_bot = Bot_var.get("enable_bot",False)
bot_token = Bot_var.get("bot_token","")
whitelisted_ids = Bot_var.get("whitelisted_ids",[])
command_prefixs = Bot_var.get("command_prefixs",[])

print_config = Other_var.get("print_config",True)


if print_config:
    logging.info(
        f"\nColor Tolerance: {tolerance}"
        f"\nPixel Radius: {pixel_radius}"
        f"\nSearch Delay: {search_delay}"
        f"\nAnti-Random: {anti_denji_random}"
        f"\nAnti-Random Debounce: {anti_random_debounce}"
        f"\nAnti-Random Delay: {anti_random_delay}"
        f"\nAuto-Update Display Scale: {auto_update_display_scale_var}"
        f"\nCharacter: {anti_random_character}"
        f"\nOther Clicking: {other_clicking}"
        f"\nOther Clicking Delay: {other_clicking_delay}"
        f"\nAnti-Purchase Prompt: {anti_purchase_prompt}"
        f"\nAnti-Main-Menu: {anti_main_menu}"
        f"\nEnable Webhooks: {enable_webhooks}"
        f"\nShow Full Screen: {show_full_screen}"
        f"\nPing Players: {ping_players}"
        f"\nPlayer IDs: {player_ids}"
        f"\nSend Webhook Delay (minutes): {send_webhook_delay}"
        f"\nWebhook URLs: {webhook_urls}"
        f"\nEnable Bot: {enable_bot}"
        f"\nBot Token: {bot_token}"
        f"\nWhitelisted User-IDs: {whitelisted_ids}"
        f"\nCommand Prefixs: {command_prefixs}"
    )
    
if enable_webhooks == True:
    logging.info("Webhooks enabled")
    player_ping_string = " ".join([f"<@{i}>" for i in player_ids]) if ping_players and player_ids else ""
    logging.info(f"Players to ping: '{player_ping_string}'")

last_webhook_sent = 0
webhooks_sent = 1
time_started = time.time()  
total_clicks = 0
character_clicks = 0
successful_character_clicks = 0
pixels_checked = 0
custom_bot_display_scale = False

'''class HighlightOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.update()

    def highlight_pixel(self, x: int, y: int, color="red"):
        radius = 2
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline=color)
        self.root.update()

    def clear_highlights(self):
        self.canvas.delete("all")


overlay = HighlightOverlay()'''

def get_screen_resolution():
    user32 = windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height
    
def is_target_pixel(screenshot, target_rgb: Tuple[int, int, int], px: int, py: int) -> bool:
    # logging.info(f"checking at {px},{py}")
    if 0 <= px < screenshot.width and 0 <= py < screenshot.height:
        global pixels_checked
        pixel = screenshot.getpixel((px, py))
        pixels_checked += 1
        # overlay.highlight_pixel(px/display_scale, py/display_scale)
        return all(abs(pixel[i] - target_rgb[i]) <= tolerance for i in range(3)) or pixel == (0, 255, 0)
    return False

def find_color_around(coord: Tuple[int, int], target_rgb: Tuple[int, int, int], radius: int = pixel_radius) -> Optional[Tuple[int, int]]:
    x, y = coord
    screenshot = ImageGrab.grab()
    #overlay.clear_highlights()

    for r in range(radius + 1):
        for dx, dy in [(-r, 0), (r, 0), (0, -r), (0, r)]:
            if is_target_pixel(screenshot,target_rgb,x + dx, y + dy):
                return x + dx, y + dy

    for dx in range(-radius, radius + 1):
        for dy in [-radius, radius]:
            if is_target_pixel(screenshot,target_rgb,x + dx, y + dy):
                return x + dx, y + dy
        if dx in [-radius, radius]:
            for dy in range(-radius + 1, radius):
                if is_target_pixel(screenshot,target_rgb,x + dx, y + dy):
                    return x + dx, y + dy

    return None

def send_webhook(webhook_url, embed, content, screenshot_bytes=None):
    webhook = DiscordWebhook(webhook_url, content=content)
    webhook.add_embed(embed)
    if screenshot_bytes:
        webhook.add_file(file=screenshot_bytes, filename='screenshot.png')
        embed.set_image(url="attachment://screenshot.png")

    webhook.execute()
    logging.info("Webhook message sent successfully.")

def capture_window(window_title,fullscreen_param : bool):
    try:
        if show_full_screen or fullscreen_param:
            return ImageGrab.grab()

        roblox_window = next((win for win in gw.getWindowsWithTitle(window_title)), None)
        if roblox_window and roblox_window.isActive:
            logging.info("Found Roblox Window!")
            bbox = ((roblox_window.left + 10), (roblox_window.top + 10), (roblox_window.right - 10), (roblox_window.bottom - 10))
            return ImageGrab.grab(bbox)
        
        logging.warning(f" '{window_title}' not found. Using placeholder image.")
        return Image.open(os.path.join("Images", 'placeholder.png'))
    
    except Exception as e:
        logging.error(f"Error capturing '{window_title}': {e}. Using placeholder image.")
        return Image.open(os.path.join("Images", 'placeholder.png'))
    
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {seconds:.1f}s" if hours else f"{int(minutes)}m {seconds:.1f}s"

async def webhook_spy():
    try:
        if not enable_webhooks:
            return

        global webhooks_sent, last_webhook_sent, time_started
        if webhooks_sent == 1:
            time_started = time.time()
        while True: 
            screenshot = capture_window("Roblox",False)
            screenshot_bytes = BytesIO()
            screenshot.save(screenshot_bytes, format='PNG')
            screenshot_bytes.seek(0)

            total_time = time.time() - time_started
            elapsed_total_time = format_time(total_time)
            
            screen_resolution = (lambda res: f"\n> **💻 Screen Resolution:**\n> ``{res[0]}x{res[1]}``")(get_screen_resolution())
            
            time_emoji = chr(128336 + (int(((time.time()) / 900 - 3) / 2 % 24) // 2) + 
                            (int(((time.time()) / 900 - 3) / 2 % 24) % 2 * 12))

            embed = DiscordEmbed(
                title="👁 Game Update!",
                description=f"# 🎥 Current Screen Update!\n## {webhooks_sent} Webhook Update{'s' if webhooks_sent != 1 else ''} Sent! 📤",
                color=0x000000
            )

            timetext = (
                f"> **⌛ Total Elapsed Time:**\n> ``{elapsed_total_time}``\n"
                f"> **⌚ Total Elapsed Timestamp:**\n> <t:{int(time_started)}:R> ``|`` <t:{int(time_started)}> "
            )

            if webhooks_sent > 1:
                elapsed_since_last = time.time() - last_webhook_sent
                timetext += (
                    f"\n> **⏳ Time Since Last Update:**\n> ``{format_time(elapsed_since_last)}``\n"
                    f"> **⏰ Last Updated Timestamp:**\n> <t:{int(last_webhook_sent)}:R> ``|`` <t:{int(last_webhook_sent)}> "
                )

            embed.add_embed_field(name=f"{time_emoji} __Time Information__", value=timetext, inline=True)
            embed.add_embed_field(name="😴 __Click Information__", value=f"> **🖱 Total Afk Prevention Clicks:**\n> ``{total_clicks}``\n> **❔ Total Random Prevention Clicks:**\n> ``{character_clicks}``\n> **❓ Total Successful Random Prevention Clicks:**\n> ``{successful_character_clicks}``", inline=True)
            embed.add_embed_field(name="📄 __Other Information__", value=f"> **🖥️ Display Screen Scale:**\n> ``{str(display_scale*100)}%``{screen_resolution}\n> **💽 Total Pixels Checked:**\n> ``{pixels_checked}``", inline=True)

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1121115514769514519/1330625312467320933/abalog_HD.png")
            embed.set_footer(text='Created by in_doc')
            embed.set_timestamp()

            logging.info("Sending webhook update...")

            for webhook_url in webhook_urls:
                send_webhook(webhook_url, embed, player_ping_string, screenshot_bytes.getvalue())

            webhooks_sent += 1
            last_webhook_sent = time.time()

            logging.info(f"Waiting {send_webhook_delay} minutes before sending another webhook.")
            await asyncio.sleep(send_webhook_delay*60)
            
    except Exception as e:
        logging.error(f"Error for webhooks: {e}.")

async def click_coords(x: int, y: int, antidenji: bool) -> None:
    global total_clicks
    if antidenji == False:
        logging.info(f"Clicking at coordinates: ({x}, {y})")
    else:
        if is_clicking_afk_screen == True:
            return
    try:
        x, y = round(x), round(y)
        # pydirectinput.mouseUp()
        # pydirectinput.press('k')
        pydirectinput.moveTo(x, y)

        pydirectinput.click()
        pydirectinput.click()
        await asyncio.sleep(0.1)
        pydirectinput.move(5, None)
        pydirectinput.click()
        pydirectinput.click()
        # pydirectinput.press('k')
        if antidenji == False:
            total_clicks += 1
    except Exception as e:
        logging.error(f"Error during clicking at ({x}, {y}): {e}")

async def stop_clicking_afk_screen():
    await asyncio.sleep(15)
    global is_clicking_afk_screen
    if is_clicking_afk_screen == True:
        is_clicking_afk_screen = False
    # logging.info("Stopped clicking value")

async def monitor_color(coord: Tuple[int, int], target_rgb: Tuple[int, int, int]) -> None:
    global is_clicking_afk_screen
    logging.info(f"Started monitoring color at {coord}")
    while True:
        try:
            color_coords = find_color_around(coord, target_rgb)
            if color_coords:
                logging.info(f"Target color detected at {color_coords} | {coord}")
                if is_clicking_afk_screen == False:
                    is_clicking_afk_screen = True
                logging.info(f"Afk Screen spotted, Clicking at coordinates: ({coord})")
                await click_coords(*color_coords,False)
                if is_clicking_afk_screen == True:
                    asyncio.create_task(stop_clicking_afk_screen())
            await asyncio.sleep(search_delay)
        except Exception as e:
            logging.error(f"Error monitoring color at {coord}: {e}")
            await asyncio.sleep(1)

async def anti_random():
    if not anti_denji_random:
        return

    global character_clicks, is_clicking_afk_screen, successful_character_clicks, is_clicking_character_screen, anti_random_character
    target_colors = [(0, 147, 86), (0, 201, 117)]
    coord1 = (1570, 952)

    logging.info("Anti Denji/Random character enabled.")

    while True:
        try:
            screenshot = ImageGrab.grab()
            pixel = screenshot.getpixel(coord1)
            if any(all(abs(pixel[i] - color[i]) <= tolerance for i in range(3)) for color in target_colors):
                await asyncio.sleep(anti_random_delay)
                screenshot = ImageGrab.grab()
                pixel = screenshot.getpixel(coord1)
                if any(all(abs(pixel[i] - color[i]) <= tolerance for i in range(3)) for color in target_colors):

                    character_clicks += 1
                    is_clicking_character_screen = True

                    logging.info(f"Anti-Random Clicks activated at: {coord1}")
                    pydirectinput.moveTo(*(round(coord1[0]), round(coord1[1])))
                    await asyncio.sleep(0.1)
                    pydirectinput.move(5, None)

                    if not is_clicking_afk_screen:
                        pydirectinput.click()
                    else:
                        await asyncio.sleep(1)
                        is_clicking_character_screen = False
                        continue

                    await asyncio.sleep(0.2)
                    pydirectinput.move(-300, None)
                    await asyncio.sleep(0.5)

                    if anti_random_character == "deidara":
                        if display_scale == 1.5:
                            coords = [(1463, 613), (630, 430), (730, 880)]
                        else:
                            coords = [(1577, 619), (680, 415), (794, 910)]
                    elif anti_random_character == "enel":
                        if display_scale == 1.5:
                            coords = [(923, 161), (730, 880)]
                        else:
                            coords = [(972, 126), (794, 910)]
                    else:
                        coords = []

                    for i, coord in enumerate(coords):
                        logging.info(f"Anti-Random Clicks activated at: {coord}")
                        for _ in range(3 if i == 0 else 2):
                            await click_coords(*coord, True)
                            await asyncio.sleep(0.1)
                        await asyncio.sleep(0.25)

                        if is_clicking_afk_screen:
                            await click_coords(*coord, False)
                            await asyncio.sleep(1)
                            pydirectinput.press("tab")
                            is_clicking_character_screen = False
                            await asyncio.sleep(2)
                            break

                    pydirectinput.press("tab")
                    successful_character_clicks += 1
                    is_clicking_character_screen = False
                    await asyncio.sleep(anti_random_debounce)

            await asyncio.sleep(0.3)
        except Exception as e:
            logging.error(f"Anti-Random Error: {e}")
            await asyncio.sleep(0.1)


async def other_clickings():
    if not other_clicking: 
        return
    global anti_purchase_prompt, anti_main_menu, display_scale,other_clicking_delay

    logging.info("Other clicking functions enabled.")

    app_target_colors = [(39, 41, 48), (40, 44, 52)]
    amm_target_colors = [(42, 179, 42), (64, 252, 60)]
    
    while True:
        try:
            if is_clicking_afk_screen == True or is_clicking_character_screen == True:
                await asyncio.sleep(1)
                continue

            screenshot = ImageGrab.grab()
            if anti_main_menu:
                if display_scale == 1.5:
                    amm_coords = (862, 583)
                else:
                    amm_coords = (871, 584)
                pixel = screenshot.getpixel(amm_coords)
                if any(all(abs(pixel[i] - color[i]) <= 5 for i in range(3)) for color in amm_target_colors):
                    if is_clicking_afk_screen == True or is_clicking_character_screen == True:
                        await asyncio.sleep(1)
                        continue
                    pydirectinput.moveTo(*amm_coords)
                    await click_coords(*amm_coords,True)
                    logging.info(f"Clicking at coords {amm_coords} for Main Menu.")

            await asyncio.sleep(0.1)

            if anti_purchase_prompt:
                if display_scale == 1.5:
                    app_coords = (905, 660)
                else:
                    app_coords = (921, 617)

                pixel = screenshot.getpixel(app_coords)
                if any(all(abs(pixel[i] - color[i]) <= 3 for i in range(3)) for color in app_target_colors):
                    if is_clicking_afk_screen == True or is_clicking_character_screen == True:
                        await asyncio.sleep(1)
                        continue
                    pydirectinput.press('k')
                    pydirectinput.mouseUp(button='right')
                    pydirectinput.moveTo(*app_coords)
                    await asyncio.sleep(0.1)
                    await click_coords(*app_coords,True)
                    pydirectinput.press('k')
                    logging.info(f"Clicking at coords {app_coords} for Purchase Prompt.")

            await asyncio.sleep(other_clicking_delay)
        except Exception as e:
            logging.error(f"Other clicking error: {e}")
            await asyncio.sleep(0.1)

async def auto_update_display_scale():
    global display_scale,auto_update_display_scale_var,custom_bot_display_scale
    if auto_update_display_scale_var == False:
        return
    while True:
        try:
            new_scale = ctypes.windll.shcore.GetScaleFactorForDevice(0)/100
            if display_scale != new_scale:
                if custom_bot_display_scale == False:
                    logging.info(f"Display scale has been changed from {display_scale}x to {new_scale}x.")
                    display_scale = new_scale
            elif display_scale == new_scale and custom_bot_display_scale:
                custom_bot_display_scale = False
                    
        except Exception as e:
            logging.error(f"Auto Update display Error: {e}")
        await asyncio.sleep(0.2)

async def discord_bot():
    global display_scale, command_prefixs,custom_bot_display_scale, whitelisted_ids,enable_bot, bot_token, show_full_screen, valid_scales,successful_character_clicks,pixels_checked,time_started
    if enable_bot == False or bot_token == "":
        logging.info("Discord bot is disabled or empty bot token!")
        return
    try:
        def is_authorized(ctx):
            authorized_users = [int(x) for x in whitelisted_ids]
            return ctx.author.id in authorized_users
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix=command_prefixs, intents=intents)

        @bot.event
        async def on_ready():
            logging.info(f"Logged in as {bot.user}")
            logging.info('Guilds:')
            total_members = 0
            for guild in bot.guilds:
                logging.info(guild.name)
                total_members += len(guild.members)
            logging.info(f'Total members: {total_members}')
            logging.info(f'Total guilds: {len(bot.guilds)}')
            
            synced = await bot.tree.sync()

            logging.info(f"{len(synced)} Slash commands synced")

        @bot.hybrid_command()
        @app_commands.allowed_installs(guilds=True, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @commands.cooldown(1, 5, commands.BucketType.user)
        async def screenshot(ctx):
            try:
                logging.info(f"{ctx.author.name} has used the screenshot command")
                if not is_authorized(ctx):
                    return
                screenshot = capture_window("Roblox", False)
                screenshot_bytes = BytesIO()
                screenshot.save(screenshot_bytes, format='PNG')
                screenshot_bytes.seek(0)
                total_time = time.time() - time_started
                screen_resolution = (lambda res: f"\n> **💻 Screen Resolution:**\n> ``{res[0]}x{res[1]}``")(get_screen_resolution())
                elapsed_total_time = format_time(total_time)
                
                time_emoji = chr(128336 + (int(((time.time()) / 900 - 3) / 2 % 24) // 2) + 
                                (int(((time.time()) / 900 - 3) / 2 % 24) % 2 * 12))

                embed = discord.Embed(
                    title="👁 Game Update!",
                    description="# 🎥 Current Screen Update!\n",
                    color=0x000000
                )

                timetext = (
                    f"> **⌛ Total Elapsed Time:**\n> ``{elapsed_total_time}``\n"
                    f"> **⌚ Total Elapsed Timestamp:**\n> <t:{int(time_started)}:R> ``|`` <t:{int(time_started)}> "
                )

                embed.add_field(name=f"{time_emoji} __Time Information__", value=timetext, inline=True)
                embed.add_field(name="😴 __Click Information__", value=f"> **🖱 Total Afk Prevention Clicks:**\n> ``{total_clicks}``\n> **❔ Total Random Prevention Clicks:**\n> ``{character_clicks}``\n> **❓ Total Successful Random Prevention Clicks:**\n> ``{successful_character_clicks}``", inline=True)
                embed.add_field(name="📄 __Other Information__", value=f"> **🖥️ Display Screen Scale:**\n> ``{str(display_scale*100)}%``{screen_resolution}\n> **💽 Total Pixels Checked:**\n> ``{pixels_checked}``", inline=True)

                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1121115514769514519/1330625312467320933/abalog_HD.png")
                embed.set_footer(text='Created by in_doc')
                embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
                
                file_path = "Images/screenshot.png"
                with open(file_path, "wb") as f: f.write(screenshot_bytes.getvalue())
                file = discord.File(file_path, filename="screenshot.png")
                embed.set_image(url=f"attachment://screenshot.png")
                await ctx.reply(embed=embed, file=file, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False), mention_author=False)
                os.remove(file_path)

            except Exception as ss_e:
                logging.error(f"Discord Bot Screenshot Command Error: {ss_e}")

        @bot.hybrid_command()
        @app_commands.allowed_installs(guilds=True, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @commands.cooldown(1, 5, commands.BucketType.user)
        async def change_display_scale(ctx, new_scale_display: float):
            global display_scale,custom_bot_display_scale
            try:                
                if not is_authorized(ctx):
                    return
                logging.info(f"{ctx.author.name} has used the Display Scale Command ({new_scale_display}x)")
                if new_scale_display > 20:
                    new_scale_display = new_scale_display / 100  
                if new_scale_display not in valid_scales:
                    await ctx.reply("```Scale not supported.```", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False), mention_author=False)
                else:
                    await ctx.reply(f"```Scale updated from {display_scale}x to {new_scale_display}x```", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False), mention_author=False)  
                    custom_bot_display_scale = True
                    display_scale = new_scale_display
            except Exception as ds_e:
                logging.error(f"Discord Bot Display Scale Command Error: {ds_e}")

        @bot.hybrid_command()
        @app_commands.allowed_installs(guilds=True, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @commands.cooldown(1, 5, commands.BucketType.user)
        async def ping(ctx):
            logging.info(f"{ctx.message.author} used the ping command.")
            if not is_authorized(ctx):
                return
            await ctx.reply(f'{round(bot.latency * 1000)} ms', mention_author=False)
        await bot.start(bot_token)
    except Exception as e:
        logging.error(f"Discord Bot Error: {e}")

async def main() -> None:
    width, height = get_screen_resolution()
    if width != 1920 or height != 1080:
        input("The screen resolution is not 1080p. Please change your resolution to 1920x1080! ")
        exit()
    target_rgb = (3, 201, 0)
    tasks = [monitor_color(coord, target_rgb) for coord in coords.values()]
    tasks.append(webhook_spy())
    tasks.append(anti_random())
    tasks.append(auto_update_display_scale())
    tasks.append(other_clickings())
    tasks.append(discord_bot())
    logging.info("Starting monitoring tasks")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")
