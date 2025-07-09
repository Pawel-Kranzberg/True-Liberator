import pygame
import sys
import math
import random
import numpy
import json
import os

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (retro 1980s palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (255, 0, 255)

# Difficulty settings
DIFFICULTY_SETTINGS = {
    'EASY': {
        'ai_accuracy': 0.8,
        'ai_range': 400,
        'ai_reaction_chance': 0.3,
        'missile_count': 8,
        'shot_cooldown': 2500,
        'player_missile_limit': 12,  # Doubled from 6
        'player_cooldown': 1000,
        'player_explosion_radius': 60,  # Large explosions
        'defensive_explosion_radius': 15  # Swapped - smaller defensive explosions on easy
    },
    'NORMAL': {
        'ai_accuracy': 0.85,
        'ai_range': 500,
        'ai_reaction_chance': 0.4,
        'missile_count': 12,
        'shot_cooldown': 1000,
        'player_missile_limit': 10,  # Updated to 10 missiles
        'player_cooldown': 1500,
        'player_explosion_radius': 45,  # Medium explosions
        'defensive_explosion_radius': 20
    },
    'HARD': {
        'ai_accuracy': 0.9,
        'ai_range': 600,
        'ai_reaction_chance': 0.6,
        'missile_count': 15,
        'shot_cooldown': 500,
        'player_missile_limit': 8,  # Doubled from 4
        'player_cooldown': 2000,
        'player_explosion_radius': 30,  # Small explosions - can only destroy single targets
        'defensive_explosion_radius': 25  # Swapped - larger defensive explosions on hard
    }
}

class HighScoreManager:
    def __init__(self):
        self.scores_file = "high_scores.json"
        self.high_scores = self.load_scores()
        
    def load_scores(self):
        # Pre-populated high scores
        default_scores = [
            {"name": "COMMANDER", "score": 5000, "difficulty": "HARD"},
            {"name": "GENERAL", "score": 4200, "difficulty": "HARD"},
            {"name": "COLONEL", "score": 3800, "difficulty": "NORMAL"},
            {"name": "MAJOR", "score": 3200, "difficulty": "NORMAL"},
            {"name": "CAPTAIN", "score": 2800, "difficulty": "NORMAL"},
            {"name": "LIEUTENANT", "score": 2200, "difficulty": "EASY"},
            {"name": "SERGEANT", "score": 1800, "difficulty": "EASY"},
            {"name": "CORPORAL", "score": 1400, "difficulty": "EASY"},
            {"name": "PRIVATE", "score": 1000, "difficulty": "EASY"},
            {"name": "RECRUIT", "score": 600, "difficulty": "EASY"}
        ]
        
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            else:
                self.save_scores(default_scores)
                return default_scores
        except:
            return default_scores
            
    def save_scores(self, scores=None):
        try:
            scores_to_save = scores if scores else self.high_scores
            with open(self.scores_file, 'w') as f:
                json.dump(scores_to_save, f, indent=2)
        except:
            pass
            
    def add_score(self, name, score, difficulty):
        # print(f"DEBUG: Adding score - Name: '{name}', Score: {score}, Difficulty: {difficulty}")
        new_entry = {"name": name, "score": score, "difficulty": difficulty}
        self.high_scores.append(new_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep top 10
        # print(f"DEBUG: High scores after adding: {[entry['name'] for entry in self.high_scores[:3]]}")
        self.save_scores()
        
    def is_high_score(self, score):
        return len(self.high_scores) < 10 or score > self.high_scores[-1]["score"]

class NameEntryScreen:
    def __init__(self, screen, score, difficulty):
        self.screen = screen
        self.score = score
        self.difficulty = difficulty
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.player_name = ""
        self.max_name_length = 10
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 500  # milliseconds
        
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Submit name (use default if empty)
                final_name = self.player_name.strip() if self.player_name.strip() else "PLAYER"
                return ('SUBMIT', final_name)
            elif event.key == pygame.K_ESCAPE:
                # Cancel name entry
                return ('CANCEL', None)
            elif event.key == pygame.K_BACKSPACE:
                # Remove last character
                if self.player_name:
                    self.player_name = self.player_name[:-1]
            else:
                # Add character if it's printable and within length limit
                if len(self.player_name) < self.max_name_length:
                    char = event.unicode
                    if char.isprintable() and char != ' ':  # No spaces for cleaner display
                        self.player_name += char.upper()  # Convert to uppercase for retro feel
        return ('CONTINUE', None)
        
    def update(self):
        # Update cursor blinking
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars background
        for i in range(100):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 23) % SCREEN_HEIGHT
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            
        # Title
        title = self.font_large.render("NEW HIGH SCORE!", True, PURPLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Score display
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(score_text, score_rect)
        
        difficulty_text = self.font_small.render(f"Difficulty: {self.difficulty}", True, CYAN)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, 230))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        # Name entry prompt
        prompt = self.font_medium.render("Enter your name:", True, YELLOW)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(prompt, prompt_rect)
        
        # Name input box
        box_width = 300
        box_height = 50
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = 340
        
        # Draw input box
        pygame.draw.rect(self.screen, (50, 50, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, GREEN, (box_x, box_y, box_width, box_height), 2)
        
        # Draw entered name
        name_display = self.player_name
        if self.cursor_visible and len(name_display) < self.max_name_length:
            name_display += "_"
        elif len(name_display) == self.max_name_length:
            name_display = name_display  # No cursor when at max length
            
        name_text = self.font_medium.render(name_display, True, WHITE)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, box_y + box_height//2))
        self.screen.blit(name_text, name_rect)
        
        # Instructions
        inst1 = self.font_small.render("Type your name and press ENTER", True, WHITE)
        inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH//2, 450))
        self.screen.blit(inst1, inst1_rect)
        
        inst2 = self.font_small.render("ESC to cancel, ENTER with empty name uses 'PLAYER'", True, (150, 150, 150))
        inst2_rect = inst2.get_rect(center=(SCREEN_WIDTH//2, 480))
        self.screen.blit(inst2, inst2_rect)
        
        # Character limit indicator
        limit_text = self.font_small.render(f"{len(self.player_name)}/{self.max_name_length}", True, CYAN)
        limit_rect = limit_text.get_rect(center=(SCREEN_WIDTH//2, 520))
        self.screen.blit(limit_text, limit_rect)
        
        pygame.display.flip()

class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.selected_difficulty = 'NORMAL'
        self.menu_state = 'MAIN'  # MAIN, DIFFICULTY, HIGH_SCORES
        self.high_score_manager = HighScoreManager()
        
        # Create menu music
        self.menu_music = self.create_menu_music()
        self.music_playing = False
        
    def create_menu_music(self):
        """Create Terminator-inspired chiptune music"""
        try:
            import numpy
            sample_rate = 22050
            duration = 4.0  # 4 second loop
            frames = int(duration * sample_rate)
            arr = numpy.zeros((frames, 2))
            
            # Terminator-inspired bass line (simplified)
            bass_notes = [110, 110, 146.83, 110, 98, 110, 130.81, 110]  # A2, A2, D3, A2, G2, A2, C3, A2
            note_duration = frames // len(bass_notes)
            
            for note_idx, freq in enumerate(bass_notes):
                start_frame = note_idx * note_duration
                end_frame = min(start_frame + note_duration, frames)
                
                for i in range(start_frame, end_frame):
                    t = (i - start_frame) / sample_rate
                    # Square wave for retro sound
                    wave = 1024 * (1 if numpy.sin(2 * numpy.pi * freq * t) > 0 else -1)
                    # Add some decay
                    envelope = max(0.1, 1 - t * 1.5)
                    wave *= envelope
                    arr[i][0] = wave
                    arr[i][1] = wave
                    
            return pygame.sndarray.make_sound(arr.astype(numpy.int16))
        except:
            return None
            
    def start_music(self):
        if self.menu_music and not self.music_playing:
            try:
                pygame.mixer.Sound.play(self.menu_music, loops=-1)  # Loop indefinitely
                self.music_playing = True
            except:
                pass
                
    def stop_music(self):
        if self.music_playing:
            try:
                pygame.mixer.stop()
                self.music_playing = False
            except:
                pass
                
    def reset_high_scores(self):
        """Reset high scores to default pre-populated values"""
        default_scores = [
            {"name": "COMMANDER", "score": 5000, "difficulty": "HARD"},
            {"name": "GENERAL", "score": 4200, "difficulty": "HARD"},
            {"name": "COLONEL", "score": 3800, "difficulty": "NORMAL"},
            {"name": "MAJOR", "score": 3200, "difficulty": "NORMAL"},
            {"name": "CAPTAIN", "score": 2800, "difficulty": "NORMAL"},
            {"name": "LIEUTENANT", "score": 2200, "difficulty": "EASY"},
            {"name": "SERGEANT", "score": 1800, "difficulty": "EASY"},
            {"name": "CORPORAL", "score": 1400, "difficulty": "EASY"},
            {"name": "PRIVATE", "score": 1000, "difficulty": "EASY"},
            {"name": "RECRUIT", "score": 600, "difficulty": "EASY"}
        ]
        self.high_score_manager.high_scores = default_scores
        self.high_score_manager.save_scores()
        
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.menu_state == 'MAIN':
                if event.key == pygame.K_1:
                    self.menu_state = 'DIFFICULTY'
                elif event.key == pygame.K_2:
                    self.menu_state = 'HIGH_SCORES'
                elif event.key == pygame.K_ESCAPE:
                    return 'QUIT'
            elif self.menu_state == 'DIFFICULTY':
                if event.key == pygame.K_1:
                    self.selected_difficulty = 'EASY'
                    return 'START_GAME'
                elif event.key == pygame.K_2:
                    self.selected_difficulty = 'NORMAL'
                    return 'START_GAME'
                elif event.key == pygame.K_3:
                    self.selected_difficulty = 'HARD'
                    return 'START_GAME'
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = 'MAIN'
            elif self.menu_state == 'HIGH_SCORES':
                if event.key == pygame.K_1:
                    self.menu_state = 'MAIN'
                elif event.key == pygame.K_2:
                    # Reset high scores
                    self.reset_high_scores()
                elif event.key == pygame.K_ESCAPE:
                    self.menu_state = 'MAIN'
        return 'MENU'
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars background
        for i in range(100):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 23) % SCREEN_HEIGHT
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            
        if self.menu_state == 'MAIN':
            self.draw_main_menu()
        elif self.menu_state == 'DIFFICULTY':
            self.draw_difficulty_menu()
        elif self.menu_state == 'HIGH_SCORES':
            self.draw_high_scores()
            
        pygame.display.flip()
        
    def draw_main_menu(self):
        # Title
        title = self.font_large.render("TRUE LIBERATOR", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Reverse Missile Command", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        options = [
            "1 - START GAME",
            "2 - HIGH SCORES",
            "ESC - QUIT"
        ]
        
        for i, option in enumerate(options):
            text = self.font_small.render(option, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 300 + i * 50))
            self.screen.blit(text, text_rect)
            
    def draw_difficulty_menu(self):
        # Title
        title = self.font_medium.render("SELECT DIFFICULTY", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Difficulty options with descriptions
        difficulties = [
            ("1 - EASY", "12 missiles, 1s cooldown, Large explosions", GREEN),
            ("2 - NORMAL", "10 missiles, 1.5s cooldown, Medium explosions", YELLOW),
            ("3 - HARD", "8 missiles, 2s cooldown, Small explosions", RED)
        ]
        
        for i, (option, desc, color) in enumerate(difficulties):
            text = self.font_small.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 250 + i * 80))
            self.screen.blit(text, text_rect)
            
            desc_text = pygame.font.Font(None, 20).render(desc, True, WHITE)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, 275 + i * 80))
            self.screen.blit(desc_text, desc_rect)
            
        # Additional info
        info_text = pygame.font.Font(None, 18).render("Hard mode: explosions can only destroy single targets!", True, RED)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH//2, 430))
        self.screen.blit(info_text, info_rect)
        
        info_text2 = pygame.font.Font(None, 18).render("Defensive missiles have proximity fuses (30px radius)!", True, CYAN)
        info_rect2 = info_text2.get_rect(center=(SCREEN_WIDTH//2, 450))
        self.screen.blit(info_text2, info_rect2)
        
        info_text3 = pygame.font.Font(None, 18).render("Hard mode has larger defensive explosions!", True, RED)
        info_rect3 = info_text3.get_rect(center=(SCREEN_WIDTH//2, 470))
        self.screen.blit(info_text3, info_rect3)
            
        # Back instruction
        back_text = self.font_small.render("ESC. BACK", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, 500))
        self.screen.blit(back_text, back_rect)
        
    def draw_high_scores(self):
        # Reload high scores to ensure we have the latest data
        self.high_score_manager.high_scores = self.high_score_manager.load_scores()
        
        # Title
        title = self.font_medium.render("HIGH SCORES", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Headers
        headers = self.font_small.render("RANK  NAME        SCORE    DIFFICULTY", True, YELLOW)
        headers_rect = headers.get_rect(center=(SCREEN_WIDTH//2, 130))
        self.screen.blit(headers, headers_rect)
        
        # High scores
        for i, score_entry in enumerate(self.high_score_manager.high_scores):
            rank = f"{i+1:2d}."
            name = f"{score_entry['name']:10s}"
            score = f"{score_entry['score']:6d}"
            difficulty = score_entry['difficulty']
            
            # Color based on difficulty
            if difficulty == 'EASY':
                color = GREEN
            elif difficulty == 'NORMAL':
                color = YELLOW
            else:
                color = RED
                
            score_line = f"{rank} {name} {score}    {difficulty}"
            text = pygame.font.Font(None, 28).render(score_line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 170 + i * 30))
            self.screen.blit(text, text_rect)
            
        # Menu options
        option1 = self.font_small.render("1. MAIN MENU", True, WHITE)
        option1_rect = option1.get_rect(center=(SCREEN_WIDTH//2, 500))
        self.screen.blit(option1, option1_rect)
        
        option2 = self.font_small.render("2. RESET SCORES", True, RED)
        option2_rect = option2.get_rect(center=(SCREEN_WIDTH//2, 530))
        self.screen.blit(option2, option2_rect)
        
        # Back instruction
        back_text = self.font_small.render("ESC. BACK TO MAIN MENU", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, 560))
        self.screen.blit(back_text, back_rect)

class MissileLauncher:
    def __init__(self, x, y, missile_limit=3, cooldown=1000):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.color = GREEN
        self.missiles_remaining = missile_limit
        self.max_missiles = missile_limit
        self.last_shot_time = 0
        self.shot_cooldown = cooldown
        
    def can_shoot(self, current_time):
        return (self.missiles_remaining > 0 and 
                current_time - self.last_shot_time > self.shot_cooldown)
        
    def shoot(self, current_time):
        if self.can_shoot(current_time):
            self.missiles_remaining -= 1
            self.last_shot_time = current_time
            return True
        return False
        
    def reload(self):
        """Reload missiles after a delay"""
        self.missiles_remaining = self.max_missiles
        
    def draw(self, screen):
        # Draw launcher base
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y, self.width, self.height))
        # Draw launcher barrel
        pygame.draw.rect(screen, self.color, (self.x - 3, self.y - 15, 6, 15))
        
        # Draw missile count
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.missiles_remaining), True, WHITE)
        screen.blit(text, (self.x - 5, self.y + 25))

class Missile:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        
        # Calculate direction and speed
        distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
        self.speed = 3
        self.dx = (target_x - start_x) / distance * self.speed
        self.dy = (target_y - start_y) / distance * self.speed
        
        self.trail = []
        self.active = True
        
    def update(self):
        if not self.active:
            return
            
        # Store trail position
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 15:
            self.trail.pop(0)
            
        # Move missile
        self.x += self.dx
        self.y += self.dy
        
        # Check if reached target
        if abs(self.x - self.target_x) < 5 and abs(self.y - self.target_y) < 5:
            self.active = False
            return True  # Hit target
        
        # Check if missile went off screen
        if self.y > SCREEN_HEIGHT:
            self.active = False
            
        return False
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = i / len(self.trail)
            color = (int(255 * alpha), int(255 * alpha), 0)
            pygame.draw.circle(screen, color, pos, max(1, int(3 * alpha)))
            
        # Draw missile head
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 3)

class Explosion:
    def __init__(self, x, y, max_radius=50, is_defensive=False):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = max_radius
        self.growth_rate = 2
        self.active = True
        self.is_defensive = is_defensive  # Defensive explosions don't harm cities/bases
        
    def update(self):
        if not self.active:
            return
            
        self.radius += self.growth_rate
        if self.radius >= self.max_radius:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw expanding explosion circles
        if self.is_defensive:
            # Blue/cyan colors for defensive explosions
            colors = [CYAN, (0, 200, 255), (100, 255, 255), WHITE]
        else:
            # Red/orange colors for player explosions
            colors = [RED, ORANGE, YELLOW, WHITE]
            
        for i, color in enumerate(colors):
            r = max(0, self.radius - i * 5)
            if r > 0:
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(r), 2)

class DefensiveMissileBase:
    def __init__(self, x, y, difficulty='NORMAL'):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.destroyed = False
        self.color = RED
        self.missiles_remaining = DIFFICULTY_SETTINGS[difficulty]['missile_count']
        self.max_missiles = self.missiles_remaining
        self.last_shot_time = 0
        self.shot_cooldown = DIFFICULTY_SETTINGS[difficulty]['shot_cooldown']
        
    def draw(self, screen):
        if self.destroyed:
            # Draw destroyed base
            pygame.draw.rect(screen, (100, 0, 0), (self.x - self.width//2, self.y, self.width, self.height))
            return
            
        # Draw active base
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y, self.width, self.height))
        # Draw missile count
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.missiles_remaining), True, WHITE)
        screen.blit(text, (self.x - 5, self.y - 20))
        
    def can_shoot(self, current_time):
        return (not self.destroyed and 
                self.missiles_remaining > 0 and 
                current_time - self.last_shot_time > self.shot_cooldown)
                
    def shoot(self, target_x, target_y, current_time):
        if self.can_shoot(current_time):
            self.missiles_remaining -= 1
            self.last_shot_time = current_time
            return DefensiveMissile(self.x, self.y, target_x, target_y)
        return None
        
    def check_hit(self, x, y, radius):
        if self.destroyed:
            return False
            
        distance = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        if distance < radius + 20:
            self.destroyed = True
            return True
        return False

