
#Written by @rf20008
# Licensed under the GNU license
# Feel free to contribute! :-)
#Python 3.8+ is required. 

if not __debug__: #__debug__ must be true for the bot to run (because assert statements)
    raise RuntimeError("__debug__ must be True for the bot to run!")

#imports - standard library
import copy
import random
import os
import warnings
from time import sleep, time, asctime
import subprocess
import traceback
import threading
from sys import stderr
# Imports - 3rd party
import dislash #https://github.com/EQUENOS/dislash.py
from dislash import InteractionClient, Option, OptionType, NotOwner, OptionChoice
import nextcord #https://github.com/nextcord/nextcord
import nextcord.ext.commands as nextcord_commands
from dislash.application_commands.core import check
# Imports - My own files
from helpful_modules import _error_logging, checks, cooldowns
from helpful_modules import custom_embeds, problems_module
from helpful_modules import return_intents, save_files, the_documentation_file_loader
# might be replaced with from helpful_modules import * and using __all__

from cogs import developer_commands
from helpful_modules.cooldowns import check_for_cooldown, OnCooldown
from helpful_modules._error_logging import log_error

from helpful_modules.custom_embeds import *
from helpful_modules.the_documentation_file_loader import *
try:
    import dotenv # https://pypi.org/project/python-dotenv/
    assert hasattr(dotenv, "load_dotenv")
except (ModuleNotFoundError, AssertionError):
    print("Dotenv could not be found, therefore cannot load .env")
dotenv.load_dotenv()
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", None)
if DISCORD_TOKEN is None:
    raise ValueError("Cannot start bot; no discord_token environment variable")



warnings.simplefilter("default") #unnecessary, probably will be removed
#constants

trusted_users=[]
try:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    assert DISCORD_TOKEN is not None
except (KeyError, AssertionError):
    raise RuntimeError(
        "You haven't setup the .env file correctly! You need DISCORD_TOKEN=<your token>"
        )
main_cache = problems_module.get_main_cache()
vote_threshold = -1
mathProblems={}
guildMathProblems = {}
cooldowns = {}
guild_maximum_problem_limit=125
erroredInMainCode = False
def loading_documentation_thread():
    "This thread reloads the documentation."
    d = DocumentationFileLoader()
    d.load_documentation_into_readable_files()
    del d
loader = threading.Thread(target=loading_documentation_thread)
loader.start()

def get_git_revision_hash() -> str:
    "A method that gets the git revision hash. Credit to https://stackoverflow.com/a/21901260 for the code :-)"
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()[:7] #[7:] is here because of the commit hash, the rest of this function is from stack overflow

def the_daemon_file_saver():

    global guildMathProblems, trusted_users,vote_threshold
    
    FileSaverObj = save_files.FileSaver(name = "The Daemon File Saver",
                             enabled=True,
                             printSuccessMessagesByDefault=True)
    FileSaverDict = FileSaverObj.load_files(main_cache,True)
    (guildMathProblems,
     bot.trusted_users,
     vote_threshold) = (
        FileSaverDict["guildMathProblems"],
        FileSaverDict["trusted_users"],
        FileSaverDict["vote_threshold"])

    while True: 
        sleep(45) 
        FileSaverObj.save_files(main_cache,False,guildMathProblems,vote_threshold,mathProblems,bot.trusted_users)

            



def generate_new_id():
    return random.randint(0, 10**14)

#Bot creation
Intents = return_intents.return_intents()
bot = nextcord_commands.Bot(
        command_prefix=" ",
        intents=Intents,
        application_id = 845751152901750824)
  
bot.main_cache = main_cache
bot.trusted_users = trusted_users
bot._transport_modules = {
    "problems_module": problems_module,"save_files": save_files, 
    "the_documentation_file_loader": the_documentation_file_loader, 
    "check_for_cooldown": check_for_cooldown, "custom_embeds": custom_embeds,
    "checks": checks}
bot.blacklisted_users = []
t = threading.Thread(target=the_daemon_file_saver,name="The File Saver",daemon=True)
#bot.load_extension("jishaku")


slash = InteractionClient(client=bot,sync_commands=True)
bot.slash = slash
bot.add_cog(developer_commands.DeveloperCommands(bot))
print("Bots successfully created.")

#Events

@bot.event
async def on_connect():
    "Run when the bot connects"
    print("The bot has connected to Discord successfully.")

