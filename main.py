import math, random, os, warnings, threading, aiohttp, copy, nextcord, discord
import dislash, traceback
import return_intents
import nextcord.ext.commands as nextcord_commands

import problems_module


from dislash import InteractionClient, Option, OptionType, NotOwner, OptionChoice
from time import sleep, time
from nextcord.ext import commands, tasks 
from random import randint
from nextcord import Embed, Color
from custom_embeds import *
from nextcord.ext.commands import errors
from save_files import FileSaver
from user_error import UserError
from the_documentation_file_loader import *
from problems_module import get_main_cache
from sys import exc_info



warnings.simplefilter("default")
#constants
#print("Is it working??")
trusted_users=[]
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
#print(type(DISCORD_TOKEN))
#print(f"Discord Token: {DISCORD_TOKEN}")
main_cache = get_main_cache()
vote_threshold = 1
mathProblems={}
guildMathProblems = {}
guild_maximum_problem_limit=125
erroredInMainCode = False
def loading_documentation_thread():
    d = DocumentationFileLoader()
    d.load_documentation_into_readable_files()
    del d
t = threading.Thread(target=loading_documentation_thread)
t.start()
#print("yes")

def the_daemon_file_saver():
    #print("e",flush=True)
    global mathProblems,guildMathProblems
    global trusted_users
    global vote_threshold
    FileSaverObj = FileSaver("The Daemon File Saver", enabled=True,printSuccessMessagesByDefault=True)
    FileSaverDict = FileSaverObj.load_files(True)
    (guildMathProblems,trusted_users,vote_threshold) = (FileSaverDict["guildMathProblems"],FileSaverDict["trusted_users"],FileSaverDict["vote_threshold"])

    while True:    
        sleep(45) 
        FileSaverObj.save_files(True,guildMathProblems,vote_threshold,mathProblems,trusted_users)

            
t = threading.Thread(target=the_daemon_file_saver,name="The File Saver",daemon=True)

t.start()

#print("Work please!!!!!")
#print(trusted_users)
def generate_new_id():
    return random.randint(0, 10**14)
Intents = return_intents.return_intents()
bot = nextcord_commands.Bot(
        " ",intents=Intents
)
#bot.load_extension("jishaku")


slash = InteractionClient(client=bot,sync_commands=True)
print("Bots successfully created.")


@bot.event
async def on_ready():
    print("The bot has connected to Discord successfully.")

@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error,discord.ext.commands.errors.CommandOnCooldown):
        await ctx.reply(str(error))
        return
    if isinstance(error,NotOwner):
        await ctx.reply(embed=ErrorEmbed("You are not the owner of this bot."))
        return
    #Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))

    await ctx.reply(embed=ErrorEmbed(traceback.format_exc(),custom_title="Oh, no! An exception occurred"))
    

@bot.event
async def on_command_error(ctx,error):
    print(error)
    if isinstance(error, errors.MissingRequiredArgument):
        await ctx.channel.send(embed=ErrorEmbed("Not enough arguments!"))
        return
    if isinstance(error, errors.CommandNotFound):
        await ctx.channel.send(embed=ErrorEmbed("This command does not exist."))
        return
    if isinstance(error, errors.TooManyArguments):
        await ctx.reply(embed=ErrorEmbed("Too many arguments."))
        return
    print(type(error))
    erroredInMainCode=True
    await ctx.reply("Something went wrong! Message the devs ASAP! (Our tags are ay136416#2707 and duck_master#8022)")
    raise error



@slash.command(name="force_load_files",description="Force loads files to replace dictionaries. THIS WILL DELETE OLD DICTS!")
async def force_load_files(ctx):
    global mathProblems,guildMathProblems
    global trusted_users
    global vote_threshold
    if ctx.author.id not in trusted_users:
        await ctx.reply(ErrorEmbed("You aren't trusted and therefore don't have permission to forceload files."))
        return
    try:
        FileSaver3 = FileSaver(enabled=True,printSuccessMessagesByDefault=False)
        FileSaverDict = FileSaver3.load_files()
        (guildMathProblems,trusted_users,vote_threshold) = (FileSaverDict["guildMathProblems"],FileSaverDict["trusted_users"],FileSaverDict["vote_threshold"])
        FileSaver3.goodbye()
        await ctx.reply(embed=SuccessEmbed("Successfully forcefully loaded files!"))
        return
    except RuntimeError:
        await ctx.reply(embed=ErrorEmbed("Something went wrong..."))
        return
