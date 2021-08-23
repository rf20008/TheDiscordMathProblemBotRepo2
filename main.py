import discord, math, random, os
import time, datetime, json, aiohttp, copy
from discord_slash import SlashCommand, SlashContext
import discord_slash
import threading
from discord.ext import commands, tasks
#constants
#print("Is it working??")
trusted_users=[]
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
#print(type(DISCORD_TOKEN))
#print(f"Discord Token: {DISCORD_TOKEN}")
vote_threshold = 1
mathProblems={}
guildMathProblems = {}
guild_maximum_problem_limit=125
erroredInMainCode = False
#print("yes")

def d():
  #print("e",flush=True)
  global mathProblems,guildMathProblems
  global trusted_users
  global vote_threshold
  with open("math_problems.json", "r") as file:
    mathProblems = json.load(fp=file)
  with open("trusted_users.txt", "r") as file2:
    for line in file2:
      trusted_users.append(int(line))
  with open("vote_threshold.txt", "r") as file3:
    for line in file3:
      vote_threshold = int(line)
      print(line)
  with open("guild_math_problems.json", "r") as file4:
    guildMathProblems = json.load(fp=file4)

  #print("f")
  while True:  
    #print("o")
    time.sleep(45) 
    if erroredInMainCode:
      print("An error happened in the main code. Stopping the program...")
      exit()
      raise Exception
    print(f"Attempting to save files.")
    with open("math_problems.json", "w") as file:
      file.write(json.dumps(mathProblems))
    with open("trusted_users.txt", "w") as file2:
      for user in trusted_users:
        file2.write(str(user))
        file2.write("\n")
        #print(user)

    with open("vote_threshold.txt", "w") as file3:
      file3.write(str(vote_threshold))
    with open("guild_math_problems.json", "w") as file4:
      e=json.dumps(obj=guildMathProblems)
      print(e)
      file4.write(e)
    
    print("Successfully saved files!")
      
t = threading.Thread(target=d,name="The File Saver",daemon=True)

t.start()



#print("Work please!!!!!")
#print(trusted_users)
def generate_new_id():
  return random.randint(0, 10**14)
#bot = commands.AutoShardedBot(command_prefix="math_problems.")
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands')

bot = commands.Bot(
    command_prefix = commands.when_mentioned_or('math_problems.'),
    help_command = help_command
)
slash = discord_slash.SlashCommand(bot, sync_commands=True)      # sync_commands is for doing synchronization for 
                                                                 # every command you add, remove or update in your
                                                                 # code
#print("k")


@bot.event
async def on_ready():
  print("The bot has connected to Discord successfully.")
@bot.event
async def on_slash_command_error(ctx, error):
  erroredInMainCode=True
  await ctx.send("Something went wrong! Message the devs ASAP! (Our tags are ay136416#2707 and duck_master#8022)", hidden=True)
  raise error

@bot.event
async def on_command_error(ctx,error):
  
  if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
    await ctx.channel.send("Not enough arguments!")
    return
  if isinstance(error, discord.ext.commands.errors.CommandNotFound):
    await ctx.channel.send("This command does not exist. Mention me and use help to get a list of all commands!")
    return
  print(type(error))
  erroredInMainCode=True
  await ctx.send("Something went wrong! Message the devs ASAP! (Our tags are ay136416#2707 and duck_master#8022)")
  raise error