@bot.event
async def on_ready():
    "Ran when the nextcord library detects that the bot is ready"
    print("The bot is now ready!")

@bot.event
async def on_slash_command_error(ctx, error, print_stack_traceback=[True, stderr]):
    "Function called when a slash command errors, which will inevitably happen"
    if print_stack_traceback[0]: 
        #print the traceback to the file
        print("\n".join(
            traceback.format_exception(
                etype=type(error),
                value=error,
                tb=error.__traceback__)),
             file=print_stack_traceback[1])
        
    if isinstance(error,OnCooldown):
        await ctx.reply(str(error))
        return
    error_traceback_as_obj = (traceback.format_exception(etype=type(error),value=error,tb=error.__traceback__))
    log_error(error) # Log the error
    if isinstance(error,NotOwner):
        await ctx.reply(embed=ErrorEmbed("You are not the owner of this bot."))
        return
    #Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))
    
    error_traceback = "\n".join(error_traceback_as_obj)

    await ctx.reply(embed=ErrorEmbed(nextcord.utils.escape_markdown(error_traceback),
        custom_title="Oh, no! An error occurred!", 
        footer=f"Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"))



    


@slash.slash_command(name="edit_problem", description = "edit a problem", options = [
    Option(name="problem_id",description="problem_id",
           type=OptionType.INTEGER,required=True),
    Option(name="guild_id",description="the guild id",
           type=OptionType.INTEGER),
    Option(name = "new_question", description="the new question",
           type=OptionType.STRING,required=False),
    Option(name = "new_answer", description="the new answer",
           type=OptionType.STRING,required=False)])
async def edit_problem(ctx,problem_id,new_question=None,new_answer=None,guild_id="null"):
    "Allows you to edit a math problem."
    await check_for_cooldown(ctx, "edit_problem",0.5)
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(str(guild_id),str(problem_id))
        if not problem.is_author(ctx.author):
            await ctx.reply(embed=ErrorEmbed(
                "You are not the author of this problem and therefore can't edit it!"
                ))
            return
    except KeyError:
        await ctx.reply(embed=ErrorEmbed("This problem does not exist."))
        return
    e = "Successfully"
    if new_question != None:
        if new_answer != None:
            problem.edit(question=new_question,answer=new_answer)
            e += f"changed the answer to {new_answer} and question to {new_question}!"
        else:
            problem.edit(question=new_question)
            e += f"changed the question to {new_question}!"
    else:
        if new_answer != None:
            problem.edit(answer=new_answer)
            e += f"changed the answer to {new_answer}"
        else:
            raise Exception("*** No new answer or new question provided. Aborting command...***")

    await ctx.reply(embed=SuccessEmbed(e),ephemeral=True)
      



@slash.slash_command(name="show_problem_info", description = "Show problem info", options=[
    Option(name="problem_id", description="problem id of the problem you want to show",
           type=OptionType.INTEGER, required=True)
    ,Option(name="show_all_data",
            description="whether to show all data (only useable by problem authors and trusted users",
            type=OptionType.BOOLEAN, required=False),
    Option(name="raw", description="whether to show data as json?",
           type=OptionType.BOOLEAN, required=False),
    Option(name="is_guild_problem", 
           description="whether the problem you are trying to view is a guild problem",
           type=OptionType.BOOLEAN, required=False)])
async def show_problem_info(ctx, problem_id, show_all_data=False, raw=False,is_guild_problem=False):
    "Show the info of a problem."
    await check_for_cooldown(ctx, "edit_problem",0.5)
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    problem_id = int(problem_id)
    try:
        guild_id = ctx.guild.id
    except AttributeError as exc:
        raise Exception(
            "*** AttributeError: guild.id was not found! Please report this error or refrain from using it here***"
        ) from exc


    real_guild_id = str(ctx.guild.id) if is_guild_problem else "null"
    problem = main_cache.get_problem(real_guild_id, str(problem_id))

    if True:  
        if is_guild_problem and guild_id is None:
            embed1= ErrorEmbed( description = "Run this command in the discord server which has this problem, not a DM!")
            ctx.reply(embed=embed1)
            return
        if guild_id not in main_cache.get_guilds():
            main_cache.add_empty_guild(guild_id)
        problem = main_cache.get_problem(str(ctx.guild.id) if is_guild_problem else "null",
                                         str(problem_id))
        Problem__ = f"Question: {problem.get_question()}\nAuthor: {str(problem.get_author())}\nNumVoters/Vote Threshold: {problem.get_num_voters()}/{vote_threshold}\nNumSolvers: {len(problem.get_solvers())}"
        
        if show_all_data:
            if not ((problem.is_author(ctx.author) or ctx.author.id not in bot.trusted_users or (
                is_guild_problem and ctx.author.guild_permissions.administrator == True))):
                await ctx.reply(embed=ErrorEmbed("Insufficient permissions!"), ephemeral=True)
                return
            Problem__+= f"\nAnswer: {problem.get_answer}"
        
            

        if raw:
            await ctx.reply(embed=SuccessEmbed(str(problem.convert_to_dict())), ephemeral=True)
            return
        await ctx.reply(embed=SuccessEmbed(Problem__), ephemeral=True)
