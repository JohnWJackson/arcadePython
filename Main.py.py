import arcade
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

VIEWPORT_MARGIN = 10
TOP_MARGIN = 40

TEXT_WIDTH = 20

# Scaling percentages
SPRITE_SCALING_PLAYER = .5
SPRITE_SCALING_ENEMY = .1
SPRITE_SCALING_BULLET = .4

# Screen states
WELCOME = 0
GAME_RUNNING = 1
GAME_OVER = 2

# Ship speeds
MOVEMENT_SPEED = 5

# Projectile speeds
PLAYER_BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 7

# Starting player lives
PLAYER_LIVES = 3

# Levels and level scaling
CURRENT_LEVEL = 5
ENEMY_COUNT = CURRENT_LEVEL * 2


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

    # def reset_pos(self):
    #     self.center_y = random.randrange((SCREEN_HEIGHT / 2) + TOP_MARGIN, SCREEN_HEIGHT - VIEWPORT_MARGIN)
    #     self.center_x = SCREEN_WIDTH + 40

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

        # Keep track of frames
        self.total_frames = 0

        # Starting game state - WELCOME
        self.current_state = WELCOME

        # Game pause
        self.paused = False

        # Load textures
        self.welcome_texture = arcade.load_texture("images/welcome.png")
        self.gameover_texture = arcade.load_texture("images/gameover.png")

        # Sprite lists
        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None

        # Set up the player
        self.player_sprite = None
        self.score = 0
        self.lives = PLAYER_LIVES

        # Simple physics engine
        self.physics_engine = None

        # Load sounds
        self.welcome_music = arcade.sound.load_sound("sounds/welcome_theme.wav")
        self.gun_sound = arcade.sound.load_sound("sounds/laser_gun01.wav")
        self.enemy_explosion_sound = arcade.sound.load_sound("sounds/explosion01.wav")
        self.player_explosion_sound = arcade.sound.load_sound("sounds/explosion02.wav")

    def setup(self):
        """
        Main
        """
        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

        # Start welcome music
        arcade.play_sound(self.welcome_music)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

        # Set up the player
        self.score = 0

        self.player_sprite = arcade.Sprite("images/ship01.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT - (SCREEN_HEIGHT - 60)
        self.player_list.append(self.player_sprite)

        # Set up the enemies
        x = TOP_MARGIN
        enemy_locations = []
        for i in range(ENEMY_COUNT):
            enemy_locations.append([SCREEN_WIDTH / 2, SCREEN_HEIGHT - x])
            x += TOP_MARGIN

        for enemy in enemy_locations:
            enemy_sprite = Enemy("images/enemy_ship01.png", SPRITE_SCALING_ENEMY)
            enemy_sprite.center_x = enemy[0]
            enemy_sprite.center_y = enemy[1]
            enemy_sprite.change_x = random.randrange(-7, 7, 2)
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
        elif self.current_state == GAME_OVER:
            self.draw_gameover_page()

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        global CURRENT_LEVEL

        # Only happens if the game is running
        if self.current_state == GAME_RUNNING:

            # Count the frames to a max of 60
            self.total_frames = (self.total_frames + 1) % 60

            # Updates
            self.physics_engine.update()
            self.player_list.update()
            self.enemy_list.update()
            self.player_bullet_list.update()
            self.enemy_bullet_list.update()

            # Player boundary checks
            if self.player_sprite.left < VIEWPORT_MARGIN:
                self.player_sprite.boundary_left = VIEWPORT_MARGIN
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
                # Enemies disappear when kiled
                for enemy in hit_list:
                    enemy.kill()
                    # Plus 100 to score
                    self.score += 100
                    # Play sound
                    arcade.play_sound(self.enemy_explosion_sound)

            # Half enemies shoot bullets every 60 frames, other half every 30 frames
            enemy_count = 1
            for enemy in self.enemy_list:
                enemy_count += 1
                if enemy_count % 2 == 0:
                    if self.total_frames % 60 == 0:
                        enemy_bullet = EnemyBullet("images/bullet_01.png", SPRITE_SCALING_BULLET)
                        enemy_bullet.center_x = enemy.center_x
                        enemy_bullet.top = enemy.bottom
                        self.enemy_bullet_list.append(enemy_bullet)
                else:
                    if self.total_frames == 30:
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

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever arrow keys are pressed
        """
        if self.current_state == GAME_RUNNING:

            # pause_count = 0
            # if key == arcade.key.P:
            #     pause_count += 1
            #     if pause_count == 1:
            #         self.paused = True
            #     elif pause_count == 2:
            #         self.paused = False
            # while self.paused:
            #     arcade.pause(1)

            if key == arcade.key.UP:
                self.player_sprite.change_y = MOVEMENT_SPEED
            if key == arcade.key.DOWN:
                self.player_sprite.change_y = -MOVEMENT_SPEED
            if key == arcade.key.RIGHT:
                self.player_sprite.change_x = MOVEMENT_SPEED
            if key == arcade.key.LEFT:
                self.player_sprite.change_x = -MOVEMENT_SPEED

        elif self.current_state == GAME_OVER:
            if key == arcade.key.ESCAPE:
                quit()

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off an arrow key
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """

        if self.current_state == GAME_RUNNING:
            # Player bullets
            player_bullet = PlayerBullet("images/bullet_01.png", SPRITE_SCALING_BULLET)
            player_bullet.center_x = self.player_sprite.center_x
            player_bullet.bottom = self.player_sprite.top
            self.player_bullet_list.append(player_bullet)

            # Play sound
            arcade.sound.play_sound(self.gun_sound)

        elif self.current_state == WELCOME:
            self.current_state = GAME_RUNNING

        elif self.current_state == GAME_OVER:
            self.lives = PLAYER_LIVES
            self.current_state = GAME_RUNNING

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main method """
    game = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
