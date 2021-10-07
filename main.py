import random, os, warnings, threading, copy, nextcord, subprocess
from dislash.application_commands.core import check
import dislash, traceback
import return_intents
import nextcord.ext.commands as nextcord_commands
import problems_module, custom_embeds, save_files, the_documentation_file_loader
from cogs import developer_commands
from cooldowns import check_for_cooldown, OnCooldown
from _error_logging import log_error
from dislash import InteractionClient, Option, OptionType, NotOwner, OptionChoice
from time import sleep, time, asctime
from custom_embeds import *
from save_files import FileSaver
from user_error import UserError
from the_documentation_file_loader import *
from problems_module import get_main_cache




warnings.simplefilter("default")
#constants

trusted_users=[]
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

main_cache = get_main_cache()
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
t = threading.Thread(target=loading_documentation_thread)
t.start()

def get_git_revision_hash() -> str:
    "A method that gets the git revision hash. Credit to https://stackoverflow.com/a/21901260 for the code :-)"
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()[:7] #[7:] is here because of the commit hash, the rest of this function is from stack overflow

def the_daemon_file_saver():

    global guildMathProblems, trusted_users,vote_threshold
    
    FileSaverObj = FileSaver(name = "The Daemon File Saver",
                             enabled=True,
                             printSuccessMessagesByDefault=True)
    FileSaverDict = FileSaverObj.load_files(main_cache,True)
    (guildMathProblems,
     trusted_users,
     vote_threshold) = (
        FileSaverDict["guildMathProblems"],
        FileSaverDict["trusted_users"],
        FileSaverDict["vote_threshold"])

    while True: 
        sleep(45) 
        FileSaverObj.save_files(main_cache,False,guildMathProblems,vote_threshold,mathProblems,trusted_users)

            
t = threading.Thread(target=the_daemon_file_saver,name="The File Saver",daemon=True)

t.start()

def generate_new_id():
    return random.randint(0, 10**14)
Intents = return_intents.return_intents()
bot = nextcord_commands.Bot(
        " ",intents=Intents
)
bot.main_cache = main_cache
bot.trusted_users = trusted_users
bot._transport_modules = {"problems_module": problems_module,"save_files": save_files, "the_documentation_file_loader": the_documentation_file_loader, "check_for_cooldown": check_for_cooldown, "custom_embeds": custom_embeds}
bot.add_cog(developer_commands.DeveloperCommands(bot))
#bot.load_extension("jishaku")


slash = InteractionClient(client=bot,sync_commands=True)
print("Bots successfully created.")


@bot.event
async def on_ready():
    print("The bot has connected to Discord successfully.")