@slash.slash(name="show_problem_info", description = "Show problem info", options=[discord_slash.manage_commands.create_option(name="problem_id", description="problem id of the problem you want to show", option_type=4, required=True),discord_slash.manage_commands.create_option(name="show_all_data", description="whether to show all data (only useable by problem authors and trusted users", option_type=5, required=False),discord_slash.manage_commands.create_option(name="raw", description="whether to show data as json?", option_type=5, required=False),discord_slash.manage_commands.create_option(name="is_guild_problem", description="whether the problem you are trying to view is a guild problem", option_type=5, required=False)])
async def show_problem_info(ctx, problem_id, show_all_data=False, raw=False,is_guild_problem=False):
  problem_id = int(problem_id)

  guild_id = str(ctx.guild_id)
  if guild_id not in guildMathProblems:
    guildMathProblems[guild_id]={}
  if is_guild_problem:
    if guild_id == None:
      ctx.send("Run this command in the discord server which has this problem, not a DM!")
      return
    if guild_id not in guildMathProblems.keys():
      guildMathProblems[guild_id] = {}
    if problem_id not in guildMathProblems[guild_id].keys():
      await ctx.send("Problem non-existant!")
      return

    if show_all_data:
      if not (ctx.author_id == guildMathProblems[guild_id][problem_id]["author"] or ctx.author_id not in trusted_users or (is_guild_problem and ctx.author.guild_permissions.administrator == True)):
        await ctx.send("Insufficient permissions!", hidden=True)
        return

    if raw:
      await ctx.send(str(mathProblems[problem_id]), hidden=True)
      return
  if problem_id not in mathProblems.keys():
    await ctx.send("Problem non-existant!")
    return
  if show_all_data:
    if not (ctx.author_id == mathProblems[problem_id]["author"] or ctx.author_id not in trusted_users or (is_guild_problem and ctx.author.guild_permissions.administrator == True)):
      await ctx.send("Insufficient permissions!", hidden=True)
      return
    if raw:
      await ctx.send(str(mathProblems[problem_id]), hidden=True)
      return
    e= "Question: "
    e += mathProblems[problem_id]["question"] 
    e+= "\nAuthor: "
    e+= str(mathProblems[problem_id]["author"])
    e+= "\nNumVoters/Vote Threshold: ("
    e+= str(len(mathProblems[problem_id]["voters"]))
    e+= "/"
    e += str(vote_threshold)
    e+= ") \nNumSolvers: "
    e+= str(len(mathProblems[problem_id]["solvers"]))
    e+= "\nAnswer: "
    e+= str(mathProblems[problem_id]["answer"])
    await ctx.send(e, hidden=True)
  else:
    if raw:
      g = copy.deepcopy(mathProblems[problem_id])
      g.pop("answer")
      await ctx.send(str(g), hidden=True)
      return
    e= "Question: "
    e += mathProblems[problem_id]["question"] 
    e+= "\nAuthor: "
    e+= str(mathProblems[problem_id]["author"])
    e+= "\nNumVoters/Vote Threshold: ("
    e+= str(len(mathProblems[problem_id]["voters"]))
    e+= "/"
    e += str(vote_threshold)
    e+= ") \nNumSolvers: "
    e+= str(len(mathProblems[problem_id]["solvers"]))
  
    await ctx.send(e, hidden=True)
@slash.slash(name="list_all_problem_ids", description= "List all problem ids", options=[discord_slash.manage_commands.create_option(name="show_only_guild_problems", description="Whether to show guild problem ids",required=False,option_type=5)])
async def list_all_problem_ids(ctx,show_only_guild_problems=False):
  await ctx.defer()
  if show_only_guild_problems:
    guild_id = str(ctx.guild_id)
    if guild_id == None:
      await ctx.send("Run this command in a Discord server or set show_only_guild_problems to False!", hidden=True)
      return
    await ctx.send("\n".join([str(item) for item in mathProblems.keys()])[:1930])
    return

  await ctx.send("\n".join([str(item) for item in mathProblems.keys()])[:1930])
@slash.slash(name="generate_new_problems", description= "Generates new problems", options=[discord_slash.manage_commands.create_option(name="num_new_problems_to_generate", description="the number of problems that should be generated", option_type=4, required=True)])
async def generate_new_problems(ctx, num_new_problems_to_generate):
  await ctx.defer()
  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't trusted!",hidden=True)
    return
  elif num_new_problems_to_generate > 200:
    await ctx.send("You are trying to create too many problems. Try something smaller than or equal to 200.", hidden=True)
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
    e = {"answer": answer, "voters": [], "author": 845751152901750824, "solvers":[], "question": (str(num1) +" " +  str(operation) + " "+ str(num2) + " (Was automatically created by the bot).")}
    while True:
      problem_id = generate_new_id()
      if problem_id not in mathProblems.keys():
        break
    mathProblems[problem_id] = e
  await ctx.send("Successfully created new problems.", hidden=True)
