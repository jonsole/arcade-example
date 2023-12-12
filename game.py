"""
Platformer Game
"""
import arcade
import time

# Constants
SCREEN_WIDTH = 800  
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
TILE_SCALING = 2

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_FORCE = 600
PLAYER_BOUNCE = 0.5
GRAVITY = 500
PLAYER_JUMP_FORCE = 20000
PLAYER_JUMP_TIME = 0.2


class Object(arcade.Sprite):

    def __init__(self, platforms, walls):
        super().__init__()

        self.platforms = platforms
        self.walls = walls
        self.accel_x = 0
        self.accel_y = 0
        self.is_on_surface = False


    def on_update(self, delta_time: float = 1 / 60) -> None:

        self.change_x += self.accel_x * delta_time    
        self.change_x *= 0.95

        centre_x = self.center_x
        center_y = self.center_y

        # move in left/right direction
        self.center_x += self.change_x * delta_time
        walls_after_x = arcade.check_for_collision_with_list(self, self.walls)
        if walls_after_x: 

            bounce_x = 0

            # check if we should bounce of the walls
            for w in walls_after_x:                
                self.center_y += 2
                if arcade.check_for_collision(self, w):
                    self.center_y = center_y
                    if w.center_x > self.center_x:
                        bounce_x -= 1
                    elif w.center_x < self.center_x:
                        bounce_x += 1

            # perform bounce
            if bounce_x < 0:
                self.change_x = -abs(self.change_x) * PLAYER_BOUNCE
                self.center_x  -= 0.5
            elif bounce_x > 0:         
                self.change_x = abs(self.change_x) * PLAYER_BOUNCE
                self.center_x  += 0.5

        # get list of platforms we're touching before moving up/down
        platforms_before = arcade.check_for_collision_with_list(self, self.platforms)

        # move in up/down direction, include gravity
        self.center_y += self.change_y * delta_time
        walls_after = arcade.check_for_collision_with_list(self, self.walls)
        if walls_after:
            self.center_y = center_y
            self.change_y = 0
            self.is_on_surface = True
            center_y = self.center_y
        else:
            self.change_y -= GRAVITY * delta_time

        # get list of platforms we're touching after moving up/down
        platforms_after = arcade.check_for_collision_with_list(self, self.platforms)

        # if going up we not on a platform
        if self.change_y > 0:
            self.is_on_surface = False
        else:
            # if touching after but not before, we on a platform
            if platforms_after and not platforms_before:
                self.center_y = center_y
                self.change_y = 0
                self.is_on_surface = True
                center_y = self.center_y                
        

class Skeleton(Object):

    def __init__(self, platforms, walls, player):
        super().__init__(platforms, walls)

        self.player = player

        filename = 'assets\skeleton.png'
        self.walk_textures = [[],[]]
        self.idle_textures = [[],[]]

        for i in range(0,4):            
            self.idle_textures[0].append(arcade.load_texture(filename, x=i*64, y=48, width=64, height=48))
            self.idle_textures[1].append(arcade.load_texture(filename, x=i*64, y=48, width=64, height=48).flip_left_right())
            self.walk_textures[0].append(arcade.load_texture(filename, x=i*64, y=96, width=64, height=48))
            self.walk_textures[1].append(arcade.load_texture(filename, x=i*64, y=96, width=64, height=48).flip_left_right())

        self.scale = 2.0
        self.direction_x = 0
        self.accel_x = 200

    def on_update(self, delta_time):

        if self.player.center_x + 20 < self.center_x:
            self.accel_x = -200
        elif self.player.center_x - 20 > self.center_x:
            self.accel_x = 200
            
        if abs(self.accel_x) > 1:
            self.direction_x = 0 if self.accel_x > 0 else 1
            self.texture = self.walk_textures[self.direction_x][int((self.center_x / 8) % len(self.walk_textures[self.direction_x]))]
        else:
            self.texture = self.idle_textures[self.direction_x][int(time.time() * 5 % len(self.idle_textures[self.direction_x]))]

        # We can only jump if we're standing on a platform
        if self.is_on_surface:
            self.change_y += self.accel_y * delta_time

        return super().on_update(delta_time)


class Player(Object):
    """ Player Class """

    def __init__(self, platforms, walls):
        super().__init__(platforms, walls)

        filename = 'assets/player.png'
        self.walk_textures = [[],[]]
        self.idle_textures = [[],[]]

        for i in range(0,6):            
            self.idle_textures[0].append(arcade.load_texture(filename, x=i*48, y=0,  width=48, height=48))
            self.idle_textures[1].append(arcade.load_texture(filename, x=i*48, y=0,  width=48, height=48).flip_left_right())
            self.walk_textures[0].append(arcade.load_texture(filename, x=i*48, y=48, width=48, height=48))
            self.walk_textures[1].append(arcade.load_texture(filename, x=i*48, y=48, width=48, height=48).flip_left_right())

        self.scale = 2.0

        self.direction_x = 0
        self.jump_time= 0


    def on_update(self, delta_time):

        if abs(self.accel_x) > 1:
            self.direction_x = 0 if self.accel_x > 0 else 1
            self.texture = self.walk_textures[self.direction_x][int((self.center_x / 8) % len(self.walk_textures[self.direction_x]))]
        else:
            self.texture = self.idle_textures[self.direction_x][int(time.time() * 5 % len(self.idle_textures[self.direction_x]))]

        # We can only jump if we're standing on a platform
        if self.is_on_surface:
            self.change_y += self.accel_y * delta_time

        return super().on_update(delta_time)



        


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")


    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up the Cameras
        self.camera = arcade.Camera()
        self.gui_camera = arcade.Camera()

        # Name of map file to load
        map_name = "cave/cave.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            "coins": {
                "use_spatial_hash": True,
            },
            "platforms": {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Keep track of the score
        self.score = 0

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = Player(self.scene["platforms"], self.scene["walls"])
        self.player_sprite.center_x = 256
        self.player_sprite.center_y = 512
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)
        self.scene.add_sprite_list_before("player", "platforms", sprite_list=self.player_sprite_list)

        self.skeleton_sprite = Skeleton(self.scene["platforms"], self.scene["walls"], self.player_sprite)
        self.skeleton_sprite.center_x = 256 + 32
        self.skeleton_sprite.center_y = 512
        self.enemy_sprite_list = arcade.SpriteList()
        self.enemy_sprite_list.append(self.skeleton_sprite)
        self.scene.add_sprite_list_before("enemies", "platforms", sprite_list=self.enemy_sprite_list)


        # --- Other stuff

        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)



    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw(pixelated=True)
        
        # Debug
        self.player_sprite.draw_hit_box()        
        for s in self.scene["coins"]:
            s.draw_hit_box()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.accel_y = PLAYER_JUMP_FORCE

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.accel_x = -PLAYER_MOVEMENT_FORCE
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.accel_x = PLAYER_MOVEMENT_FORCE

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.accel_y = 0

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.accel_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.accel_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""

        self.scene.update_animation(names=['coins'], delta_time=delta_time)
        self.scene.on_update(delta_time)

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["coins"]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            coin.center_y += 20
            #coin.remove_from_sprite_lists()

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()