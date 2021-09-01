import json
class FileSaver:
  def __init__(self,name="",enabled=True,math_problems_file_name="math_problems.json",guild_math_problems_file_name="guild_math_problems.json",trusted_users_file_name="trusted_users.txt",vote_threshold_file_name="vote_threshold.txt"):
    self.enabled=True
    self.math_problems_file_name=math_problems_file_name
    self.guild_math_problems_file_name=guild_math_problems_file_name
    self.trusted_users_file_name=trusted_users_file_name
    self.vote_threshold_file_name=vote_threshold_file_name
    self.name=name
  def __str__(self):
    return self.name
  def enable(self):
    self.enabled=True
  def disable(self):
    self.enabled=False
  async def load_files(self,printSuccessMessages=False,guild_math_problems_dict,vote_threshold,math_problems_dict,trusted_users_list):
    if not self.enabled:
      raise RuntimeError("I'm not enabled! I can't save files!")

    if printSuccessMessages:
      print(f"{str(self)}: Attempting to save guild_math_problems_dict to{self.guild_math_problems_file_name}, vote_threshold to {self.vote_threshold_file_name}, trusted_users_list to {self.trusted_users_file_name}, and math_problems_dict to {self.math_problems_file_name}.")
    with open("math_problems.json", "r") as file:
      mathProblems = json.load(fp=file)
    with open("trusted_users.txt", "r") as file2:
      for line in file2:
        trusted_users.append(int(line))
    with open("vote_threshold.txt", "r") as file3:
      for line in file3:
        vote_threshold = int(line)
        
    with open("guild_math_problems.json", "r") as file4:
      guildMathProblems = json.load(fp=file4)

  #print("f")
  while True:  
    #print("o")
    time.sleep(45) 
    if erroredInMainCode:
      print("An error happened in the main code. Stopping the program...")
      exit()
      #raise Exception
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
      file4.write(e)
    