@slash.slash_command(name="force_save_files",description="Forcefully saves files (can only be used by trusted users).")
async def force_save_files(ctx):
    global mathProblems,guildMathProblems
    global trusted_users
    global vote_threshold
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    if ctx.author.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't trusted and therefore don't have permission to forcesave files."))
        return
    try:
        FileSaver2 = FileSaver(enabled=True)
        FileSaver2.save_files(True,guildMathProblems,vote_threshold,mathProblems,trusted_users)
        FileSaver2.goodbye()
        await ctx.reply(embed=SuccessEmbed("Successfully saved 4 files!"))
    except RuntimeError:
        await ctx.reply(embed=ErrorEmbed("Something went wrong..."))
    


@slash.slash_command(name="edit_problem", description = "edit a problem", options = [
Option(name="problem_id",description="problem_id",type=OptionType.INTEGER,required=True),
Option(name="guild_id",description="the guild id", type=OptionType.INTEGER),Option(name = "new_question", description="the new question", type=OptionType.STRING,required=False),Option(name = "new_answer", description="the new answer", type=OptionType.STRING,required=False)])
async def edit_problem(ctx,new_question,new_answer,problem_id,guild_id):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(str(guild_id),str(problem_id))
        if not problem.is_author(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You are not the author of this problem and therefore can't edit it!"))
    except:
        await ctx.reply(embed=ErrorEmbed("This problem does not exist."))

    problem.edit(question=new_question,answer=new_answer)

    await ctx.reply(embed=SuccessEmbed(f"Successfully changed the answer to {new_answer} and question to {new_question}!"))
      



@slash.slash_command(name="show_problem_info", description = "Show problem info", options=[Option(name="problem_id", description="problem id of the problem you want to show", type=OptionType.INTEGER, required=True),Option(name="show_all_data", description="whether to show all data (only useable by problem authors and trusted users", type=OptionType.BOOLEAN, required=False),Option(name="raw", description="whether to show data as json?", type=OptionType.BOOLEAN, required=False),Option(name="is_guild_problem", description="whether the problem you are trying to view is a guild problem", type=OptionType.BOOLEAN, required=False)])
async def show_problem_info(ctx, problem_id, show_all_data=False, raw=False,is_guild_problem=False):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    problem_id = int(problem_id)
    try:
        guild_id = ctx.guild.id
    except AttributeError as e:
        await ctx.reply(":( AttributeError")
        return


    if guild_id not in guildMathProblems:
        guildMathProblems[guild_id]={}
    yay = str(ctx.guild.id) if is_guild_problem else "null"
    problem = main_cache.get_problem(yay, str(problem_id))

    if True:  
        if is_guild_problem and guild_id == None:
            embed1= ErrorEmbed(title="Error", description = "Run this command in the discord server which has this problem, not a DM!")
            ctx.reply(embed=embed1)
            return
        if guild_id not in main_cache._dict.keys():
            main_cache.add_empty_guild(guild_id)
        problem = main_cache.get_problem(str(ctx.guild.id) if is_guild_problem else "null",str(problem_id))
        e= "Question: "
        e+= problem.get_question() 
        e+= "\nAuthor: "
        e+= str(problem.get_author())
        e+= "\nNumVoters/Vote Threshold: "
        e+= str(problem.get_num_voters())
        e+= "/"
        e += str(vote_threshold)
        e+= " \nNumSolvers: "
        e+= str(len(problem.get_solvers()))
        if show_all_data:
            e+= "\nAnswer: "
            e+= str(problem.get_answer())
        
        if show_all_data:
            if not ((problem.is_author(ctx.author) or ctx.author.id not in trusted_users or (is_guild_problem and ctx.author.guild_permissions.administrator == True))):
                await ctx.reply(embed=ErrorEmbed("Insufficient permissions!"), ephemeral=True)
                return

        if raw:
            await ctx.reply(embed=SuccessEmbed(str(problem.convert_to_dict())), ephemeral=True)
            return
        await ctx.reply(embed=SuccessEmbed(e), ephemeral=True)
@slash.slash_command(name="list_all_problem_ids", description= "List all problem ids", options=[Option(name="show_only_guild_problems", description="Whether to show guild problem ids",required=False,type=OptionType.BOOLEAN)])
async def list_all_problem_ids(ctx,show_only_guild_problems=False):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    if show_only_guild_problems:
        guild_id = ctx.guild.id
        if guild_id == None:
            await ctx.reply("Run this command in a Discord server or set show_only_guild_problems to False!", ephemeral=True)
            return
        if show_only_guild_problems:
            guild_problems = main_cache.get_guild_problems(ctx.guild)
        else:
            guild_problems = main_cache.get_global_problems()
        thing_to_write = [str(problem) for problem in guild_problems]
        await ctx.reply(embed=SuccessEmbed("\n".join(thing_to_write)[:1950],successTitle="Problem IDs:"))
        return

    global_problems = main_cache.get_global_problems()
    thing_to_write = "\n".join([str(problem.id) for problem in global_problems])
    await ctx.send(embed=SuccessEmbed(thing_to_write))
  
@slash.slash_command(name="generate_new_problems", description= "Generates new problems", options=[Option(name="num_new_problems_to_generate", description="the number of problems that should be generated", type=OptionType.INTEGER, required=True)])
async def generate_new_problems(ctx, num_new_problems_to_generate):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)

    if ctx.author.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't trusted!",ephemeral=True))
        return
    elif num_new_problems_to_generate > 200:
        await ctx.reply("You are trying to create too many problems. Try something smaller than or equal to 200.", ephemeral=True)

    for i in range(num_new_problems_to_generate):
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
        q = "What is " + str(num1) + " " +{"*": "times", "+": "times", 
          "-": "minus", "/": "divided by", "^": "to the power of"}[operation] + " " + str(num2) + "?"
        Problem = problems_module.MathProblem(
          question= q,
          answer = str(answer),
          author = 845751152901750824,
          guild_id = "null",
          id = problem_id
        )
        main_cache.add_problem("null",problem_id,Problem)
    await ctx.reply(embed=SuccessEmbed(f"Successfully created {str(num_new_problems_to_generate)} new problems!"), ephemeral=True)