class DefensiveMissile:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        
        # Calculate direction and speed (faster than player missiles)
        distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
        self.speed = 4
        self.dx = (target_x - start_x) / distance * self.speed
        self.dy = (target_y - start_y) / distance * self.speed
        
        self.trail = []
        self.active = True
        self.proximity_fuse_radius = 30  # Consistent 30-pixel radius for all difficulties
        
    def update(self, player_missiles):
        if not self.active:
            return False
            
        # Store trail position
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 10:
            self.trail.pop(0)
            
        # Move missile
        self.x += self.dx
        self.y += self.dy
        
        # Check proximity fuse - explode if close to any player missile
        for player_missile in player_missiles:
            if player_missile.active:
                distance = math.sqrt((self.x - player_missile.x)**2 + (self.y - player_missile.y)**2)
                if distance <= self.proximity_fuse_radius:
                    self.active = False
                    return True  # Proximity detonation
        
        # Check if reached target (backup detonation)
        if abs(self.x - self.target_x) < 8 and abs(self.y - self.target_y) < 8:
            self.active = False
            return True  # Hit target
        
        # Check if missile went off screen
        if self.y < 0 or self.y > SCREEN_HEIGHT or self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False
            
        return False
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw trail (red/orange for defensive missiles)
        for i, pos in enumerate(self.trail):
            alpha = i / len(self.trail)
            color = (int(255 * alpha), int(100 * alpha), 0)
            pygame.draw.circle(screen, color, pos, max(1, int(2 * alpha)))
            
        # Draw missile head
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 2)

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.destroyed = False
        self.color = CYAN
        
    def draw(self, screen):
        if self.destroyed:
            return
            
        # Draw city buildings
        for i in range(3):
            building_x = self.x + i * 20
            building_height = random.randint(20, 35) if not hasattr(self, 'building_heights') else self.building_heights[i]
            if not hasattr(self, 'building_heights'):
                if not hasattr(self, 'building_heights'):
                    self.building_heights = [random.randint(20, 35) for _ in range(3)]
            pygame.draw.rect(screen, self.color, (building_x, self.y - self.building_heights[i], 18, self.building_heights[i]))
            
            # Draw windows
            for row in range(0, self.building_heights[i], 8):
                for col in range(2, 16, 6):
                    if random.random() > 0.3:  # Some windows are lit
                        pygame.draw.rect(screen, YELLOW, (building_x + col, self.y - self.building_heights[i] + row + 2, 2, 3))
    
    def check_hit(self, x, y, radius):
        if self.destroyed:
            return False
            
        # Check if explosion overlaps with city
        city_center_x = self.x + self.width // 2
        city_center_y = self.y - 20
        distance = math.sqrt((x - city_center_x)**2 + (y - city_center_y)**2)
        
        if distance < radius + 30:
            self.destroyed = True
            return True
        return False

