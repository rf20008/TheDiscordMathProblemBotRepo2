class UserError(Exception):
  "This error was raised by a user in raise_error"
  def _raise(self):
    raise self
    