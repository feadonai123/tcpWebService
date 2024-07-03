def readFile(path):
  with open(path, "r") as file:
    return file.read()
  
  
def readImageAsBinary(path):
  with open(path, "rb") as file:
    return file.read()
  
def exists(path):
  try:
    with open(path, "r") as file:
      return True
  except:
    return False