@slash.slash_command(name="list_all_problem_ids", description= "List all problem ids", options=[
    Option(name="show_only_guild_problems", description="Whether to show guild problem ids",required=False,
           type=OptionType.BOOLEAN)])
async def list_all_problem_ids(ctx,show_only_guild_problems=False):
    "Lists all problem ids."
    await check_for_cooldown(ctx, "list_all_problem_ids",2.5)
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    if show_only_guild_problems:
        guild_id = ctx.guild.id
        if guild_id is None:
            await ctx.reply(
                "Run this command in a Discord server or set show_only_guild_problems to False!",
                            ephemeral=True)
            return
        if show_only_guild_problems:
            guild_problems = main_cache.get_guild_problems(ctx.guild)
        else:
            guild_problems = main_cache.get_global_problems()
        thing_to_write = [str(problem) for problem in guild_problems]
        await ctx.reply(embed=SuccessEmbed(
            "\n".join(thing_to_write)[:1950],successTitle="Problem IDs:"
            ))
        return

    global_problems = main_cache.get_global_problems()
    thing_to_write = "\n".join([str(problem.id) for problem in global_problems])
    await ctx.send(embed=SuccessEmbed(thing_to_write))
  
@slash.slash_command(name="generate_new_problems", description= "Generates new problems", options=[
    Option(name="num_new_problems_to_generate", description="the number of problems that should be generated",
           type=OptionType.INTEGER, required=True)])
async def generate_new_problems(ctx, num_new_problems_to_generate):
    "Generate new Problems"
    await check_for_cooldown(ctx, "generate_new_problems",0.5)
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)

    if ctx.author.id not in bot.trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't trusted!",ephemeral=True))
        return
    if num_new_problems_to_generate > 200:
        await ctx.reply("You are trying to create too many problems. Try something smaller than or equal to 200.",ephemeral=True)

    for i in range(num_new_problems_to_generate): # basic problems for now.... :(
        operation = random.choice(["+", "-", "*", "/", "^"])
        if operation == "^":
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
        else:
            num1 = random.randint(-1000, 1000)
            num2 = random.randint(-1000, 1000)
            while num2 == 0 and operation == "/":
                num2 = random.randint(-1000,1000)
            
        if operation == "^":
            answer = num1**num2
        elif operation == "+":
            answer = num1+num2
        elif operation == "-":
            answer = num1 - num2
        elif operation == "*":
            answer = num1 * num2
        elif operation == "/":
            answer = round(num1*100 / num2)/100
        #elif op
        while True:
            problem_id = generate_new_id()
            if problem_id not in [problem.id for problem in main_cache.get_global_problems()]:
                break
        q = "What is " + str(num1) + " " + {
        "*": "times",
         "+": "times", 
          "-": "minus", 
         "/": "divided by",
         "^": "to the power of"
         }[operation] + " " + str(num2) + "?"
        Problem = problems_module.MathProblem(
            question= q,
          answer = str(answer),
          author = 845751152901750824,
          guild_id = "null",
          id = problem_id,
          cache=main_cache
        )
        main_cache.add_problem("null",problem_id,Problem)
    await ctx.reply(embed=SuccessEmbed(
        f"Successfully created {str(num_new_problems_to_generate)} new problems!"
        ), ephemeral=True)
