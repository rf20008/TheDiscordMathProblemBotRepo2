import json
class DocumentationException(Exception):
  def _raise(self):
    raise self
class DocumentationNotFound(DocumentationException):
  pass
class DocumentationFileNotFound(DocumentationNotFound):
  pass

class DocumentationFileLoader:
  def __init__(self):
    pass
  def _load_documentation_file(self):
    e = ""
    with open("docs/documentation.json", "r") as file:
      for line in file:
        e+= str(line) + "\n"
    return json.loads(e)
  def load_documentation_into_readable_files(self):
    dictToStoreFileContent = {}
    docmentation_from_json = self._load_documentation_file()
    for item in documentation_from_json:
      dictToStoreFileContent[item["file_name"]] = "<! For you Github PR People, this file is dynamically generated from documentation.json. You should consider editing that instead :)>"
      if item["contains_legend"] == "true":
        dictToStoreFileContent[item["file_name"]] += """# Legend - global
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.

⚠: Only useable by global trusted users (such as /raise_error)

**: Not a bot/slash command (Documentation is here for purposes of me, and those who wish to fork my project/contribute with pull requests :))

***: This is a module/class. Cannot be called.

No Mark: This is a command without user restrictions"""
      item2 = item["contents"]
      for Item in item2:
        dictToStoreFileContent[item["file_name"]] += "\n" + "#" * item2["indentation"] + " " +item2["title"] + "\n"
        dictToStoreFileContent[item["contents"]]
    
    for documentationFileName in dictToStoreFileContent.keys():
      with open(documentationFileName,"w") as file:
        file.write(dictToStoreFileContent[documentationFileName])
    return documentation_from_json
  def get_documentation(self,documentationSource,documentationItem):
    _documentation = None
    documentation_from_json = self._load_documentation_file()
    for item in documentation_from_json.keys():
      if documentation_from_json[item]["file_name"] == documentationSource:
        _documentation = item
        break
    if _documentation == None:
      raise DocumentationFileNotFound("Documentation file not found")
    for item2 in documentation_from_json[item]:
      if item2["title"] == documentationItem:
        return item2["contents"]
    raise DocumentationNotFound(f"Documentation for {DocumentationItem} not found.")
    

  

