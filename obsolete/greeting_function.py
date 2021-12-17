
def say_hello(msg):
  greeting = msg.channel.send(f"Hello, {msg.author.name}! Sokka, the boomerang guy here.")
  return greeting
  