##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list 
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")
@slash.slash_command(name="delallbotproblems", description = "delete all automatically generated problems")
async def delallbotproblems(ctx):

    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    await ctx.reply(embed=SimpleEmbed("",description="Attempting to delete bot problems"),ephemeral=True)
    numDeletedProblems =0
    problems_to_delete = [problem for problem in main_cache.get_global_problems() if problem.get_author() == 845751152901750824]
    for problem in problems_to_delete:
        main_cache.remove_problem(str(problem.guild_id), str(problem.id))
        numDeletedProblems+=1
    await ctx.reply(embed=SuccessEmbed(f"Successfully deleted {numDeletedProblems}!"))
@slash.slash_command(name = "list_trusted_users", description = "list all trusted users")
async def list_trusted_users(ctx):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    e = ""
    for item in trusted_users:
        e += "<@" + str(item) + ">"
        e+= "\n"
    await ctx.reply(e, ephemeral = True)
@slash.slash_command(name="new_problem", description = "Create a new problem", options = [Option(name="answer", description="The answer to this problem", type=OptionType.STRING, required=True), Option(name="question", description="your question", type=OptionType.STRING, required=True),Option(name="guild_question", description="Whether it should be a question for the guild", type=OptionType.BOOLEAN, required=False)])
async def new_problem(ctx, answer, question, guild_question=False):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    if len(question) > 250:
        await ctx.reply(embed=ErrorEmbed("Your question is too long! Therefore, it cannot be added. The maximum question length is 250 characters.",custom_title="Your question is too long."), ephemeral=True)
        return
    if len(answer) > 100:
        await ctx.reply(embed=ErrorEmbed(description="Your answer is longer than 100 characters. Therefore, it is too long and cannot be added.",custom_title="Your answer is too long"),ephemeral=True)
        return
    if guild_question:
        guild_id = ctx.guild.id
        if guild_id == None:
            await ctx.reply(embed=ErrorEmbed("You need to be in the guild to make a guild question!"))
            return

        if guild_id not in main_cache._dict.keys():
            main_cache.add_empty_guild(guild_id)
        elif len(main_cache.get_guild_problems(ctx.guild)) >= guild_maximum_problem_limit and guild_question:

            await ctx.reply(embed=ErrorEmbed("You have reached the guild math problem limit."))
            return

        while True:

            problem_id = generate_new_id()
            if problem_id not in [problem.guild_id for problem in main_cache.get_guild_problems(ctx.guild)]:
                break

        if guild_question:
            guild_id = str(ctx.guild.id)
        else:
            guild_id = "null"
        problem = problems_module.MathProblem(
          question=question,
          answer=answer,
          id=str(problem_id),
          author=ctx.author.id,
          guild_id=guild_id
        )
        print(problem)
        main_cache.add_problem(problem.guild_id, problem_id,problem)
        

        await ctx.reply(embed=SuccessEmbed("You have successfully made a math problem!",successTitle="Successfully made a new math problem."), ephemeral = True)
        return
    while True:
        problem_id = generate_new_id()
        if problem_id not in [problem.id for problem in main_cache.get_global_problems()]:
            break
    print(problem_id)
    

    problem = problems_module.MathProblem(question=question,answer=answer,id=problem_id,guild_id="null",author=ctx.author.id)
    print(problem.convert_to_dict())
    main_cache.add_problem(problem_id, problem.guild_id,problem)
    await ctx.reply(embed=SuccessEmbed("You have successfully made a math problem!"), ephemeral = True)

