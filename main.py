import discord, math, random, requests, os
import time, datetime, json, aiohttp
#from discord_slash import SlashCommand, SlashContext
#import discord_slash
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
erroredInMainCode = False
#print("yes")
def print_current_time():
  e = datetime.datetime.now()

  print (e.strftime("%Y-%m-%d %H:%M:%S"),end=" ")
  print (e.strftime("%d/%m/%Y"),end=" ")
  print (e.strftime("%I:%M:%S %p"),end=" ")
  print (e.strftime("%a, %b %d, %Y"),end=" ")
def d():
  #print("e",flush=True)
  global mathProblems
  global trusted_users
  global vote_threshold
  with open("math_problems.json", "r") as file:
    mathProblems = json.load(fp=file)
  with open("trusted_users.txt", "r") as file:
    for line in file:
      trusted_users.append(int(line))
  with open("vote_threshold.txt") as file3:
    for line in file3:
      vote_threshold = int(line)
      print(line)
  #print("f")
  while True:  
    #print("o")
    time.sleep(60) 
    if erroredInMainCode:
      print("An error happened in the main code. Stopping the program...")
      exit()
      raise Exception
    print(f"Attempting to save files. The time is: ")
    print_current_time()
    with open("math_problems.json", "w") as file:
      file.write(json.dumps(mathProblems))
    with open("trusted_users.txt", "w") as file2:
      for user in trusted_users:
        file2.write(str(user))
        file2.write("\n")
        #print(user)

    with open("vote_threshold.txt") as file3:
      file.write(str(vote_threshold))
    
    print("Successfully saved files!")
      
t = threading.Thread(target=d,name="D",daemon=True)

t.start()
#print("Work please!!!!!")
#print(trusted_users)
def generate_new_id():
  return random.randint(0, 10**20)
#bot = commands.AutoShardedBot(command_prefix="math_problems.")
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands')

bot = commands.Bot(
    command_prefix = commands.when_mentioned_or('math_problems.'),
    help_command = help_command
)
#print("k")
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
  await ctx.channel.send("Something went wrong! Message the devs ASAP! (Our tags are ay136416#2707 and duck_master#8022)")
  raise error
  
##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list 
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")
class ProblemRelated(commands.Cog):
  "Problem related commands"
  @bot.command(help="""Creates a new math problem
  math_problems.new_problem <answer> <text>""",brief = "Adds a new math problem to the list!")
  async def new_problem(ctx, answer, *args):
    global mathProblems
    question = "".join(args)
    if len(question) > 250:
      await ctx.channel.send("Your question is too long! Therefore, it cannot be added. The maximum question length is 250 characters.")
      return
    while True:
      problem_id = generate_new_id()
      if problem_id not in mathProblems.keys():
        break

    e = {"answer": answer, "voters": [], "author": ctx.message.author.id, "solvers":[], "question": question}
    mathProblems[problem_id] = e
    await ctx.channel.send("You have successfully made a math problem!")

  @bot.command(help="""See if your answer is correct or not!
  math_problems.check_answer <problem_id> <answer>""", brief = "See if you got it right on a math problem")
  async def check_answer(ctx,problem_id,answer):
    global mathProblems
    try:
      if ctx.message.author.id in mathProblems[problem_id]["solvers"]:
        await ctx.channel.send("You have already solved this problem!")
        return
    except KeyError:
      await ctx.channel.send("This problem doesn't exist!")
      return

    if mathProblems[problem_id]["answer"] != answer:
      await ctx.channel.send("Sorry..... but you got it wrong! You can vote for the deletion of this problem if it's wrong or breaks copyright rules.")
    else:
      await ctx.channel.send("Yay! You are right.")
      mathProblems[problem_id]["solvers"].append(ctx.message.author.id)
  @bot.command(help = """List all problems stored with the bot! 
  math_problems.list_all_problems <showSolvedProblems=False>
  showSolvedProblems is whether or not to show solved problems. Cuts off after the 1931'st character.""", brief = "List all problems stored with the bot.")
  async def list_all_problems(ctx, showSolvedProblems=""):
    if showSolvedProblems != "":
      showSolvedProblems = True
    else:
      showSolvedProblems = False
    print(showSolvedProblems)
    if mathProblems.keys() == []:
      await ctx.channel.send("There aren't any problems! You should add one!")
      return
    elif showSolvedProblems == False and False not in [ctx.message.author.id in mathProblems[id]["solvers"] for id in mathProblems.keys()]:
      await ctx.channel.send("You solved all the problems! Add a new one!")
      return
    e = ""
    e += "Problem Id \t Question \t numVotes \t numSolvers"
    for question in mathProblems.keys():
      if len(e) >= 1930:
        e += "The combined length of the questions is too long.... shortening it!"
        await ctx.channel.send(e[:1930])
        return
      elif not (showSolvedProblems) and ctx.message.author.id in mathProblems[question]["solvers"]:
        continue
      e += "\n"
      e += str(question) + "\t"
      print(mathProblems[question])
      e += str(mathProblems[question]["question"]) + "\t"
      e += "(" 
      e+= str(len(mathProblems[question]["voters"])) + "/" + str(vote_threshold) + ")" + "\t"
      e += str(len(mathProblems[question]["solvers"])) + "\t"
    await ctx.channel.send(e[:1930])