##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list 
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")
@slash.slash(name="delallbotproblems", description = "delete all automatically generated problems")
async def delallbotproblems(ctx):
  await ctx.send("Attempting to delete bot problems",hidden=True)
  global mathProblems
  mathProblems2 = copy.deepcopy(mathProblems)
  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't trusted", hidden=True)
    return
  numDeletedProblems = 0
  f = mathProblems.keys()
  for e in f:
    if mathProblems2[e]["author"] == 845751152901750824:
      mathProblems2.pop(e)
      numDeletedProblems += 1
  mathProblems = mathProblems2
  await ctx.send(f"Successfully deleted {numDeletedProblems}!")
@slash.slash(name = "list_trusted_users", description = "list all trusted users")
async def list_trusted_users(ctx):

  await ctx.send("\n".join([str(item) for item in trusted_users]))
@slash.slash(name="new_problem", description = "Create a new problem", options = [discord_slash.manage_commands.create_option(name="answer", description="The answer to this problem", option_type=4, required=True), discord_slash.manage_commands.create_option(name="question", description="your question", option_type=3, required=True),discord_slash.manage_commands.create_option(name="guild_question", description="Whether it should be a question for the guild", option_type=5, required=False)])
async def new_problem(ctx, answer, question, guild_question=False):
  global mathProblems, guildMathProblems
  if len(question) > 250:
    await ctx.send("Your question is too long! Therefore, it cannot be added. The maximum question length is 250 characters.", hidden=True)
    return
  
  if guild_question:
    guild_id = str(ctx.guild_id)
    if guild_id == None:
      await ctx.send("You need to be in the guild to make a guild question!")
      return
    if guild_id not in guildMathProblems.keys():
      guildMathProblems[guild_id] = {}
    elif len(guildMathProblems[guild_id]) >= guild_maximum_problem_limit:
      await ctx.send("You have reached the guild math problem limit.")
      return
    while True:
      problem_id = generate_new_id()
      if problem_id not in guildMathProblems[guild_id].keys():
        break
    e = {"answer": answer, "voters": [], "author": ctx.author_id, "solvers":[], "question": question}
    print(e)
    guildMathProblems[guild_id][problem_id] = e
    print(guildMathProblems[guild_id][problem_id])
    await ctx.send("You have successfully made a math problem!", hidden = True)
    return
  while True:
    problem_id = generate_new_id()
    if problem_id not in mathProblems.keys():
      break
  e = {"answer": answer, "voters": [], "author": ctx.author_id, "solvers":[], "question": question}
  mathProblems[problem_id] = e
  await ctx.send("You have successfully made a math problem!", hidden = True)

@slash.slash(name="check_answer", description = "Check if you are right", options=[discord_slash.manage_commands.create_option(name="problem_id", description="the id of the problem you are trying to check the answer of", option_type=4, required=True),discord_slash.manage_commands.create_option(name="answer", description="your answer", option_type=4, required=True),discord_slash.manage_commands.create_option(name="checking_guild_problem", description="whether checking a guild problem", option_type=5, required = False)])
async def check_answer(ctx,problem_id,answer, checking_guild_problem=False):
  global mathProblems,guildMathProblems
  try:
    if ctx.author_id in mathProblems[problem_id]["solvers"]:
      await ctx.send("You have already solved this problem!", hidden = True)
      return
  except KeyError:
    await ctx.send("This problem doesn't exist!", hidden=True)
    return

  if mathProblems[problem_id]["answer"] != answer:
    await ctx.send("Sorry..... but you got it wrong! You can vote for the deletion of this problem if it's wrong or breaks copyright rules.", hidden=True)
  else:
    await ctx.send("Yay! You are right.", hidden=True)
    mathProblems[problem_id]["solvers"].append(ctx.author_id)
