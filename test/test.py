import time
from gi.repository import Gio

t1 = time.time()
with open('file.txt') as file:
    file.read()
t2 = time.time()

print("open():", t2 - t1)

t3 = time.time()
file = Gio.File.new_for_path('file.txt')
io = file.load_contents(None)
t4 = time.time()

print("Gio.File():", t4-t3)
print(io[1])