class ModerationRelatedCommands(commands.Cog):
  @bot.command(help = """Sets the vote threshold for problem deletion to the specified value! (can only be used by trusted users)
  math_problems.set_vote_threshold <threshold>""", brief = "Changes the vote threshold")
  async def set_vote_threshold(ctx,threshold):
    global vote_threshold
    try:
      threshold = int(threshold)
    except:
      await ctx.channel.send("Invalid threshold argument!")
      return
    if ctx.message.author.id not in trusted_users:
      await ctx.channel.send("You aren't allowed to do this!")
      return
    if threshold <1:
      await ctx.channel.send("You can't set the threshold to smaller than 1.")
      return
    vote_threshold=int(threshold)
    for problem in mathProblems.keys():
      x = len(mathProblems[problem]["voters"])
      if x > vote_threshold:
        await ctx.channel.send(f"Successfully deleted problem #{problem} due to it having {x} votes, {x-threshold} more than the threshold!")
    await ctx.channel.send(f"The vote threshold has successfully been changed to {threshold}!")
  @bot.command(help = "Vote for a problem to be deleted! Once a problem gets more votes than the threshold, it gets deleted! Specify the problem_id in order that I know what problem you want deleted.", brief = "Vote for the deletion of a bad problem using this command")
  async def vote(ctx, problem_id):
    global mathProblems
    try:
      if ctx.message.author.id in mathProblems[problem_id]["voters"]:
        await ctx.channel.send("You have already voted for the deletion of this problem!")
        return
    except KeyError:
      await ctx.channel.send("This problem doesn't exist!")
      return
    mathProblems[problem_id]["voters"].append(ctx.message.author.id)
    e = "You successfully voted for the problem's deletion! As long as this problem is not deleted, you can always un-vote. There are "
    e += str(len(mathProblems[problem_id]["voters"]))
    e += "/"
    e+= str(vote_threshold)
    e += " votes on this problem!"
    await ctx.channel.send(e)
    if len(mathProblems[problem_id]["voters"]) >= vote_threshold:
      del mathProblems[problem_id]
      await ctx.channel.send("This problem has surpassed the threshold and has been deleted!")
  @bot.command(help = "Takes awsay your vote for the deletion of a problem (just specify problem id)",brief="Takes away a user's vote for the deletion of a problem")
  async def unvote(ctx,problem_id):
    global mathProblems
    try:
      if ctx.message.author.id not in mathProblems[problem_id]["voters"]:
        await ctx.channel.send("You aren't voting for the deletion of this problem!")
        return
    except KeyError:
      await ctx.channel.send("This problem doesn't exist!")
      return
    mathProblems[problem_id]["voters"].pop(mathProblems[problem_id]["voters"].index(ctx.message.author.id))
    await ctx.channel.send("Successfully un-voted for the problem's deletion!")
  @bot.command(help="""Deletes a question (either forcefully by a trusted user or deleting a problem submitted by the user who submitted this command
  math_problems.delete_problem  <problem_id> 
  Succeeds if trusted user or author of the problem, fails otherwise""", brief = "Deletes a question (either forcefully by a trusted user or deleting a problem submitted by the user who submitted this command")
  async def delete_problem(ctx, problem_id):
    global mathProblems
    user_id = ctx.message.author.id
    if problem_id not in mathProblems.keys():
      await ctx.channel.send("That problem doesn't exist! Use math_problems.list_problems to list all problems!")
      return
    if ctx.message.author.id not in trusted_users and mathProblems[problem_id]["author"] != ctx.message.author.id:
      await ctx.channel.send("You aren't a trusted user or the author of the problem!")
      return
    mathProblems.pop(problem_id)
    await ctx.channel.send(f"Successfully deleted problem #{problem_id}!")
  @bot.command(help="""Adds a trusted user (can only be used by trusted users)
  math_problems.add_trusted_user <user_nick>""", brief = "Adds a trusted user (can only be used by trusted users)")
  async def add_trusted_user(ctx,member: discord.Member = None):
    
    if ctx.message.author.id not in trusted_users:
      await ctx.channel.send("You aren't a trusted user!")
      return
    if member == None:
      await ctx.channel.send("Please mention a member to get them added!")
      return
    user_id = member.id
    if user_id == None:
      await ctx.channel.send(f"{user_nick} isn't a valid nickname of a user!")
      return
    #user_id = e.id
    if user_id in trusted_users:
      await ctx.channel.send(f"{bot.get_user(user_id).nick} is already a trusted user!")
      return
    trusted_users.append(trusted_users.index(user_id))
    await ctx.channel.send(f"Successfully made {bot.get_user(user_id).nick} no longer a trusted user!") 
  @bot.command(help="""Removes a trusted user (can only be used by trusted users)
  math_problems.remove_trusted_user <user_nick>""", brief = "Removes a trusted user (can only be used by trusted users)")
  async def remove_trusted_user(ctx,member: discord.Member = None):
    if ctx.message.author.id not in trusted_users:
      await ctx.channel.send("You aren't a trusted user!")
      return

    if member == None:
      await ctx.channel.send("Please mention a member to get them added!")
      return
    user_id = member.id
    if user_id == None:
      await ctx.channel.send(f"{user_nick} isn't a valid nickname of a user!")
      return
    #user_id = e.id
    if user_id not in trusted_users:
      await ctx.channel.send(f"{bot.get_user(user_id).nick} isn't a trusted user!")
      return
    trusted_users.pop(trusted_users.index(user_id))
    await ctx.channel.send(f"Successfully made {bot.get_user(user_id).nick} no longer a trusted user!") 
class miscellaneous(commands.Cog):
  @bot.command(help="Generates a invite link for this bot! Takes no arguments", brief = "Generates an invite link for this bot and takes no arguments")
  async def generate_invite_link(ctx):
    await ctx.channel.send("https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147552256&scope=bot%20applications.commands")
    return
  @bot.command(help="ping? prints latency and takes no arguments",
  brief = "prints latency and takes no arguments")
  async def ping(ctx):
    await ctx.channel.send(f"Pong! My latency is {round(bot.latency*1000)}ms.")
  @bot.command(help="Prints the vote threshold and takes no arguments", brief ="Prints the vote threshold and takes no arguments")
  async def what_is_vote_threshold(ctx):
    await ctx.channel.send(f"The vote threshold is {vote_threshold}.")
print("The bot has finished setting up and will now run.")
bot.run(DISCORD_TOKEN)
