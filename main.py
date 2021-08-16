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
erroredInMainCode = False
#print("yes")
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
  with open("vote_threshold.txt", "r") as file3:
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
    
    print("Successfully saved files!")
      
t = threading.Thread(target=d,name="D",daemon=True)

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
  ctx.send("Attempting to delete bot problems",hidden=True)
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
  await ctx.defer(hidden=True)
  e = ""
  for trusted_user in trusted_users:
    e += "\n"
    e += str(bot.get_user(trusted_user))
  ctx.send(e, hidden=True)
@slash.slash(name="new_problem", description = "Create a new problem", options = [discord_slash.manage_commands.create_option(name="answer", description="The answer to this problem", option_type=4, required=True), discord_slash.manage_commands.create_option(name="question", description="your question", option_type=3, required=True)])
async def new_problem(ctx, answer, question):
  global mathProblems
  if len(question) > 250:
    await ctx.send("Your question is too long! Therefore, it cannot be added. The maximum question length is 250 characters.", hidden=True)
    return
  while True:
    problem_id = generate_new_id()
    if problem_id not in mathProblems.keys():
      break

  e = {"answer": answer, "voters": [], "author": 845751152901750824, "solvers":[], "question": question}
  mathProblems[problem_id] = e
  await ctx.send("You have successfully made a math problem!", hidden = True)

@slash.slash(name="check_answer", description = "Check if you are right", options=[discord_slash.manage_commands.create_option(name="problem_id", description="the id of the problem you are trying to check the answer of", option_type=4, required=True),discord_slash.manage_commands.create_option(name="answer", description="your answer", option_type=4, required=True)])
async def check_answer(ctx,problem_id,answer):
  global mathProblems
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
@slash.slash(name="list_all_problems", description = "List all problems stored with the bot", options=[discord_slash.manage_commands.create_option(name="show_solved_problems", description="Whether to show solved problems", option_type=5, required=False)])
async def list_all_problems(ctx, show_solved_problems=False):
  showSolvedProblems = show_solved_problems
  if showSolvedProblems != "":
    showSolvedProblems = True
  else:
    showSolvedProblems = False
  #print(showSolvedProblems)
  if mathProblems.keys() == []:
    await ctx.send("There aren't any problems! You should add one!", hidden=True)
    return
  elif showSolvedProblems == False and False not in [ctx.author_id in mathProblems[id]["solvers"] for id in mathProblems.keys()]:
    await ctx.send("You solved all the problems! You should add a new one.", hidden=True)
    return
  e = ""
  e += "Problem Id \t Question \t numVotes \t numSolvers"
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
@slash.slash(name="vote", description = "Vote for the deletion of a problem", options=[discord_slash.manage_commands.create_option(name="problem_id", description="problem id of the problem you are attempting to delete", option_type=4, required=True)])
async def vote(ctx, problem_id):
  global mathProblems
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
  global mathProblems
  try:
    if ctx.author_id not in mathProblems[problem_id]["voters"]:
      await ctx.send("You aren't voting for the deletion of this problem!", hidden=True)
      return
  except KeyError:
    await ctx.send("This problem doesn't exist!", hidden=True)
    return
  mathProblems[problem_id]["voters"].pop(mathProblems[problem_id]["voters"].index(ctx.author_id))
  await ctx.send(f"Successfully un-voted for the problem's deletion! Now there are {str(len(mathProblems[problem_id]['voters']))}/{vote_threshold} votes on the problem.", hidden=True)
slash.slash(name="delete_problem", description = "Deletes a problem", options = [discord_slash.manage_commands.create_option(name="problem_id", description="Problem ID!", option_type=4, required=True)])
async def delete_problem(ctx, problem_id):
  global mathProblems
  user_id = ctx.author_id
  if problem_id not in mathProblems.keys():
    await ctx.send("That problem doesn't exist! Use math_problems.list_problems to list all problems!", hidden=True)
    return
  if ctx.author_id not in trusted_users and mathProblems[problem_id]["author"] != ctx.author_id:
    await ctx.send("You aren't a trusted user or the author of the problem!", hidden=True)
    return
  mathProblems.pop(problem_id)
  await ctx.send(f"Successfully deleted problem #{problem_id}!", hidden=True)
@slash.slash(name="add_trusted_user", description = "adds a trusted user",options=[discord_slash.manage_commands.create_option(name="user", description="The user you want to give super special bot access to", option_type=6, required=True)])
async def add_trusted_user(ctx,user):
  member = user
  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't a trusted user!", hidden=True)
    return
  user_id = member.id
  if user_id == None:
    await ctx.send(f"{user_nick} isn't a valid nickname of a user!", hidden=True)
    return
  #user_id = e.id
  if user.id in trusted_users:
    await ctx.send(f"{member.nick} is already a trusted user!", hidden=True)
    return
  trusted_users.append(trusted_users.index(user.id))
  await ctx.send(f"Successfully made {user.nick} a trusted user!", hidden=True) 
@slash.slash(name="remove_trusted_user", description = "removes a trusted user",options=[discord_slash.manage_commands.create_option(name="user", description="The user you want to give super special bot access to", option_type=6, required=True)])
async def remove_trusted_user(ctx,user):
  member = user
  if ctx.author_id not in trusted_users:
    await ctx.send("You aren't a trusted user!", hidden=True)
    return
  user_id = member.id
  if user_id == None:
    await ctx.send(f"{user_nick} isn't a valid nickname of a user!", hidden=True)
    return
  #user_id = e.id
  if user_id not in trusted_users:
    await ctx.send(f"{user.nick} isn't a trusted user!", hidden=True)
    return
  trusted_users.pop(trusted_users.index(user_id))
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
@slash.slash(name="test", description="TEST!",        # Adding a new slash command with our slash variable
             options=[discord_slash.manage_commands.create_option(name="first_option", description="Testing!", option_type=3, required=False)])
async def test(ctx,first_option=-1):
  await ctx.send(first_option,hidden=True)
  return


print("The bot has finished setting up and will now run.")
bot.run(DISCORD_TOKEN)
