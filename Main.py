import arcade
from random import randint, randrange
from math import ceil
import time


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

TEXT_WIDTH = 20

# Spacing
VIEWPORT_MARGIN = 10
PIXEL_SPACING = 40

# Scaling percentages
SPRITE_SCALING_PLAYER = .5
SPRITE_SCALING_ENEMY = .1
SPRITE_SCALING_BULLET = .4

# Screen states
WELCOME = 0
GAME_RUNNING = 1
NEXT_LEVEL = 2
GAME_OVER = 3
PAUSE = 4

# Ship speeds
MOVEMENT_SPEED = 5

# Projectile speeds
PLAYER_BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 7

# Starting player lives
PLAYER_LIVES = 3


class PlayerBullet(arcade.Sprite):
    """
    Player bullet shooting direction and speed
    """
    def update(self):
        self.center_y += PLAYER_BULLET_SPEED


class EnemyBullet(arcade.Sprite):
    """
    Enemy bullet shooting direction and speed
    """
    def update(self):
        self.center_y -= ENEMY_BULLET_SPEED


class Enemy(arcade.Sprite):
    """
    Enemy lateral movement and boundaries
    """
    def __init__(self, filename, sprite_scaling):
        super().__init__(filename, sprite_scaling)

        self.change_x = 0

    def update(self):
        # Enemy movement
        self.center_x += self.change_x

        # Enemy boundaries
        if self.left < 0:
            self.change_x *= -1
        if self.right > SCREEN_WIDTH:
            self.change_x *= -1