@slash.slash_command(name="check_answer", description = "Check if you are right", options=[Option(name="problem_id", description="the id of the problem you are trying to check the answer of", type=OptionType.INTEGER, required=True),Option(name="answer", description="your answer", type=OptionType.STRING, required=True),Option(name="checking_guild_problem", description="whether checking a guild problem", type=OptionType.BOOLEAN, required = False)])
async def check_answer(ctx,problem_id,answer, checking_guild_problem=False):
    global mathProblems,guildMathProblems
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(ctx.guild.id if checking_guild_problem else "null", str(problem_id))
        if problem.is_solver(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You have already solved this problem!",custom_title="Already solved."), ephemeral = True)
            return
    except KeyError:
        await ctx.reply(embed=ErrorEmbed("This problem doesn't exist!",custom_title="Nonexistant problem."), ephemeral=True)
        return

    if not problem.check_answer(answer):
        await ctx.reply(embed=ErrorEmbed("Sorry..... but you got it wrong! You can vote for the deletion of this problem if it's wrong or breaks copyright rules.",custom_title="Sorry, your answer is wrong."), ephemeral=True)
    else:
        await ctx.reply(embed=SuccessEmbed("",successTitle="You answered this question correctly!"), ephemeral=True)
        problem.add_solver(ctx.author)
        return
@slash.slash_command(name="list_all_problems", description = "List all problems stored with the bot", options=[Option(name="show_solved_problems", description="Whether to show solved problems", type=OptionType.BOOLEAN, required=False),Option(name="show_guild_problems", description="Whether to show solved problems", type=OptionType.BOOLEAN, required=False),Option(name="show_only_guild_problems", description="Whether to only show guild problems", type=OptionType.BOOLEAN, required=False)])
async def list_all_problems(ctx, show_solved_problems=False,show_guild_problems=True,show_only_guild_problems=False):

    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)

    showSolvedProblems = show_solved_problems
    guild_id = ctx.guild.id
    if guild_id not in guildMathProblems:
        guildMathProblems[guild_id]={}
    if showSolvedProblems != "":
        showSolvedProblems = True
    else:
        showSolvedProblems = False
    #print(showSolvedProblems)
    if mathProblems.keys() == []:
        await ctx.reply(embed=ErrorEmbed("There aren't any problems! You should add one!"), ephemeral=True)
        return
    #if not showSolvedProblems and False not in [ctx.author.id in mathProblems[id]["solvers"] for id in mathProblems.keys()] or (show_guild_problems and (show_only_guild_problems and (guildMathProblems[ctx.guild.id] == {}) or False not in [ctx.author.id in guildMathProblems[guild_id][id]["solvers"] for id in guildMathProblems[guild_id].keys()])) or show_guild_problems and not show_only_guild_problems and False not in [ctx.author.id in mathProblems[id]["solvers"] for id in mathProblems.keys()] and False not in [ctx.author.id in guildMathProblems[guild_id][id]["solvers"] for id in guildMathProblems[guild_id].keys()]:
        #await ctx.reply("You solved all the problems! You should add a new one.", ephemeral=True)
        #return
    e = ""
    e += "Problem Id \t Question \t numVotes \t numSolvers"
    if show_guild_problems:
        for problem in main_cache.get_guild_problems(ctx.guild):
            if len(e) >= 1930:
                e += "The combined length of the questions is too long.... shortening it!"
                await ctx.reply(embed=SuccessEmbed(e[:1930]))
                return
            elif not (showSolvedProblems) and problem.is_solver(ctx.author):
                continue
            e += "\n"
            e += str(problem.id) + "\t"
            e += str(problem.get_question()) + "\t"
            e += "(" 
            e+= str(problem.get_num_voters()) + "/" + str(vote_threshold) + ")" + "\t"
            e += str(len(problem.get_solvers())) + "\t"
            e += "(guild)"
    if len(e) > 1930:
        await ctx.reply(embed=SuccessEmbed(e[:1930]))
        return
    if show_only_guild_problems:
        await ctx.reply(e[:1930])
        return

    for problem in main_cache.get_global_problems():
        if len(e) >= 1930:
            e += "The combined length of the questions is too long.... shortening it!"
            await ctx.reply(embed=SuccessEmbed(e[:1930]))
            return
        elif not (showSolvedProblems) and problem.is_solver(ctx.author):
            continue
        e += "\n"
        e += str(problem.id) + "\t"
        #print(mathProblems[question])
        e += str(problem.get_question()) + "\t"
        e += "(" 
        e+= str(problem.get_num_voters) + "/" + str(vote_threshold) + ")" + "\t"
        e += str(len(problem.get_solvers())) + "\t"
    await ctx.reply(embed=SuccessEmbed(e[:1930]))