##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list 
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")
@slash.slash_command(name="delallbotproblems", description = "delete all automatically generated problems")
async def delallbotproblems(ctx):
    await check_for_cooldown(ctx, "delallbotproblems",10)
    "Delete all automatically generated problems"
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    await ctx.reply(embed=SimpleEmbed("",description="Attempting to delete bot problems"),ephemeral=True) #may get rid of later? :)
    numDeletedProblems = 0
    problems_to_delete = [problem for problem in main_cache.get_global_problems() if
                          problem.get_author() == bot.user.id]
    for problem in problems_to_delete:
        main_cache.remove_problem(str(problem.guild_id), str(problem.id))
        numDeletedProblems+=1
    await ctx.reply(embed=SuccessEmbed(f"Successfully deleted {numDeletedProblems}!"))
@slash.slash_command(name = "list_trusted_users", description = "list all trusted users")
async def list_trusted_users(ctx):
    "List all trusted users."
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    __trusted_users = ""
    for item in bot.trusted_users:
        __trusted_users += "<@" + str(item) + ">"
        __trusted_users+= "\n"
    await ctx.reply(__trusted_users, ephemeral = True)
@slash.slash_command(name="submit_problem", description = "Create a new problem",
                     options = [Option(name="answer", description="The answer to this problem",
                                       type=OptionType.STRING, required=True),
                                Option(name="question", description="your question",
                                       type=OptionType.STRING, required=True),
                                Option(name="guild_question", description="Whether it should be a question for the guild",
                                       type=OptionType.BOOLEAN, required=False)])
async def submit_problem(ctx, answer, question, guild_question=False):
    "Create & submit a new problem"

    await check_for_cooldown(ctx, "submit_problem",5)

    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    if len(question) > 250:
        await ctx.reply(embed=ErrorEmbed(
            "Your question is too long! Therefore, it cannot be added. The maximum question length is 250 characters.",
                                         custom_title="Your question is too long."), ephemeral=True)
        return
    if len(answer) > 100:
        await ctx.reply(embed=ErrorEmbed(
            description="Your answer is longer than 100 characters. Therefore, it is too long and cannot be added.",
                                         custom_title="Your answer is too long"),
                        ephemeral=True)
        remover=threading.Thread(target=main_cache.remove_duplicate_problems)
        remover.start()
        return
    if guild_question:
        guild_id = ctx.guild.id
        if guild_id is None:
            await ctx.reply(embed=ErrorEmbed("You need to be in the guild to make a guild question!"))
            return

        if guild_id not in main_cache.get_guilds():
            main_cache.add_empty_guild(guild_id)
        elif len(main_cache.get_guild_problems(ctx.guild)) >= guild_maximum_problem_limit and guild_question:

            await ctx.reply(embed=ErrorEmbed("You have reached the guild math problem limit."))
            return

        while True:

            problem_id = generate_new_id()
            if problem_id not in [problem.id for problem in main_cache.get_guild_problems(ctx.guild)]:
                break

        if guild_question:
            guild_id = str(ctx.guild.id)
        else:
            guild_id = "null"
        problem = problems_module.MathProblem(
          question=question,
          answer=answer,
          id=problem_id,
          author=ctx.author.id,
          guild_id=guild_id,
          cache = main_cache
        )
        main_cache.add_problem(guild_id=str(guild_id),
                               problem_id=str(problem_id),
                               Problem=problem)
        

        await ctx.reply(embed=SuccessEmbed("You have successfully made a math problem!",
                                           successTitle="Successfully made a new math problem."),
                        ephemeral = True)

        return
    while True:
        problem_id = generate_new_id()
        if problem_id not in main_cache.get_global_problems().keys():
            break
    

    problem = problems_module.MathProblem(question=question
                                          ,answer=answer,
                                          id=problem_id,
                                          guild_id="null",
                                          author=ctx.author.id,
                                          cache = main_cache)
    main_cache.add_problem(problem_id=str(problem_id),
                           guild_id=str(problem.guild_id),
                           Problem=problem)
    await ctx.reply(embed=SuccessEmbed("You have successfully made a math problem!"
                                       ), ephemeral = True)
    t=threading.Thread(target=main_cache.remove_duplicate_problems)
    t.start()

@slash.slash_command(name="check_answer", description = "Check if you are right",
                     options=[
                         Option(name="problem_id", description="the id of the problem you are trying to check the answer of",
                                type=OptionType.INTEGER, required=True),
                         Option(name="answer", description="your answer",
                                type=OptionType.STRING, required=True),
                         Option(name="checking_guild_problem", description="whether checking a guild problem",
                                type=OptionType.BOOLEAN, required = False)])