@slash.slash(name="list_all_problems", description = "List all problems stored with the bot", options=[discord_slash.manage_commands.create_option(name="show_solved_problems", description="Whether to show solved problems", option_type=5, required=False),discord_slash.manage_commands.create_option(name="show_guild_problems", description="Whether to show solved problems", option_type=5, required=False),discord_slash.manage_commands.create_option(name="show_only_guild_problems", description="Whether to only show guild problems", option_type=5, required=False)])
async def list_all_problems(ctx, show_solved_problems=False,show_guild_problems=True,show_only_guild_problems=False):
  showSolvedProblems = show_solved_problems
  guild_id = str(ctx.guild_id)
  if guild_id not in guildMathProblems:
    guildMathProblems[guild_id]={}
  if showSolvedProblems != "":
    showSolvedProblems = True
  else:
    showSolvedProblems = False
  #print(showSolvedProblems)
  if mathProblems.keys() == []:
    await ctx.send("There aren't any problems! You should add one!", hidden=True)
    return
  #if not showSolvedProblems and False not in [ctx.author_id in mathProblems[id]["solvers"] for id in mathProblems.keys()] or (show_guild_problems and (show_only_guild_problems and (guildMathProblems[str(ctx.guild_id)] == {}) or False not in [ctx.author_id in guildMathProblems[guild_id][id]["solvers"] for id in guildMathProblems[guild_id].keys()])) or show_guild_problems and not show_only_guild_problems and False not in [ctx.author_id in mathProblems[id]["solvers"] for id in mathProblems.keys()] and False not in [ctx.author_id in guildMathProblems[guild_id][id]["solvers"] for id in guildMathProblems[guild_id].keys()]:
    #await ctx.send("You solved all the problems! You should add a new one.", hidden=True)
    #return
  e = ""
  e += "Problem Id \t Question \t numVotes \t numSolvers"
  if show_guild_problems:
    for question in guildMathProblems[guild_id].keys():
      if len(e) >= 1930:
        e += "The combined length of the questions is too long.... shortening it!"
        await ctx.send(e[:1930])
        return
      elif not (showSolvedProblems) and ctx.author_id in guildMathProblems[guild_id][question]["solvers"]:
        continue
      e += "\n"
      e += str(question) + "\t"
      e += str(guildMathProblems[guild_id][question]["question"]) + "\t"
      e += "(" 
      e+= str(len(guildMathProblems[guild_id][question]["voters"])) + "/" + str(vote_threshold) + ")" + "\t"
      e += str(len(guildMathProblems[guild_id][question]["solvers"])) + "\t"
      e += "(guild)"
  if len(e) > 1930:
    await ctx.send(e[:1930])
    return
  if show_only_guild_problems:
    await ctx.send(e[:1930])
    return

  for question in mathProblems.keys():
    if len(e) >= 1930:
      e += "The combined length of the questions is too long.... shortening it!"
      await ctx.send(e[:1930])
      return
    elif not (showSolvedProblems) and ctx.author_id in mathProblems[question]["solvers"]:
      continue
    e += "\n"
    e += str(question) + "\t"
    #print(mathProblems[question])
    e += str(mathProblems[question]["question"]) + "\t"
    e += "(" 
    e+= str(len(mathProblems[question]["voters"])) + "/" + str(vote_threshold) + ")" + "\t"
    e += str(len(mathProblems[question]["solvers"])) + "\t"
  await ctx.send(e[:1930])

@slash.slash(name = "set_vote_threshold", description = "Sets the vote threshold", options=[discord_slash.manage_commands.create_option(name="threshold", description="the threshold you want to change it to", option_type=4, required=True)])
async def set_vote_threshold(ctx,threshold):
  global vote_threshold
  try:
    threshold = int(threshold)
  except:
    await ctx.send("Invalid threshold argument!", hidden=True)
    return
  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't allowed to do this!", hidden=True)
    return
  if threshold <1:
    await ctx.send("You can't set the threshold to smaller than 1.", hidden=True)
    return
  vote_threshold=int(threshold)
  for problem in mathProblems.keys():
    x = len(mathProblems[problem]["voters"])
    if x > vote_threshold:
      await ctx.send(f"Successfully deleted problem #{problem} due to it having {x} votes, {x-threshold} more than the threshold!", hidden=True)
  await ctx.send(f"The vote threshold has successfully been changed to {threshold}!", hidden=True)
