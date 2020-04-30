from django.contrib.auth.models import User
from adventure.models import Player, Room


TILE_EMPTY = 'X'
TILE_CRATE = '_'


""" Code to make the maze """

def create_empty_grid(width, height, default_value=TILE_EMPTY):
    grid = []
    for row in range(height):
        grid.append([])
        for column in range(width):
            grid[row].append(default_value)
    return grid

def create_outside_walls(maze):
    for row in range(len(maze)):
        maze[row][0] = TILE_CRATE
        maze[row][len(maze[row])-1] = TILE_CRATE

    for column in range(1, len(maze[0]) - 1):
        maze[0][column] = TILE_CRATE
        maze[len(maze) - 1][column] = TILE_CRATE

def make_maze_recursive_call(maze, top, bottom, left, right):

    start_range = bottom + 2
    end_range = top - 1
    y = random.randrange(start_range, end_range, 2)

    for column in range(left + 1, right):
        maze[y][column] = TILE_CRATE
    start_range = left + 2
    end_range = right - 1
    x = random.randrange(start_range, end_range, 2)
    
    for row in range(bottom + 1, top):
        maze[row][x] = TILE_CRATE


    wall = random.randrange(4)
    if wall != 0:
        gap = random.randrange(left + 1, x, 2)
        maze[y][gap] = TILE_EMPTY
    if wall != 1:
        gap = random.randrange(x + 1, right, 2)
        maze[y][gap] = TILE_EMPTY
    if wall != 2:
        gap = random.randrange(bottom + 1, y, 2)
        maze[gap][x] = TILE_EMPTY
    if wall != 3:
        gap = random.randrange(y + 1, top, 2)
        maze[gap][x] = TILE_EMPTY


    if top > y + 3 and x > left + 3:
        make_maze_recursive_call(maze, top, y, left, x)
    if top > y + 3 and x + 3 < right:
        make_maze_recursive_call(maze, top, y, x, right)
    if bottom + 3 < y and x + 3 < right:
        make_maze_recursive_call(maze, y, bottom, x, right)
    if bottom + 3 < y and x > left + 3:
        make_maze_recursive_call(maze, y, bottom, left, x)


def make_maze_recursion(maze_width, maze_height):

    maze = create_empty_grid(maze_width, maze_height)
    create_outside_walls(maze)
    make_maze_recursive_call(maze, maze_height - 1, 0, 0, maze_width - 1)
    return maze


""" Get a list of points around a given point """

def around_list(point):
    above = [point[0], point[1] -1]
    below = [point[0], point[1] + 1]
    right = [point[0] + 1, point[1]] 
    left = [point[0] - 1, point[1]] 
    around = [above, below, right, left]
    return around


""" make a Room object with x and y coordinates """

def create_room_from_point(x, y):
    ID = str(x) + str(y)
    title = "Title " + str(ID)
    description = "Description " + str(ID)
    room = Room(title=title, description=description, x=x, y=y)
    return room


class World:
    def __init__(self, maze_width, maze_height):
        
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.maze = make_maze_recursion(self.maze_width, self.maze_height)
        self.num_rooms = 0
        
    def generate_rooms(self):
        
        rooms_list = []
        for x in range(0, self.maze_width):
            for y in range(0, self.maze_height):
                if self.maze[x][y] == 'X':
                    self.num_rooms += 1
                    rooms_list.append([x, y])
                    
                    
        all_the_rooms = []

        for point in rooms_list:
            """ Create a room object from a point """
            room = create_room_from_point(point[0], point[1])
            """ save the room to the DB """
            room.save()
            surroundings = around_list(point)
            connections = []
            self.maze[point[0]][point[1]] = room.id
            for point in rooms_list:
                if point in surroundings:
                    connections.append(point)

            for items in list(enumerate(surroundings)):
                if items[1] in connections:
                    """ create a new room from the surrounding points that are Xs"""
                    new_room = create_room_from_point(items[1][0], items[1][1])
                    """ save the room """
                    new_room.save()
                    if items[0] == 0:
                        room.connect_rooms(new_room, 'e')
                    if items[0] == 1:
                        room.connect_rooms(new_room, 'w')
                    if items[0] == 2:
                        room.connect_rooms(new_room, 's')
                    if items[0] == 3:
                        room.connect_rooms(new_room, 'n') 

            all_the_rooms.append(room)
            
        return all_the_rooms


""" Create the maze of Xs"""

width = 15
height = 15
w = World(width, height)
%pprint
for room in w.maze:
    print(room)

""" Turn the X points into room objects, save them and link them together """

rooms = w.generate_rooms()
titles = ["Cave"] * w.num_rooms
descriptions = ["It's dark in here."] * w.num_rooms

""" Give the rooms titles and descriptions and save them again"""

for room in enumerate(rooms):
    room[1].name = titles[room[0]]
    room[1].description = descriptions[room[0]]
    room[1].save()
























































Room.objects.all().delete()

r_outside = Room(title="Outside Cave Entrance",
               description="North of you, the cave mount beckons")

r_foyer = Room(title="Foyer", description="""Dim light filters in from the south. Dusty
passages run north and east.""")

r_overlook = Room(title="Grand Overlook", description="""A steep cliff appears before you, falling
into the darkness. Ahead to the north, a light flickers in
the distance, but there is no way across the chasm.""")

r_narrow = Room(title="Narrow Passage", description="""The narrow passage bends here from west
to north. The smell of gold permeates the air.""")

r_treasure = Room(title="Treasure Chamber", description="""You've found the long-lost treasure
chamber! Sadly, it has already been completely emptied by
earlier adventurers. The only exit is to the south.""")

r_outside.save()
r_foyer.save()
r_overlook.save()
r_narrow.save()
r_treasure.save()

# Link rooms together
r_outside.connectRooms(r_foyer, "n")
r_foyer.connectRooms(r_outside, "s")

r_foyer.connectRooms(r_overlook, "n")
r_overlook.connectRooms(r_foyer, "s")

r_foyer.connectRooms(r_narrow, "e")
r_narrow.connectRooms(r_foyer, "w")

r_narrow.connectRooms(r_treasure, "n")
r_treasure.connectRooms(r_narrow, "s")

players=Player.objects.all()
for p in players:
  p.currentRoom=r_outside.id
  p.save()