async def check_answer(ctx,problem_id,answer, checking_guild_problem=False):
    "Check if you are right"
    await check_for_cooldown(ctx, "check_answer",5)

    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(ctx.guild.id if checking_guild_problem else "null", str(problem_id))
        if problem.is_solver(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You have already solved this problem!",
                                             custom_title="Already solved."),
                            ephemeral = True)
            return
    except KeyError:
        await ctx.reply(embed=ErrorEmbed("This problem doesn't exist!",
                                         custom_title="Nonexistant problem."),
                        ephemeral=True)
        return

    if not problem.check_answer(answer):
        await ctx.reply(embed=ErrorEmbed(
            "Sorry..... but you got it wrong! You can vote for the deletion of this problem if it's wrong or breaks copyright rules.",
                                         custom_title="Sorry, your answer is wrong."), ephemeral=True)
    else:
        await ctx.reply(embed=SuccessEmbed("",successTitle="You answered this question correctly!"), ephemeral=True)
        problem.add_solver(ctx.author)
        return
@slash.slash_command(name="list_all_problems", description = "List all problems stored with the bot",
                     options=[
                         Option(name="show_solved_problems", description="Whether to show solved problems",
                                type=OptionType.BOOLEAN, required=False),
                         Option(name="show_guild_problems", description="Whether to show solved problems",
                                type=OptionType.BOOLEAN, required=False),
                         Option(name="show_only_guild_problems", description="Whether to only show guild problems",
                                type=OptionType.BOOLEAN, required=False)])
async def list_all_problems(ctx, show_solved_problems=False,show_guild_problems=True,show_only_guild_problems=False):
    "List all MathProblems."
    await check_for_cooldown(ctx,"list_all_problems")
    if ctx.guild is None and show_guild_problems:
        await ctx.reply("You must be in a guild to see guild problems!")
        return
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    showSolvedProblems = show_solved_problems
    if ctx.guild is not None:
        guild_id = ctx.guild.id
    else:
        guild_id = "null"
    if guild_id not in guildMathProblems:
        guildMathProblems[guild_id]={}
    if mathProblems.keys() == []:
        await ctx.reply(embed=ErrorEmbed("There aren't any problems! You should add one!"), ephemeral=True)
        return
    #if not showSolvedProblems and False not in [ctx.author.id in mathProblems[id]["solvers"] for id in mathProblems.keys()] or (show_guild_problems and (show_only_guild_problems and (guildMathProblems[ctx.guild.id] == {}) or False not in [ctx.author.id in guildMathProblems[guild_id][id]["solvers"] for id in guildMathProblems[guild_id].keys()])) or show_guild_problems and not show_only_guild_problems and False not in [ctx.author.id in mathProblems[id]["solvers"] for id in mathProblems.keys()] and False not in [ctx.author.id in guildMathProblems[guild_id][id]["solvers"] for id in guildMathProblems[guild_id].keys()]:
        #await ctx.reply("You solved all the problems! You should add a new one.", ephemeral=True)
        #return
    problem_info_as_str = ""
    problem_info_as_str += "Problem Id \t Question \t numVotes \t numSolvers"
    if show_guild_problems:
        for problem in main_cache.get_guild_problems(ctx.guild):
            if len(problem_info_as_str) >= 1930:
                problem_info_as_str += "The combined length of the questions is too long.... shortening it!" #May be removed
                await ctx.reply(embed=SuccessEmbed(problem_info_as_str[:1930]))
                return
            if not (showSolvedProblems) and problem.is_solver(ctx.author):
                continue
            problem_info_as_str += "\n"
            problem_info_as_str += str(problem.id) + "\t"
            problem_info_as_str += str(problem.get_question()) + "\t"
            problem_info_as_str += "(" 
            problem_info_as_str+= str(problem.get_num_voters()) + "/" + str(vote_threshold) + ")" + "\t"
            problem_info_as_str += str(len(problem.get_solvers())) + "\t"
            problem_info_as_str += "(guild)"
    if len(problem_info_as_str) > 1930:
        await ctx.reply(embed=SuccessEmbed(problem_info_as_str[:1930]))
        return
    if show_only_guild_problems:
        await ctx.reply(problem_info_as_str[:1930])
        return
    global_problems = main_cache.get_global_problems()
    for problem in global_problems: 
        if len(problem) >= 1930:
            problem_info_as_str += "The combined length of the questions is too long.... shortening it!"
            await ctx.reply(embed=SuccessEmbed(problem_info_as_str[:1930]))
            return
        if not isinstance(problem, problems_module.MathProblem):
            print(list(global_problems))
            raise RuntimeError("Uhhhhhhh..... the problem is not a MathProblem! Please help :-)") # For some reason..... the problem is an Integer, not a MathProblem...
            #For now, I could get the problem.... (it looks like an ID, but I should find the root cause first)
        if not (showSolvedProblems) and problem.is_solver(ctx.author):
            continue
        #Probably will be overhauled with str(problem)
        problem_info_as_str += "\n"
        problem_info_as_str += str(problem.id) + "\t"
        problem_info_as_str += str(problem.get_question()) + "\t"
        problem_info_as_str += "(" 
        problem_info_as_str+= str(problem.get_num_voters()) + "/" + str(vote_threshold) + ")" + "\t"
        problem_info_as_str += str(len(problem.get_solvers())) + "\t"
    await ctx.reply(embed=SuccessEmbed(problem_info_as_str[:1930]))