@slash.slash(name="vote", description = "Vote for the deletion of a problem", options=[discord_slash.manage_commands.create_option(name="problem_id", description="problem id of the problem you are attempting to delete", option_type=4, required=True),discord_slash.manage_commands.create_option(name="is_guild_problem", description="problem id of the problem you are attempting to delete", option_type=5, required=False)])
async def vote(ctx, problem_id,is_guild_problem=False):
  global mathProblems, guildMathProblems
  if is_guild_problem:
    guild_id = str(ctx.guild_id)
    try:
      if ctx.author_id in guildMathProblems[guild_id][problem_id]["voters"]:
        await ctx.send("You have already voted for the deletion of this problem!", hidden=True)
        return
    except KeyError:
      await ctx.send("This problem doesn't exist!", hidden=True)
      return
    if guild_id == None:
      await ctx.send("You need to be in the guild to make a guild question!")
      return
    if guild_id not in guildMathProblems.keys():
      guildMathProblems[guild_id] = {}
    try:
      if ctx.author_id in guildMathProblems[guild_id][problem_id]["voters"]:
        await ctx.send("You have already voted for the deletion of this problem!", hidden=True)
        return
    except KeyError:
      await ctx.send("This problem doesn't exist!", hidden=True)
      return
    guildMathProblems[guild_id][problem_id]["voters"].append(ctx.author_id)
    e = "You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    e += str(len(guildMathProblems[guild_id][problem_id]["voters"]))
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem!"
    await ctx.send(e, hidden=True)
    if len(mathProblems[problem_id]["voters"]) >= vote_threshold:

      await ctx.send("This problem has surpassed the threshold and has been deleted!", hidden=True)  
  try:
    if ctx.author_id in mathProblems[problem_id]["voters"]:
      await ctx.send("You have already voted for the deletion of this problem!", hidden=True)
      return
  except KeyError:
    await ctx.send("This problem doesn't exist!", hidden=True)
    return
  mathProblems[problem_id]["voters"].append(ctx.author_id)
  e = "You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
  e += str(len(mathProblems[problem_id]["voters"]))
  e += "/"
  e+= str(vote_threshold)
  e += " votes on this problem!"
  await ctx.send(e, hidden=True)
  if len(mathProblems[problem_id]["voters"]) >= vote_threshold:
    del mathProblems[problem_id]
    await ctx.send("This problem has surpassed the threshold and has been deleted!", hidden=True)
@slash.slash(name="unvote", description = "takes away vote for the deletion of a problem", options=[discord_slash.manage_commands.create_option(name="problem_id", description="Problem ID!", option_type=4, required=True)])
async def unvote(ctx,problem_id):
  global mathProblems, guildMathProblems
  if is_guild_problem:
    guild_id = str(ctx.guild_id)
    if guild_id == None:
      await ctx.send("You need to be in the guild to make a guild question!")
      return
    if guild_id not in guildMathProblems.keys():
      guildMathProblems[guild_id] = {}
    try:
      if ctx.author_id not in guildMathProblems[guild_id][problem_id]["voters"]:
        await ctx.send("You have not voted for the deletion of this problem!", hidden=True)
        return
    except KeyError:
      await ctx.send("This problem doesn't exist!", hidden=True)
      return
    guildMathProblems[guild_id][problem_id]["voters"].append(ctx.author_id)
    e = "You successfully unvoted for the problem's deletion! Now there are"
    e += str(len(guildMathProblems[guild_id][problem_id]["voters"]))
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem."
    await ctx.send(e, hidden=True)
  try:
    if ctx.author_id in mathProblems[problem_id]["voters"]:
      await ctx.send("You have not yet voted for the deletion of this problem!", hidden=True)
      return
  except KeyError:
    await ctx.send("This problem doesn't exist!", hidden=True)
    return
  mathProblems[problem_id]["voters"].append(ctx.author_id)
  e = "You successfully unvoted for the deletion of this problem. There are now "
  e += str(len(mathProblems[problem_id]["voters"]))
  e += "/"
  e+= str(vote_threshold)
  e += " votes on this problem."
  await ctx.send(e, hidden=True)