@slash.slash_command(name = "set_vote_threshold", description = "Sets the vote threshold", options=[Option(name="threshold", description="the threshold you want to change it to", type=OptionType.INTEGER, required=True)])
async def set_vote_threshold(ctx,threshold):
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    global vote_threshold
    try:
        threshold = int(threshold)
    except:
        await ctx.reply(embed=ErrorEmbed("Invalid threshold argument! (threshold must be an integer)"), ephemeral=True)
        return
    if ctx.author.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't allowed to do this!"), ephemeral=True)
        return
    if threshold <1:
        await ctx.reply(embed=ErrorEmbed("You can't set the threshold to smaller than 1."), ephemeral=True)
        return
    vote_threshold=int(threshold)
    for problem in main_cache.get_global_problems():
        if problem.get_num_voters() > vote_threshold:
            main_cache.remove_problem(problem.guild_id, problem.id)
    await ctx.reply(embed=SuccessEmbed(f"The vote threshold has successfully been changed to {threshold}!"), ephemeral=True)
@slash.slash_command(name="vote", description = "Vote for the deletion of a problem", options=[Option(name="problem_id", description="problem id of the problem you are attempting to delete", type=OptionType.INTEGER, required=True),Option(name="is_guild_problem", description="problem id of the problem you are attempting to delete", type=OptionType.BOOLEAN, required=False)])
async def vote(ctx, problem_id,is_guild_problem=False):
    global mathProblems, guildMathProblems
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(ctx.guild.id if is_guild_problem else "null",problem_id=str(problem_id))
        if problem.is_voter(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You have already voted for the deletion of this problem!"), ephemeral=True)
            return
    except Exception:
        await ctx.reply(embed=ErrorEmbed("This problem doesn't exist!"), ephemeral=True)
        return
    problem.add_voter()
    e = "You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    e += str(problem.get_num_voters())
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem!"
    await ctx.reply(embed=SuccessEmbed(e), ephemeral=True)
    if problem.get_num_voters() >= vote_threshold:
        del mathProblems[problem_id]
        await ctx.reply(embed=SimpleEmbed("This problem has surpassed the threshold and has been deleted!"), ephemeral=True)
@slash.slash_command(name="unvote", description = "Vote for the deletion of a problem", options=[Option(name="problem_id", description="problem id of the problem you are attempting to delete", type=OptionType.INTEGER, required=True),Option(name="is_guild_problem", description="problem id of the problem you are attempting to delete", type=OptionType.BOOLEAN, required=False)])
async def unvote(ctx, problem_id,is_guild_problem=False):
    global mathProblems, guildMathProblems
    if ctx.guild != None and ctx.guild.id not in main_cache._dict.keys():
        main_cache.add_empty_guild(ctx.guild)
    try:
        problem = main_cache.get_problem(ctx.guild.id if is_guild_problem else "null",problem_id=str(problem_id))
        if not problem.is_voter(ctx.author):
            await ctx.reply(embed=ErrorEmbed("You can't unvote since you are not voting."), ephemeral=True)
            return
    except Exception:
        await ctx.reply(embed=ErrorEmbed("This problem doesn't exist!"), ephemeral=True)
        return
    problem.voters.remove(ctx.author.id)
    e = "You successfully unvoted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    e += str(problem.get_num_voters())
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem!"
    await ctx.reply(embed=SuccessEmbed(e), ephemeral=True)
@slash.slash_command(name="delete_problem", description = "Deletes a problem", options = [Option(name="problem_id", description="Problem ID!", type=OptionType.INTEGER, required=True),Option(name="is_guild_problem", description="whether deleting a guild problem", type=OptionType.USER, required=False)])
async def delete_problem(ctx, problem_id,is_guild_problem=False):
    global mathProblems, guildMathProblems
    user_id = ctx.author.id
    guild_id = ctx.guild.id
    if is_guild_problem:
        if guild_id == None:
            await ctx.reply(embed=ErrorEmbed("Run this command in the discord server which has the problem you are trying to delete, or switch is_guild_problem to False."))
            return
        if problem_id not in main_cache.get_guild_problems(ctx.guild).keys():
            await ctx.reply(embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True)
            return
        if not (ctx.author.id in trusted_users or not main_cache.get_problem(str(guild_id),str(problem_id)).is_author() or ctx.author.guild_permissions.administrator):
            await ctx.reply(embed=ErrorEmbed("Insufficient permissions"), ephemeral=True)
            return
        main_cache.remove_problem(str(guild_id), problem_id)
        await ctx.reply(embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"), ephemeral=True)
    if guild_id == None:
        await ctx.reply(embed=ErrorEmbed("Run this command in the discord server which has the problem, or switch is_guild_problem to False."))
        return
    if problem_id not in main_cache.get_guild_problems(ctx.guild).keys():
        await ctx.reply(embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True)
        return
    if not (ctx.author.id in trusted_users or not main_cache.get_problem(guild_id,problem_id).is_author() or ctx.author.guild_permissions.administrator):
        await ctx.reply(embed=ErrorEmbed("Insufficient permissions"), ephemeral=True)
        return
    main_cache.remove_problem("null", problem_id)
    await ctx.reply(embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"), ephemeral=True)
@slash.slash_command(name="add_trusted_user", description = "Adds a trusted user",options=[Option(name="user", description="The user you want to give super special bot access to", type=OptionType.USER, required=True)])
async def add_trusted_user(ctx,user):

    if ctx.author.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True)
        return
    if user.id in trusted_users:
        await ctx.reply(embed=ErrorEmbed(f"{user.name} is already a trusted user!"), ephemeral=True)
        return
    trusted_users.append(user.id)
    await ctx.reply(embed=ErrorEmbed(f"Successfully made {user.nick} a trusted user!"), ephemeral=True) 

@slash.slash_command(name="remove_trusted_user", description = "removes a trusted user",options=[Option(name="user", description="The user you want to take super special bot access from", type=OptionType.USER, required=True)])
async def remove_trusted_user(ctx,user):

    if ctx.author.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True)
        return
    if user.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed(f"{user.name} isn't a trusted user!", ephemeral=True))
        return
    trusted_users.pop(trusted_users.index(user.id))
    await ctx.reply(embed=ErrorEmbed(f"Successfully made {user.nick} no longer a trusted user!"), ephemeral=True) 