@slash.slash_command(name = "set_vote_threshold", description = "Sets the vote threshold", options=[
    Option(name="threshold", description="the threshold you want to change it to",
           type=OptionType.INTEGER, required=True)])
async def set_vote_threshold(ctx,threshold):
    "Set the vote threshold"
    await check_for_cooldown(ctx,"")
    if ctx.guild is not None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    global vote_threshold
    try:
        threshold = int(threshold)
    except TypeError:
        await ctx.reply(embed=ErrorEmbed(
            "Invalid threshold argument! (threshold must be an integer)"),
                        ephemeral=True)
        return
    if ctx.author.id not in bot.trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't allowed to do this!"), ephemeral=True)
        return
    if threshold <1:
        await ctx.reply(embed=ErrorEmbed(
            "You can't set the threshold to smaller than 1."),
                        ephemeral=True)
        return
    vote_threshold=int(threshold)
    for problem in main_cache.get_global_problems():
        if problem.get_num_voters() > vote_threshold:
            main_cache.remove_problem(problem.guild_id, problem.id)
    await ctx.reply(embed=SuccessEmbed(f"The vote threshold has successfully been changed to {threshold}!"),
                    ephemeral=True)
@slash.slash_command(name="vote", description = "Vote for the deletion of a problem", options=[
    Option(name="problem_id", description="problem id of the problem you are attempting to delete",
           type=OptionType.INTEGER, required=True),
    Option(name="is_guild_problem", description="problem id of the problem you are attempting to delete",
           type=OptionType.BOOLEAN, required=False)])