@slash.slash(name="delete_problem", description = "Deletes a problem", options = [discord_slash.manage_commands.create_option(name="problem_id", description="Problem ID!", option_type=4, required=True),discord_slash.manage_commands.create_option(name="is_guild_problem", description="whether deleting a guild problem", option_type=5, required=False)])
async def delete_problem(ctx, problem_id,is_guild_problem=False):
  global mathProblems, guildMathProblems
  user_id = ctx.author_id
  guild_id = str(ctx.guild_id)
  if is_guild_problem:
    if guild_id == None:
      await ctx.send("Run this command in the discord server which has the problem you are trying to delete, or switch is_guild_problem to False.")
      return
    if problem_id not in guildMathProblems[guild_id].keys():
      await ctx.send("That problem doesn't exist.", hidden=True)
      return
    if not (ctx.author_id in trusted_users or mathProblems[problem_id]["author"]!= ctx.author_id or ctx.author.guild_permissions.administrator):
      await ctx.send("Insufficient permissions", hidden=True)
      return
    guildMathProblems[guild_id].pop(problem_id)
    await ctx.send(f"Successfully deleted problem #{problem_id}!", hidden=True)
  if problem_id not in mathProblems.keys():
    await ctx.send("That problem doesn't exist.", hidden=True)
    return
  if ctx.author_id not in trusted_users and mathProblems[problem_id]["author"] != ctx.author_id:
    await ctx.send("You aren't a trusted user or the author of the problem!", hidden=True)
    return
  mathProblems.pop(problem_id)
  await ctx.send(f"Successfully deleted problem #{problem_id}!", hidden=True)
@slash.slash(name="add_trusted_user", description = "Adds a trusted user",options=[discord_slash.manage_commands.create_option(name="user", description="The user you want to give super special bot access to", option_type=6, required=True)])
async def remove_trusted_user(ctx,user):

  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't a trusted user!", hidden=True)
    return
  if user.id in trusted_users:
    await ctx.send(f"{user.name} is already a trusted user!", hidden=True)
    return
  trusted_users.append(user.id)
  await ctx.send(f"Successfully made {user.nick} a trusted user!", hidden=True) 

@slash.slash(name="remove_trusted_user", description = "removes a trusted user",options=[discord_slash.manage_commands.create_option(name="user", description="The user you want to take super special bot access from", option_type=6, required=True)])
async def remove_trusted_user(ctx,user):

  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't a trusted user!", hidden=True)
    return
  if user.id not in trusted_users:
    await ctx.send(f"{user.name} isn't a trusted user!", hidden=True)
    return
  trusted_users.pop(trusted_users.index(user.id))
  await ctx.send(f"Successfully made {user.nick} no longer a trusted user!", hidden=True) 


@slash.slash(name="ping", description = "Prints latency and takes no arguments")
async def ping(ctx):
  await ctx.send(f"Pong! My latency is {round(bot.latency*1000)}ms.", hidden=True)
@slash.slash(name="what_is_vote_threshold", description="Prints the vote threshold and takes no arguments")
async def what_is_vote_threshold(ctx):
  await ctx.send(f"The vote threshold is {vote_threshold}.",hidden=True)
@slash.slash(name="generateInviteLink", description = "Generates a invite link for this bot! Takes no arguments")
async def generateInviteLink(ctx):
  await ctx.send("https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147552256&scope=bot%20applications.commands",hidden=True)
#slash.slash(name="test", description="TEST!",        # Adding a new slash command with our slash variable
#             options=[discord_slash.manage_commands.create_option(name="first_option", description="Testing!", option_type=3, required=False)])
#async def test(ctx,first_option=-1):
#  await ctx.send(first_option,hidden=True)
# return


print("The bot has finished setting up and will now run.")
bot.run(DISCORD_TOKEN)