@slash.slash_command(name="ping", description = "Prints latency and takes no arguments")
async def ping(ctx):
    await ctx.reply(embed=SuccessEmbed(f"Pong! My latency is {round(bot.latency*1000)}ms."), ephemeral=True)
@slash.slash_command(name="what_is_vote_threshold", description="Prints the vote threshold and takes no arguments")
async def what_is_vote_threshold(ctx):
    await ctx.reply(embed=SuccessEmbed(f"The vote threshold is {vote_threshold}."),ephemeral=True)
@slash.slash_command(name="generate_invite_link", description = "Generates a invite link for this bot! Takes no arguments")
async def generateInviteLink(ctx):
    await ctx.reply(embed=SuccessEmbed("https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147552256&scope=bot%20applications.commands",successTitle),ephemeral=True)

@slash.slash_command(name="github_repo",description = "Returns the link to the github repo")
async def github_repo(ctx):
    await ctx.reply(embed=SuccessEmbed("[Repo Link:](https://github.com/rf20008/TheDiscordMathProblemBotRepo) ",successTitle="Here is the Github Repository Link."))
@slash.slash_command(name="raise_error", description = "⚠ This command will raise an error. Useful for checking on_slash_command_error", 
options=[Option(name="error_type",description = "The type of error", choices=[
    OptionChoice(name="Exception",value="Exception"),
    OptionChoice(name="UserError", value = "UserError")
    ],required=True), Option(name="error_description",description="The description of the error", type=OptionType.STRING,required=False)])