async def vote(ctx, problem_id,is_guild_problem=False):
    "Vote for the deletion of a problem"
    await check_for_cooldown(5,"vote")
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(
            ctx.guild.id if is_guild_problem else "null",
                                         problem_id=str(problem_id))
        if problem.is_voter(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You have already voted for the deletion of this problem!"), ephemeral=True)
            return
    except problems_module.ProblemNotFound:
        await ctx.reply(embed=ErrorEmbed("This problem doesn't exist!"), ephemeral=True)
        return
    problem.add_voter(ctx.author)
    string_to_print = "You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    string_to_print += f"{problem.get_num_voters()}/{vote_threshold} votes on this problem!"
    await ctx.reply(embed=SuccessEmbed(string_to_print, title = "YouSuccessfully voted"), ephemeral=True)
    if problem.get_num_voters() >= vote_threshold:
        main_cache.remove_problem(guild_id=problem.guild_id, problem_id = problem.id)
        await ctx.reply(embed=SimpleEmbed("This problem has surpassed the threshold and has been deleted!"), ephemeral=True)
@slash.slash_command(name="unvote", description = "Vote for the deletion of a problem", options=[
    Option(name="problem_id", description="problem id of the problem you are attempting to delete",
           type=OptionType.INTEGER, required=True),
    Option(name="is_guild_problem", description="problem id of the problem you are attempting to delete",
           type=OptionType.BOOLEAN, required=False)])
async def unvote(ctx, problem_id,is_guild_problem=False):
    "Unvote for the deletion of a problem"
    await check_for_cooldown(ctx,"unvote",0.5)
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(ctx.guild.id if is_guild_problem else "null",
                                         problem_id=str(problem_id))
        if not problem.is_voter(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You can't unvote since you are not voting."), ephemeral=True)
            return
    except problems_module.ProblemNotFound:
        await ctx.reply(embed=ErrorEmbed("This problem doesn't exist!"), ephemeral=True)
        return
    problem.voters.remove(ctx.author.id)
    e = "You successfully unvoted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    e += str(problem.get_num_voters())
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem!"
    await ctx.reply(embed=SuccessEmbed(e), ephemeral=True)
@slash.slash_command(name="delete_problem", description = "Deletes a problem", options = [
    Option(name="problem_id", description="Problem ID!",
           type=OptionType.INTEGER, required=True),
    Option(name="is_guild_problem", description="whether deleting a guild problem",
           type=OptionType.USER, required=False)])
async def delete_problem(ctx, problem_id,is_guild_problem=False):
    "Delete a math problem"
    await check_for_cooldown(ctx,"unvote",0.5)
    guild_id = ctx.guild.id
    if is_guild_problem:
        if guild_id is None:
            await ctx.reply(embed=ErrorEmbed(
                "Run this command in the discord server which has the problem you are trying to delete, or switch is_guild_problem to False."
                ))
            return
        if problem_id not in main_cache.get_guild_problems(ctx.guild).keys():
            await ctx.reply(embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True)
            return
        if not (ctx.author.id in bot.trusted_users or not (
            main_cache.get_problem(str(guild_id),str(problem_id)).is_author()
            ) or (ctx.author.guild_permissions.administrator)):
            await ctx.reply(embed=ErrorEmbed("Insufficient permissions"), ephemeral=True)
            return
        main_cache.remove_problem(str(guild_id), problem_id)
        await ctx.reply(
            embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"),
            ephemeral=True)
    if guild_id is None:
        await ctx.reply(embed=ErrorEmbed(
            "Run this command in the discord server which has the problem, or switch is_guild_problem to False."))
        return
    if problem_id not in main_cache.get_guild_problems(ctx.guild).keys():
        await ctx.reply(embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True)
        return
    if not (ctx.author.id in bot.trusted_users or not
            (main_cache.get_problem(guild_id,problem_id).is_author())
            or ctx.author.guild_permissions.administrator): #Not
        await ctx.reply(embed=ErrorEmbed("Insufficient permissions!"), ephemeral=True)
        return
    main_cache.remove_problem("null", problem_id)
    await ctx.reply(embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"), ephemeral=True)
@slash.slash_command(name="add_trusted_user", description = "Adds a trusted user",options=[
    Option(name="user", description="The user you want to give super special bot access to",
           type=OptionType.USER,
           required=True)])
async def add_trusted_user(ctx,user):
    """The slash command that adds a trusted user. See the documentation for details.
You must be a trusted user to add a trusted user, and the user you are trying to make a trusted user must not be a trusted user. 
You must also share a server with the new trusted user."""
    await check_for_cooldown(ctx,"add_trusted_user",600)
    if ctx.author.id not in bot.trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True)
        return
    if user.id in bot.trusted_users:
        await ctx.reply(embed=ErrorEmbed(f"{user.name} is already a trusted user!"),
                        ephemeral=True)
        return
    bot.trusted_users.append(user.id)
    await ctx.reply(embed=ErrorEmbed(f"Successfully made {user.nick} a trusted user!"), ephemeral=True) 

@slash.slash_command(name="remove_trusted_user", description = "removes a trusted user",options=
                     [Option(
                         name="user",
                         description="The user you want to take super special bot access from",
                         type=OptionType.USER, required=True)])
async def remove_trusted_user(ctx,user):
    "Remove a trusted user"
    await check_for_cooldown(ctx,"remove_trusted_user",600)
    if ctx.author.id not in bot.trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True)
        return
    if user.id not in bot.trusted_users:
        await ctx.reply(embed=ErrorEmbed(f"{user.name} isn't a trusted user!", ephemeral=True))
        return
    bot.trusted_users.pop(user.id)
    await ctx.reply(embed=ErrorEmbed(f"Successfully made {user.nick} no longer a trusted user!"), ephemeral=True) 


@slash.slash_command(name="ping", description = "Prints latency and takes no arguments")
async def ping(ctx):
    await check_for_cooldown(ctx,"ping",5)
    "Ping the bot! This returns its latency in ms."
    await ctx.reply(embed=SuccessEmbed(f"Pong! My latency is {round(bot.latency*1000)}ms."), ephemeral=True)
@slash.slash_command(name="what_is_vote_threshold",
                     description="Prints the vote threshold and takes no arguments")
async def what_is_vote_threshold(ctx):
    "Returns the vote threshold"
    await check_for_cooldown(ctx,"what_is_vote_threshold",5)
    await ctx.reply(embed=SuccessEmbed(f"The vote threshold is {vote_threshold}."),ephemeral=True)
@slash.slash_command(name="generate_invite_link", description = "Generates a invite link for this bot! Takes no arguments")
async def generate_invite_link(ctx):
    "Generate an invite link for the bot."
    await check_for_cooldown(ctx,"generateInviteLink",5)
    await ctx.reply(embed=SuccessEmbed(
        "https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147552256&scope=bot%20applications.commands")
                    ,ephemeral=True)

@slash.slash_command(name="github_repo",description = "Returns the link to the github repo")
async def github_repo(ctx):
    await check_for_cooldown(ctx,"github_repo",5)
    await ctx.reply(embed=SuccessEmbed(
        "[Repo Link:](https://github.com/rf20008/TheDiscordMathProblemBotRepo) ",
                                       successTitle="Here is the Github Repository Link."))

@slash.slash_command(name="submit_a_request", description = "Submit a request. I will know!", options = [
  Option(name="offending_problem_guild_id", description = "The guild id of the problem you are trying to remove. The guild id of a global problem is null", type = OptionType.INTEGER, required = False),
  Option(name = "offending_problem_id", description = "The problem id of the problem. Very important (so I know which problem to check)", type = OptionType.INTEGER, required = False),
  Option(name = "extra_info", description = "A up to 5000 character description (about 2 pages) Use this wisely!", type = OptionType.STRING, required = False),
  Option(name = "copyrighted_thing", description = "The copyrighted thing that this problem is violating", type = OptionType.STRING, required=False)
, Option(name="is_legal", description = "Is this a legal request?", required = False, type = OptionType.BOOLEAN)])
async def submit_a_request(inter, offending_problem_guild_id= None, offending_problem_id=None, extra_info=None, copyrighted_thing = None, is_legal = False):
    "Submit a request! I will know! It uses a channel in my discord server and posts an embed"
    __import__("cooldowns").check_for_cooldown("submit_a_request", 5) #5 seconds cooldown
    if(extra_info is None and is_legal is False and copyrighted_thing is not Exception and offending_problem_guild_id is  None and offending_problem_id is None):
        await inter.reply(embed=ErrorEmbed("You must specify some field."))
    if extra_info is None:
        await inter.reply(embed=ErrorEmbed("Please provide extra information!"))
    assert len(extra_info) <= 5000
    channel = await bot.fetch_channel(901464948604039209) # CHANGE THIS IF YOU HAVE A DIFFERENT REQUESTS CHANNEL! (the part after id)
    try:
        Problem = main_cache.get_problem(offending_problem_guild_id, offending_problem_id)
        problem_found = True
    except (TypeError, KeyError):
        #Problem not found
        problem_found = False
    content = bot.owner_id
    embed = nextcord.Embed(title = f"A new request has been recieved from {inter.author.name}#{inter.author.discriminator}!", description = "")
    if is_legal:
      embed = nextcord.Embed(title = f"A new legal request has been recieved from {inter.author.name}#{inter.author.discriminator}!", description = "")

    if problem_found:
        embed.description = f"Problem_info:{ str(Problem)}"
    embed.description += f"""Copyrighted thing: (if legal): {copyrighted_thing}
    Extra info: {extra_info}"""
    if problem_found:
        embed.set_footer(text=str(Problem) + asctime())
    else:
        embed.set_footer(text=str(asctime()))
    
    content = "A request has been submitted."
    for owner_id in bot.owner_ids: #Mentioning owners: may be removed (you can also remove it as well)
        content += f"<@{owner_id}>"
    content += f"<@{bot.owner_id}>"
    await channel.send(embed=embed, content = content)
    await inter.reply("Your request has been submitted!")

@bot.event
async def on_guild_join(guild):
    
    if guild.id == "_global": #Should never happen
      
        await guild.leave()
        print("Oh no")
        raise RuntimeError("Oh no..... there is a guild with id _global... this will mess up the bot!") # Make sure that a guild with id _global doesn't mess up stuff
if __name__ == "__main__":
    print("The bot has finished setting up and will now run.")
    #slash.run(DISCORD_TOKEN)
    bot.run(DISCORD_TOKEN)

