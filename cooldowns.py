from time import time
cooldowns = {}
async def check_for_cooldown(ctx,command_name,cooldown_time=5,is_global_cooldown=False):
    "A function that checks for cooldowns. Returns True (and replies You are on cooldown!) Otherwise, returns False and sets the user on cooldown. cooldown_time is in seconds."
    global cooldowns
    if command_name not in cooldowns.keys():
        cooldowns[command_name] = {}
    if is_global_cooldown and "_global" not in cooldowns.keys():
        cooldowns["_global"] = {}
    if is_global_cooldown:
        command_name = "_global"
    try:
        t = cooldowns[command_name][ctx.author.id] - time.time()
        if t > 0:
            await ctx.reply(f"You are on cooldown! Try again in {t} seconds.")
            return True
        else:
            cooldowns[command_name][ctx.author.id] = time.time() + cooldown_time
            return False
    except KeyError:
        cooldowns[command_name][ctx.author.id] = time.time() + cooldown_time
        return False

    