async def raise_error(ctx, error_type,error_description = None):
    if ctx.author.id not in trusted_users:
        await ctx.send(embed=ErrorEmbed(f"⚠ {ctx.author.mention}, you do not have permission to intentionally raise errors for debugging purposes.",custom_title="Insufficient permission to raise errors."))
        return
    if error_description == None:
        error_description = f"Manually raised error by {ctx.author.mention}"    
    if error_type == "Exception":
        error = Exception(error_description)
    elif error_type == "UserError":
        error=UserError(error_description)
    await ctx.send(embed=SuccessEmbed(f"Successfully created error: {str(error)}. Will now raise the error.", successTitle="Successfully raised error."))
    raise error
@slash.slash_command(name="documentation",description = "Returns help!", 
options=[Option(name="documentation_type", description = "What kind of help you want", choices= [
    OptionChoice(name = "documentation_link",value="documentation_link"),
    OptionChoice(name="command_help", value="command_help"),
    OptionChoice(name="function_help", value="function_help"),
    ],required=True),
    Option(name="help_obj", description = "What you want help on", required=True,type=OptionType.STRING)])
async def documentation(ctx,documentation_type, help_obj):
    fileBeginHelp = 0
    if documentation_type == "documentation_link":
        await ctx.reply(embed=SuccessEmbed(f"""<@{ctx.author.id}> [Click here](https://github.com/rf20008/TheDiscordMathProblemBotRepo/tree/master/docs) for my documentation.
    """),ephemeral=True)
        return None
    d = DocumentationFileLoader()
    try:
        documentation =d.get_documentation({"command_help":"docs/commands-documentation.md",
        "function_help":"docs/misc-non-commands-documentation.md"}[documentation_type], help_obj)
    except DocumentationNotFound as e:
        if isinstance(e,DocumentationFileNotFound):
            await ctx.reply(embed=ErrorEmbed("Documentation file was not found. Please report this error!"))
            return
        await ctx.reply(embed=ErrorEmbed(str(e)))
        return
    await ctx.reply(documentation)






print("The bot has finished setting up and will now run.")
#slash.run(DISCORD_TOKEN)
bot.run(DISCORD_TOKEN)