class Game:
    def __init__(self, difficulty='NORMAL'):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("True Liberator")
        self.clock = pygame.time.Clock()
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        
        # Game objects
        self.launchers = [
            MissileLauncher(200, 50, 
                          self.difficulty_settings['player_missile_limit'], 
                          self.difficulty_settings['player_cooldown']),
            MissileLauncher(600, 50, 
                          self.difficulty_settings['player_missile_limit'], 
                          self.difficulty_settings['player_cooldown'])
        ]
        
        # Defensive missile bases (edge-center-edge positioning)
        self.defensive_bases = [
            DefensiveMissileBase(50, SCREEN_HEIGHT - 80, difficulty),      # Left edge
            DefensiveMissileBase(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, difficulty),  # Center
            DefensiveMissileBase(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 80, difficulty)   # Right edge
        ]
        
        # Cities positioned evenly between bases
        self.cities = []
        
        # First 3 cities between base 1 (50px) and base 2 (400px)
        # Distance = 400 - 50 = 350px, divided by 4 sections = 87.5px each
        base1_x = 50
        base2_x = SCREEN_WIDTH // 2
        section_width = (base2_x - base1_x * 0) / 4
        for i in range(3):
            city_x = base1_x - base1_x + section_width * (i + 1)
            self.cities.append(City(city_x, SCREEN_HEIGHT - 20))
        
        # Last 3 cities between base 2 (400px) and base 3 (750px)  
        # Distance = 750 - 400 = 350px, divided by 4 sections = 87.5px each
        base3_x = SCREEN_WIDTH - 50
        # section_width = (base3_x - base2_x) / 4
        for i in range(3):
            city_x = base2_x - base1_x + section_width * (i + 1)
            self.cities.append(City(city_x, SCREEN_HEIGHT - 20))
            
        self.missiles = []
        self.defensive_missiles = []
        self.explosions = []
        
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.victory = False
        self.show_victory_screen = False
        self.wave = 1
        self.high_score_manager = HighScoreManager()
        
        # AI parameters from difficulty settings
        self.ai_accuracy = self.difficulty_settings['ai_accuracy']
        self.ai_range = self.difficulty_settings['ai_range']
        self.ai_reaction_chance = self.difficulty_settings['ai_reaction_chance']
        self.player_explosion_radius = self.difficulty_settings['player_explosion_radius']
        self.defensive_explosion_radius = self.difficulty_settings['defensive_explosion_radius']
        
        # Launcher reload timer
        self.last_reload_time = 0
        self.reload_interval = 10000  # 10 seconds
        
        # Generate simple beep sound
        self.create_sounds()
        
    def start_new_wave(self):
        """Start a new wave with increased difficulty"""
        self.wave += 1
        
        # Restore cities
        for city in self.cities:
            city.destroyed = False
            
        # Restore and upgrade defensive bases
        for base in self.defensive_bases:
            base.destroyed = False
            base.missiles_remaining = min(base.max_missiles + self.wave, 20)  # Increase missiles
            base.max_missiles = base.missiles_remaining
            # Decrease cooldown (make AI faster)
            base.shot_cooldown = max(base.shot_cooldown - 200, 300)
            
        # Reset launchers
        for launcher in self.launchers:
            launcher.reload()
            
        # Increase AI difficulty
        self.ai_accuracy = min(self.ai_accuracy + 0.02, 0.95)  # Increase accuracy
        self.ai_reaction_chance = min(self.ai_reaction_chance + 0.05, 0.8)  # Increase reaction
        
        # Clear missiles and explosions
        self.missiles.clear()
        self.defensive_missiles.clear()
        self.explosions.clear()
        
        # Reset timers
        self.last_reload_time = pygame.time.get_ticks()
        
        # Wave bonus
        self.score += self.wave * 500
        
    def check_game_over(self):
        cities_left = sum(1 for city in self.cities if not city.destroyed)
        
        # Check if all cities are destroyed (wave complete)
        if cities_left == 0:
            self.victory = True
            
            # Check if this is a milestone wave (every 10 waves)
            if self.wave % 10 == 0:
                self.show_victory_screen = True
                self.score += 2000  # Milestone bonus
                return
            else:
                self.start_new_wave()
                self.victory = False  # Continue to next wave
                return
            
        # Check if player is out of missiles
        total_missiles_available = sum(launcher.missiles_remaining for launcher in self.launchers)
        missiles_in_flight = len(self.missiles)
        explosions_active = len([exp for exp in self.explosions if not exp.is_defensive])
        
        if total_missiles_available == 0 and missiles_in_flight == 0 and explosions_active == 0:
            # Player is out of missiles and cities remain - game over
            self.game_over = True
                
    def draw_victory_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("MISSION ACCOMPLISHED!", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        self.screen.blit(title, title_rect)
        
        subtitle = pygame.font.Font(None, 32).render(f"Wave {self.wave} Complete!", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(subtitle, subtitle_rect)
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Show options
        option1 = pygame.font.Font(None, 28).render("1. CONTINUE PLAYING", True, GREEN)
        option1_rect = option1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(option1, option1_rect)
        
        if self.high_score_manager.is_high_score(self.score):
            option2 = pygame.font.Font(None, 28).render("2. ENTER HIGH SCORE", True, PURPLE)
            option2_rect = option2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(option2, option2_rect)
            
            option3 = pygame.font.Font(None, 28).render("3. QUIT TO TITLE", True, WHITE)
            option3_rect = option3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 110))
            self.screen.blit(option3, option3_rect)
        else:
            option2 = pygame.font.Font(None, 28).render("2. QUIT TO TITLE", True, WHITE)
            option2_rect = option2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(option2, option2_rect)
            
        # Instructions
        inst_text = pygame.font.Font(None, 20).render("Press the number key for your choice", True, CYAN)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(inst_text, inst_rect)
        
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("THE END", True, RED)
        subtitle = pygame.font.Font(None, 28).render("The cities could not be liberated!", True, YELLOW)
            
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        self.screen.blit(score_text, score_rect)
        
        wave_text = pygame.font.Font(None, 28).render(f"Waves Completed: {self.wave - 1}", True, CYAN)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(wave_text, wave_rect)
        
        difficulty_text = pygame.font.Font(None, 24).render(f"Difficulty: {self.difficulty}", True, CYAN)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        if self.high_score_manager.is_high_score(self.score):
            high_score_text = pygame.font.Font(None, 28).render("NEW HIGH SCORE!", True, PURPLE)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
            self.screen.blit(high_score_text, high_score_rect)
        
        continue_text = pygame.font.Font(None, 24).render("Press SPACE to continue or ESC to quit", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(continue_text, continue_rect)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("THE END", True, RED)
        subtitle = pygame.font.Font(None, 28).render("The cities could not be liberated!", True, YELLOW)
            
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        self.screen.blit(score_text, score_rect)
        
        wave_text = pygame.font.Font(None, 28).render(f"Waves Completed: {self.wave - 1}", True, CYAN)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(wave_text, wave_rect)
        
        difficulty_text = pygame.font.Font(None, 24).render(f"Difficulty: {self.difficulty}", True, CYAN)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        if self.high_score_manager.is_high_score(self.score):
            high_score_text = pygame.font.Font(None, 28).render("NEW HIGH SCORE!", True, PURPLE)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
            self.screen.blit(high_score_text, high_score_rect)
        
        continue_text = pygame.font.Font(None, 24).render("Press SPACE to continue or ESC to quit", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(continue_text, continue_rect)
        
    def create_sounds(self):
        # Create simple retro sounds using pygame
        try:
            # Create a simple beep sound
            sample_rate = 22050
            duration = 0.1
            frequency = 440
            
            frames = int(duration * sample_rate)
            arr = numpy.zeros((frames, 2))
            
            for i in range(frames):
                wave = 4096 * numpy.sin(2 * numpy.pi * frequency * i / sample_rate)
                arr[i][0] = wave
                arr[i][1] = wave
                
            self.launch_sound = pygame.sndarray.make_sound(arr.astype(numpy.int16))
        except:
            self.launch_sound = None
            
    def create_menu_music(self):
        """Create Terminator-inspired chiptune music"""
        try:
            sample_rate = 22050
            duration = 4.0  # 4 second loop
            frames = int(duration * sample_rate)
            arr = numpy.zeros((frames, 2))
            
            # Terminator-inspired bass line (simplified)
            bass_notes = [110, 110, 146.83, 110, 98, 110, 130.81, 110]  # A2, A2, D3, A2, G2, A2, C3, A2
            note_duration = frames // len(bass_notes)
            
            for note_idx, freq in enumerate(bass_notes):
                start_frame = note_idx * note_duration
                end_frame = min(start_frame + note_duration, frames)
                
                for i in range(start_frame, end_frame):
                    t = (i - start_frame) / sample_rate
                    # Square wave for retro sound
                    wave = 2048 * (1 if numpy.sin(2 * numpy.pi * freq * t) > 0 else -1)
                    # Add some decay
                    envelope = max(0, 1 - t * 2)
                    wave *= envelope
                    arr[i][0] = wave
                    arr[i][1] = wave
                    
            return pygame.sndarray.make_sound(arr.astype(numpy.int16))
        except:
            return None
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.show_victory_screen:
                    if event.key == pygame.K_1:
                        # Continue playing
                        self.show_victory_screen = False
                        self.start_new_wave()
                        self.victory = False
                    elif event.key == pygame.K_2:
                        if self.high_score_manager.is_high_score(self.score):
                            # Enter high score with name entry
                            return ('NAME_ENTRY', None)
                        else:
                            # Quit to title (option 2 when no high score)
                            return 'MENU'
                    elif event.key == pygame.K_3 and self.high_score_manager.is_high_score(self.score):
                        # Quit to title (option 3 when high score available)
                        return 'MENU'
                        
                elif self.game_over:
                    if event.key == pygame.K_SPACE:
                        # Check if high score and offer name entry
                        if self.high_score_manager.is_high_score(self.score):
                            return ('NAME_ENTRY', None)
                        return 'MENU'
                    elif event.key == pygame.K_ESCAPE:
                        return False
                        
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.show_victory_screen:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.launch_missile(mouse_x, mouse_y)
                    
        return True
        
    def update(self):
        if self.game_over or self.show_victory_screen:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Reload launchers periodically
        # if current_time - self.last_reload_time > self.reload_interval:
        #     for launcher in self.launchers:
        #         launcher.reload()
        #     self.last_reload_time = current_time
            
        # Update AI defense
        self.update_ai_defense()
        
        # Update player missiles
        for missile in self.missiles[:]:
            hit = missile.update()
            if hit:
                # Create explosion
                explosion = Explosion(missile.target_x, missile.target_y)
                self.explosions.append(explosion)
                self.missiles.remove(missile)
            elif not missile.active:
                self.missiles.remove(missile)
                
        # Update defensive missiles
        for d_missile in self.defensive_missiles[:]:
            hit = d_missile.update(self.missiles)  # Pass player missiles for proximity detection
            if hit:
                # Create smaller defensive explosion
                explosion = Explosion(d_missile.x, d_missile.y, self.defensive_explosion_radius, True)
                self.explosions.append(explosion)
                self.defensive_missiles.remove(d_missile)
            elif not d_missile.active:
                self.defensive_missiles.remove(d_missile)
                
        # Update explosions and check for hits
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)
            else:
                # Check for city hits
                for city in self.cities:
                    if city.check_hit(explosion.x, explosion.y, explosion.radius):
                        self.score += 100
                        
                # Check for defensive base hits
                for base in self.defensive_bases:
                    if base.check_hit(explosion.x, explosion.y, explosion.radius):
                        self.score += 200  # Bonus for destroying defensive bases
                        
                # Check for missile interceptions
                for missile in self.missiles[:]:
                    if missile.active:
                        distance = math.sqrt((missile.x - explosion.x)**2 + (missile.y - explosion.y)**2)
                        if distance < explosion.radius:
                            missile.active = False
                            self.missiles.remove(missile)
                            # self.score += 50  # Bonus for intercepted missile
                            
        # Check for game over conditions
        self.check_game_over()
        
    def launch_missile(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        
        # Choose closest launcher that can shoot
        best_launcher = None
        best_distance = float('inf')
        
        for launcher in self.launchers:
            if launcher.can_shoot(current_time):
                distance = abs(launcher.x - target_x)
                if distance < best_distance:
                    best_distance = distance
                    best_launcher = launcher
        
        if best_launcher and best_launcher.shoot(current_time):
            # Create missile
            missile = Missile(best_launcher.x, best_launcher.y, target_x, target_y)
            self.missiles.append(missile)
            
            # Play launch sound
            if self.launch_sound:
                try:
                    self.launch_sound.play()
                except:
                    pass
                
    def update_ai_defense(self):
        current_time = pygame.time.get_ticks()
        
        # AI tries to intercept incoming missiles
        for missile in self.missiles:
            if not missile.active:
                continue
                
            # Calculate interception point more accurately
            # Find the best defensive base for this missile
            best_base = None
            best_interception_point = None
            best_time_to_intercept = float('inf')
            
            for base in self.defensive_bases:
                if not base.can_shoot(current_time):
                    continue
                    
                # Calculate distance to missile
                distance_to_missile = math.sqrt((base.x - missile.x)**2 + (base.y - missile.y)**2)
                
                # Only consider missiles within range
                if distance_to_missile > self.ai_range:
                    continue
                
                # Predict where to intercept the missile
                # Calculate time for defensive missile to reach various points along missile path
                for t in range(10, 100, 5):  # Check multiple time steps
                    future_missile_x = missile.x + missile.dx * t
                    future_missile_y = missile.y + missile.dy * t
                    
                    # Skip if missile will be off screen
                    if future_missile_y > SCREEN_HEIGHT or future_missile_x < 0 or future_missile_x > SCREEN_WIDTH:
                        break
                    
                    # Calculate time for defensive missile to reach this point
                    distance_to_intercept = math.sqrt((base.x - future_missile_x)**2 + (base.y - future_missile_y)**2)
                    defensive_missile_time = distance_to_intercept / 4  # Defensive missile speed is 4
                    
                    # If defensive missile can reach the point at roughly the same time
                    if abs(defensive_missile_time - t) < 15:  # Allow some tolerance
                        if t < best_time_to_intercept:
                            best_time_to_intercept = t
                            best_base = base
                            # Add some inaccuracy based on difficulty
                            accuracy_offset = 0 if random.random() < self.ai_accuracy else random.randint(-30, 30)
                            best_interception_point = (
                                future_missile_x + accuracy_offset,
                                future_missile_y + accuracy_offset
                            )
                        break
            
            # Shoot at the calculated interception point
            if best_base and best_interception_point and random.random() < self.ai_reaction_chance:
                defensive_missile = best_base.shoot(best_interception_point[0], best_interception_point[1], current_time)
                if defensive_missile:
                    self.defensive_missiles.append(defensive_missile)
                        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars background
        for i in range(50):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 23) % (SCREEN_HEIGHT // 2)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            
        # Draw launchers
        for launcher in self.launchers:
            launcher.draw(self.screen)
            
        # Draw defensive missile bases
        for base in self.defensive_bases:
            base.draw(self.screen)
            
        # Draw cities
        for city in self.cities:
            city.draw(self.screen)
            
        # Draw player missiles
        for missile in self.missiles:
            missile.draw(self.screen)
            
        # Draw defensive missiles
        for d_missile in self.defensive_missiles:
            d_missile.draw(self.screen)
            
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)
            
        # Draw crosshair at mouse position (only if game not over)
        if not self.game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, GREEN, (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
            pygame.draw.line(self.screen, GREEN, (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        cities_left = sum(1 for city in self.cities if not city.destroyed)
        cities_text = self.font.render(f"Cities: {cities_left}", True, WHITE)
        self.screen.blit(cities_text, (10, 50))
        
        bases_left = sum(1 for base in self.defensive_bases if not base.destroyed)
        bases_text = self.font.render(f"Enemy Bases: {bases_left}", True, WHITE)
        self.screen.blit(bases_text, (10, 90))
        
        # Draw difficulty and wave
        difficulty_color = GREEN if self.difficulty == 'EASY' else YELLOW if self.difficulty == 'NORMAL' else RED
        difficulty_text = pygame.font.Font(None, 28).render(f"Difficulty: {self.difficulty}", True, difficulty_color)
        self.screen.blit(difficulty_text, (10, 130))
        
        wave_text = pygame.font.Font(None, 28).render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (10, 160))
        
        # Show total missiles remaining
        total_missiles = sum(launcher.missiles_remaining for launcher in self.launchers)
        missiles_text = pygame.font.Font(None, 28).render(f"Missiles: {total_missiles}", True, YELLOW)
        self.screen.blit(missiles_text, (10, 190))
        
        # Draw instructions (only at start of game)
        if self.score == 0 and not self.game_over:
            inst_text = pygame.font.Font(None, 24).render("Click to launch missiles! Destroy cities and enemy bases!", True, YELLOW)
            text_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(inst_text, text_rect)
            
            inst_text2 = pygame.font.Font(None, 20).render("Red bases will shoot down your missiles!", True, RED)
            text_rect2 = inst_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
            self.screen.blit(inst_text2, text_rect2)
            
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        elif self.show_victory_screen:
            self.draw_victory_screen()
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            result = self.handle_events()
            if result == False:
                running = False
            elif result == 'MENU':
                return 'MENU'
            elif result == ('NAME_ENTRY', None):
                return ('NAME_ENTRY', None)
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        return 'QUIT'

def main():
    print("Welcome to True Liberator!")
    print("A reverse Missile Command experience...")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("True Liberator")
    clock = pygame.time.Clock()
    
    menu = MenuScreen(screen)
    menu.start_music()  # Start menu music
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            result = menu.handle_events(event)
            if result == 'QUIT':
                running = False
                break
            elif result == 'START_GAME':
                # Stop menu music and start game
                menu.stop_music()
                game = Game(menu.selected_difficulty)
                game_result = game.run()
                
                if game_result == 'QUIT':
                    running = False
                    break
                elif game_result == ('NAME_ENTRY', None):
                    # Show name entry screen
                    name_entry = NameEntryScreen(screen, game.score, game.difficulty)
                    
                    # Name entry loop
                    name_entry_running = True
                    while name_entry_running:
                        for name_event in pygame.event.get():
                            if name_event.type == pygame.QUIT:
                                running = False
                                name_entry_running = False
                                break
                                
                            name_result = name_entry.handle_events(name_event)
                            if name_result[0] == 'SUBMIT':
                                # Add high score with entered name
                                entered_name = name_result[1]
                                # print(f"DEBUG: Adding score for '{entered_name}' with score {game.score}")  # Debug line
                                game.high_score_manager.add_score(entered_name, game.score, game.difficulty)
                                name_entry_running = False
                                
                                # Show high score screen after name entry
                                menu.menu_state = 'HIGH_SCORES'
                                break
                            elif name_result[0] == 'CANCEL':
                                # Cancel name entry, return to menu
                                name_entry_running = False
                                break
                                
                        if not running:
                            break
                            
                        name_entry.update()
                        name_entry.draw()
                        clock.tick(FPS)
                
                # Restart menu music when returning to menu
                if running:
                    menu.start_music()
                
        if not running:
            break
            
        menu.draw()
        clock.tick(FPS)
    
    # Stop music before quitting
    menu.stop_music()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