class MyApplication(arcade.Window):
    """
    Main application class.
    """
    def __init__(self, width, height):
        super().__init__(width, height, "Space_Cadet")

        # Hide the mouse
        self.set_mouse_visible(False)

        # Game states
        self.current_state = WELCOME

        # Pause game
        self.paused = False

        # Get start time
        self.start = time.time()

        # Load textures
        self.welcome_texture = arcade.load_texture("images/welcome.png")
        self.gameover_texture = arcade.load_texture("images/gameover.png")
        self.paused_texture = arcade.load_texture("images/paused.png")
        self.nextlevel_texture = arcade.load_texture("images/nextlevel.png")

        # Sprite lists
        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None

        # Set up the player
        self.player_sprite = None
        self.score = 0
        self.enemies_killed = 0
        self.lives = PLAYER_LIVES

        # Levels and scaling
        self.current_level = 1
        self.enemy_count = 1

        # Physics engine
        self.physics_engine = None

        # Load sounds
        self.welcome_music = arcade.sound.load_sound("sounds/welcome_theme.wav")
        self.gun_sound = arcade.sound.load_sound("sounds/laser_gun01.wav")
        self.enemy_explosion_sound = arcade.sound.load_sound("sounds/explosion01.wav")
        self.player_explosion_sound = arcade.sound.load_sound("sounds/explosion02.wav")

        # Start welcome music
        arcade.play_sound(self.welcome_music)

    def setup(self):
        """
        Main
        """
        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

        # Set up the player sprite
        self.player_sprite = arcade.Sprite("images/ship01.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT - (SCREEN_HEIGHT - PIXEL_SPACING)
        self.player_list.append(self.player_sprite)

        # Set up the enemy sprites numbers and locations
        enemy_locations = []
        for i in range(self.enemy_count):
            enemy_locations.append([randint(PIXEL_SPACING, SCREEN_WIDTH - PIXEL_SPACING),
                                    randint((SCREEN_HEIGHT // 3) + PIXEL_SPACING, SCREEN_HEIGHT - PIXEL_SPACING)])

        for enemy in enemy_locations:
            enemy_sprite = Enemy("images/enemy_ship01.png", SPRITE_SCALING_ENEMY)
            enemy_sprite.center_x = enemy[0]
            enemy_sprite.center_y = enemy[1]
            enemy_sprite.change_x = randrange(-9, 9, 2)
            self.enemy_list.append(enemy_sprite)

        # Set up simple physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.enemy_list)

    def draw_welcome_page(self):
        # Load image on welcome page
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2,
                                      SCREEN_HEIGHT // 2,
                                      self.welcome_texture.width,
                                      self.welcome_texture.height,
                                      self.welcome_texture)

    def draw_gameover_page(self):
        # Load image on gameover page
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2,
                                      SCREEN_HEIGHT // 2,
                                      self.gameover_texture.width,
                                      self.gameover_texture.height,
                                      self.gameover_texture)

    def draw_paused_page(self):
        # Load image on paused page
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2,
                                      SCREEN_HEIGHT // 2,
                                      self.paused_texture.width,
                                      self.paused_texture.height,
                                      self.paused_texture)

    def draw_nextlevel_page(self):
        # Load image on next level page
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2,
                                      SCREEN_HEIGHT // 2,
                                      self.nextlevel_texture.width,
                                      self.nextlevel_texture.height,
                                      self.nextlevel_texture)

        arcade.draw_text(f"Level - {self.current_level}",
                         SCREEN_WIDTH - 390,
                         SCREEN_HEIGHT - 150,
                         arcade.color.ANDROID_GREEN,
                         40)

    def draw_game(self):
        # Draw all sprites
        self.player_list.draw()
        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()

        # Draw the score
        arcade.draw_text(f"Score: {self.score}",
                         VIEWPORT_MARGIN,
                         VIEWPORT_MARGIN,
                         arcade.color.WHITE,
                         TEXT_WIDTH)
        # Draw the remaining lives
        arcade.draw_text(f"Lives: {self.lives}",
                         SCREEN_WIDTH - 100,
                         VIEWPORT_MARGIN,
                         arcade.color.WHITE,
                         TEXT_WIDTH)

        # Draw pause info
        arcade.draw_text(f"'P' to pause",
                         SCREEN_WIDTH - 130,
                         SCREEN_HEIGHT - (VIEWPORT_MARGIN * 2),
                         arcade.color.WHITE,
                         TEXT_WIDTH)

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()

        # Draw game screens
        if self.current_state == WELCOME:
            self.draw_welcome_page()
        elif self.current_state == GAME_RUNNING:
            self.draw_game()
        elif self.current_state == NEXT_LEVEL:
            self.draw_nextlevel_page()
        elif self.current_state == PAUSE:
            self.draw_paused_page()
        elif self.current_state == GAME_OVER:
            self.draw_gameover_page()

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        # Only happens if the game is running
        if self.current_state == GAME_RUNNING and not self.paused:

            # Updates
            self.physics_engine.update()
            self.player_list.update()
            self.enemy_list.update()
            self.player_bullet_list.update()
            self.enemy_bullet_list.update()

            # Player boundary checks
            if self.player_sprite.left < VIEWPORT_MARGIN:
                self.player_sprite.left = VIEWPORT_MARGIN
            if self.player_sprite.right > SCREEN_WIDTH - VIEWPORT_MARGIN:
                self.player_sprite.right = SCREEN_WIDTH - VIEWPORT_MARGIN
            if self.player_sprite.top > SCREEN_HEIGHT / 3:
                self.player_sprite.top = SCREEN_HEIGHT / 3
            if self.player_sprite.bottom < VIEWPORT_MARGIN:
                self.player_sprite.bottom = VIEWPORT_MARGIN

            # Player bullet collision checks
            for bullet in self.player_bullet_list:
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                # Bullet disappears if flies past the screen
                if bullet.bottom > SCREEN_HEIGHT:
                    bullet.kill()
                # Bullet disappears if hits something
                if len(hit_list) > 0:
                    bullet.kill()
                # Enemies disappear when killed
                for enemy in hit_list:
                    enemy.kill()
                    self.enemies_killed += 1
                    # Plus 100 to score
                    self.score += 100
                    # Play sound
                    arcade.play_sound(self.enemy_explosion_sound)

            # Enemies shoot randomly ( 2% chance each frame to shoot )
            for enemy in self.enemy_list:
                if randint(0, 50) == 0 and self.reload_timer():
                    enemy_bullet = EnemyBullet("images/bullet_01.png", SPRITE_SCALING_BULLET)
                    enemy_bullet.center_x = enemy.center_x
                    enemy_bullet.top = enemy.bottom
                    self.enemy_bullet_list.append(enemy_bullet)

            # Enemy bullet collisions
            for enemy_bullet in self.enemy_bullet_list:
                enemy_hit_list = arcade.check_for_collision_with_list(enemy_bullet, self.player_list)
                if len(enemy_hit_list) > 0:
                    enemy_bullet.kill()
                    arcade.play_sound(self.player_explosion_sound)
                    self.lives -= 1
                    if self.lives == 0:
                        self.current_state = GAME_OVER
                elif enemy_bullet.top < 0:
                    enemy_bullet.kill()

        # Start next level when all enemies are killed
        if self.enemies_killed == self.enemy_count:
            self.current_state = NEXT_LEVEL
            self.current_level += 1
            self.enemies_killed = 0
            self.enemy_count = ceil(self.enemy_count * 1.3)
            self.enemy_list = None
            self.setup()

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever arrow keys are pressed
        """
        if self.current_state == GAME_RUNNING and not self.paused:
            # P to pause
            if key == arcade.key.P:
                self.current_state = PAUSE
                self.paused = True

            # Directional keys to move
            if key == arcade.key.UP:
                self.player_sprite.change_y = MOVEMENT_SPEED
            if key == arcade.key.DOWN:
                self.player_sprite.change_y = -MOVEMENT_SPEED
            if key == arcade.key.RIGHT:
                self.player_sprite.change_x = MOVEMENT_SPEED
            if key == arcade.key.LEFT:
                self.player_sprite.change_x = -MOVEMENT_SPEED

        # Un-pause
        elif key == arcade.key.P and self.paused:
                self.current_state = GAME_RUNNING
                self.paused = False

        elif key == arcade.key.ENTER and self.current_state == NEXT_LEVEL:
            self.current_state = GAME_RUNNING

        elif key == arcade.key.ESCAPE:
            quit()

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off an arrow key
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        # Shoot player bullets on mouse press. Half second reload timer

        if self.current_state == GAME_RUNNING and self.reload_timer():
            # Player bullets
            player_bullet = PlayerBullet("images/bullet_01.png", SPRITE_SCALING_BULLET)
            player_bullet.center_x = self.player_sprite.center_x
            player_bullet.bottom = self.player_sprite.top
            self.player_bullet_list.append(player_bullet)
            self.start = time.time()
            # Play sound
            arcade.sound.play_sound(self.gun_sound)

        elif self.current_state == WELCOME:
            self.current_state = GAME_RUNNING

        elif self.paused:
            self.current_state = GAME_RUNNING
            self.paused = False

        elif self.current_state == GAME_OVER:
            self.lives = PLAYER_LIVES
            self.enemy_count = 1
            self.enemies_killed = 0
            self.current_level = 1
            self.score = 0
            self.current_state = GAME_RUNNING
            self.setup()

    def reload_timer(self):
            return (time.time() - self.start) > .1


def main():
    """ Main method """
    game = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()