@bot.event
async def on_slash_command_error(ctx, error):
    "Function called when a command errors"
    if isinstance(error,OnCooldown):
        await ctx.reply(str(error))
        return
    error_traceback = (traceback.format_exception(etype=type(error),value=error,tb=error.__traceback__))
    log_error(error) # Log the error
    if isinstance(error,NotOwner):
        await ctx.reply(embed=ErrorEmbed("You are not the owner of this bot."))
        return
    #Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))
    
    _error_traceback = ""
    for item in error_traceback:
      _error_traceback += item
      _error_traceback += "\n"
    
    await ctx.reply(embed=ErrorEmbed(
        _error_traceback,
        custom_title="Oh, no! An exception occurred", 
        footer=f"Time: {str(asctime())} Commit hash: {get_git_revision_hash()} "))



    


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
        if is_guild_problem and guild_id == None:
            embed1= ErrorEmbed( description = "Run this command in the discord server which has this problem, not a DM!")
            ctx.reply(embed=embed1)
            return
        if guild_id not in main_cache.get_guilds():
            main_cache.add_empty_guild(guild_id)
        problem = main_cache.get_problem(str(ctx.guild.id) if is_guild_problem else "null",
                                         str(problem_id))
        Problem__ = f"Question: {problem.get_question()}\nAuthor: {str(problem.get_author())}\nNumVoters/Vote Threshold: {problem.get_num_voters()}/{vote_threshold}\nNumSolvers: {len(problem.get_solvers())}"
        
        if show_all_data:
            if not ((problem.is_author(ctx.author) or ctx.author.id not in trusted_users or (
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
        if guild_id == None:
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

    if ctx.author.id not in trusted_users:
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
    for item in trusted_users:
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
        t2=threading.Thread(target=main_cache.remove_duplicate_problems)
        t2.start()
        return
    if guild_question:
        guild_id = ctx.guild.id
        if guild_id == None:
            await ctx.reply(embed=ErrorEmbed("You need to be in the guild to make a guild question!"))
            return

        if guild_id not in main_cache.get_guilds():
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
          id=problem_id,
          author=ctx.author.id,
          guild_id=guild_id,
          cache = main_cache
        )
        main_cache.add_problem(guild_id=guild_id,
                               problem_id=problem_id,
                               Problem=problem)
        

        await ctx.reply(embed=SuccessEmbed("You have successfully made a math problem!",
                                           successTitle="Successfully made a new math problem."),
                        ephemeral = True)

        return
    while True:
        problem_id = generate_new_id()
        if problem_id not in [problem.id for problem in main_cache.get_global_problems()]:
            break
    

    problem = problems_module.MathProblem(question=question
                                          ,answer=answer,
                                          id=problem_id,
                                          guild_id="null",
                                          author=ctx.author.id,
                                          cache = main_cache)
    main_cache.add_problem(problem_id=problem_id,
                           guild_id=problem.guild_id,
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
    print(3)

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
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)

    showSolvedProblems = show_solved_problems
    guild_id = ctx.guild.id
    if guild_id not in guildMathProblems:
        guildMathProblems[guild_id]={}
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
            if not (showSolvedProblems) and problem.is_solver(ctx.author):
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
        if not (showSolvedProblems) and problem.is_solver(ctx.author):
            continue
        e += "\n"
        e += str(problem.id) + "\t"
        e += str(problem.get_question()) + "\t"
        e += "(" 
        e+= str(problem.get_num_voters()) + "/" + str(vote_threshold) + ")" + "\t"
        e += str(len(problem.get_solvers())) + "\t"
    await ctx.reply(embed=SuccessEmbed(e[:1930]))

@slash.slash_command(name = "set_vote_threshold", description = "Sets the vote threshold", options=[
    Option(name="threshold", description="the threshold you want to change it to",
           type=OptionType.INTEGER, required=True)])
async def set_vote_threshold(ctx,threshold):
    "Set the vote threshold"
    await check_for_cooldown(ctx,"")
    if ctx.guild != None and ctx.guild.id not in main_cache.get_guilds():
        main_cache.add_empty_guild(ctx.guild)
    global vote_threshold
    try:
        threshold = int(threshold)
    except TypeError:
        await ctx.reply(embed=ErrorEmbed(
            "Invalid threshold argument! (threshold must be an integer)"),
                        ephemeral=True)
        return
    if ctx.author.id not in trusted_users:
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
    e = "You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    e += str(problem.get_num_voters())
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem!"
    await ctx.reply(embed=SuccessEmbed(e), ephemeral=True)
    if problem.get_num_voters() >= vote_threshold:
        del mathProblems[problem_id]
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
        if guild_id == None:
            await ctx.reply(embed=ErrorEmbed(
                "Run this command in the discord server which has the problem you are trying to delete, or switch is_guild_problem to False."
                ))
            return
        if problem_id not in main_cache.get_guild_problems(ctx.guild).keys():
            await ctx.reply(embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True)
            return
        if not (ctx.author.id in trusted_users or not (
            main_cache.get_problem(str(guild_id),str(problem_id)).is_author()
            ) or (ctx.author.guild_permissions.administrator)):
            await ctx.reply(embed=ErrorEmbed("Insufficient permissions"), ephemeral=True)
            return
        main_cache.remove_problem(str(guild_id), problem_id)
        await ctx.reply(
            embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"),
            ephemeral=True)
    if guild_id == None:
        await ctx.reply(embed=ErrorEmbed(
            "Run this command in the discord server which has the problem, or switch is_guild_problem to False."))
        return
    if problem_id not in main_cache.get_guild_problems(ctx.guild).keys():
        await ctx.reply(embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True)
        return
    if not (ctx.author.id in trusted_users or not
            (main_cache.get_problem(guild_id,problem_id).is_author())
            or ctx.author.guild_permissions.administrator):
        await ctx.reply(embed=ErrorEmbed("Insufficient permissions"), ephemeral=True)
        return
    main_cache.remove_problem("null", problem_id)
    await ctx.reply(embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"), ephemeral=True)
@slash.slash_command(name="add_trusted_user", description = "Adds a trusted user",options=[
    Option(name="user", description="The user you want to give super special bot access to",
           type=OptionType.USER,
           required=True)])
async def add_trusted_user(ctx,user):
    "Add a trusted user"
    await check_for_cooldown(ctx,"add_trusted_user",600)
    if ctx.author.id not in trusted_users:
        await ctx.reply(embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True)
        return
    if user.id in trusted_users:
        await ctx.reply(embed=ErrorEmbed(f"{user.name} is already a trusted user!"),
                        ephemeral=True)
        return
    trusted_users.append(user.id)
    await ctx.reply(embed=ErrorEmbed(f"Successfully made {user.nick} a trusted user!"), ephemeral=True) 

@slash.slash_command(name="remove_trusted_user", description = "removes a trusted user",options=
                     [Option(
                         name="user",
                         description="The user you want to take super special bot access from",
                         type=OptionType.USER, required=True)])
async def remove_trusted_user(ctx,user):
    "Remove a trusted user"
    await check_for_cooldown(ctx,"remove_trusted_user",600)
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



print("The bot has finished setting up and will now run.")
#slash.run(DISCORD_TOKEN)
bot.run(DISCORD_TOKEN)
