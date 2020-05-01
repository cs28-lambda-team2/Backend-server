from django.contrib.auth.models import User
from adventure.models import Player, Room
import random 

Room.objects.all().delete()

TILE_EMPTY = 'X'
TILE_CRATE = '_'


""" Make the Maze Grid """

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

""" make the World """

class World:
    def __init__(self, maze_width, maze_height):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.maze = make_maze_recursion(self.maze_width, self.maze_height)
        self.num_rooms = 0
    def generate_rooms(self, titles, descriptions):
        rooms_list = []
        for x in range(0, self.maze_width):
            for y in range(0, self.maze_height):
                if self.maze[x][y] == 'X':
                    self.num_rooms += 1
                    rooms_list.append([x, y]) 
        """ Make a list of all the room Objects with titles and descriptions """
        room_objects = []
        for room in enumerate(rooms_list):
            r = Room(title=titles[room[0]],
                     description=descriptions[room[0]],
                     x=room[1][0], y=room[1][1])
            r.save()
            room_objects.append(r) 
        """ Cycle through the room objects and connect them """
        for a_room in room_objects:
            starting_room = a_room
            starting_point = starting_room.x, starting_room.y
            surroundings = []
            """ get the points around the coordinates """
            surroundings = around_list(starting_point)
            connections = []
            """ check if the point around it is a room """
            for value in rooms_list:
                if value in surroundings:
                    connections.append(value)
            """ add the direction to the connections """
            connections_and_direction = []
            for items in enumerate(surroundings):
                if items[1] in connections:
                    if items[0] == 0:
                        connections_and_direction.append([items[1], 'n'])
                    if items[0] == 1:
                        connections_and_direction.append([items[1], 's'])
                    if items[0] == 2:
                        connections_and_direction.append([items[1], 'w'])
                    if items[0] == 3:
                        connections_and_direction.append([items[1], 'e'])
            """ loop through the connection-direction pairs and connect the objects """
            for pointz in connections_and_direction:
                for outer_room in room_objects:
                    outer_point = [outer_room.x, outer_room.y]
                    if outer_point == pointz[0]:
                        if pointz[1] == 'n':
                            starting_room.connectRooms(outer_room, 'n')
                        if pointz[1] == 's':
                            starting_room.connectRooms(outer_room, 's')
                        if pointz[1] == 's':
                            starting_room.connectRooms(outer_room, 'e')
                        if pointz[1] == 'e':
                            starting_room.connectRooms(outer_room, 'w')
            """ add the room ID to the maze """              
            self.maze[starting_room.x][starting_room.y] = starting_room.id
        return room_objects


""" Create the maze of Xs"""
width = 15
height = 15
w = World(width, height)
for room in w.maze:
    print(room)

""" Turn the X points into room objects, save them and link them together """
titles = ["Cave"] * 1000
descriptions = ["It's dark in here."] * 1000
rooms = w.generate_rooms(titles, descriptions)

""" make the player start in the first room """
players=Player.objects.all()
for p in players:
  p.currentRoom=rooms[1].id
  p.save()