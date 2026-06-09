import turtle
import time
import random
import tkinter as tk
import json
import os

# 游戏常量定义
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20

# 颜色定义
BG_COLOR = "#2C3E50"
GRID_COLOR = "#4A6B7C"  # 进一步降低亮度，减少视觉干扰
BORDER_COLOR = "#E74C3C"
FOOD_COLOR = "#E74C3C"
SCORE_COLOR = "#F1C40F"
STATUS_COLOR = "#3498DB"
FAIL_COLOR = "#E74C3C"

# 方向常量
UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 彩虹颜色（从头到尾渐变）
RAINBOW_COLORS = [
    "#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#00FFFF", "#0000FF", "#8B00FF"
]


class Snake:
    """蛇类，负责管理蛇的移动、生长和绘制"""
    
    def __init__(self, screen, grid_width, grid_height):
        self.screen = screen
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.head_color = "#FFFFFF"
        self.body_color = "#CCCCCC"
        self.reset()
        self.create_turtles()
    
    def reset(self):
        self.body = [
            (self.grid_width // 2, self.grid_height // 2),
            (self.grid_width // 2 - 1, self.grid_height // 2),
            (self.grid_width // 2 - 2, self.grid_height // 2)
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
    
    def create_turtles(self):
        # 蛇头
        self.head_turtle = turtle.Turtle()
        self.head_turtle.speed(0)
        self.head_turtle.shape("square")
        self.head_turtle.color(self.head_color)
        self.head_turtle.penup()
        self.head_turtle.shapesize(0.9, 0.9)
        
        # 蛇身
        self.body_turtles = []
        for _ in range(len(self.body) - 1):
            t = turtle.Turtle()
            t.speed(0)
            t.shape("square")
            t.color(self.body_color)
            t.penup()
            t.shapesize(0.8, 0.8)
            self.body_turtles.append(t)
    
    def update_color(self, head_color, body_color):
        self.head_color = head_color
        self.body_color = body_color
        self.head_turtle.color(head_color)
        for t in self.body_turtles:
            t.color(body_color)
    
    def update_rainbow_colors(self):
        """更新彩虹模式下的蛇身颜色（每节身体不同颜色）"""
        if len(self.body) > 1:
            for i in range(len(self.body) - 1):
                color_index = i % len(RAINBOW_COLORS)
                self.body_turtles[i].color(RAINBOW_COLORS[color_index])
            self.head_turtle.color(RAINBOW_COLORS[0])
    
    def update_direction(self, new_direction):
        if (new_direction[0] != -self.direction[0] or 
            new_direction[1] != -self.direction[1]):
            self.next_direction = new_direction
    
    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)
        self.body.pop()
    
    def check_wall_collision(self):
        head_x, head_y = self.body[0]
        next_head_x = head_x + self.direction[0]
        next_head_y = head_y + self.direction[1]
        return (next_head_x < 0 or next_head_x >= self.grid_width or 
                next_head_y < 0 or next_head_y >= self.grid_height)
    
    def grow(self):
        tail_x, tail_y = self.body[-1]
        self.body.append((tail_x, tail_y))
        
        t = turtle.Turtle()
        t.speed(0)
        t.shape("square")
        t.color(self.body_color)
        t.penup()
        t.shapesize(0.8, 0.8)
        self.body_turtles.append(t)
    
    def draw(self):
        head_x, head_y = self.body[0]
        self.head_turtle.goto(head_x * GRID_SIZE - self.grid_width * GRID_SIZE // 2 + GRID_SIZE // 2,
                             head_y * GRID_SIZE - self.grid_height * GRID_SIZE // 2 + GRID_SIZE // 2)
        
        for i, segment in enumerate(self.body[1:]):
            seg_x, seg_y = segment
            self.body_turtles[i].goto(seg_x * GRID_SIZE - self.grid_width * GRID_SIZE // 2 + GRID_SIZE // 2,
                                      seg_y * GRID_SIZE - self.grid_height * GRID_SIZE // 2 + GRID_SIZE // 2)
    
    def check_self_collision(self):
        head = self.body[0]
        return head in self.body[1:]
    
    def check_obstacle_collision(self, obstacles):
        """检查障碍物碰撞（与边界碰撞逻辑一致：预判下一步位置）"""
        head_x, head_y = self.body[0]
        next_head_x = head_x + self.direction[0]
        next_head_y = head_y + self.direction[1]
        return (next_head_x, next_head_y) in obstacles
    
    def clear(self):
        self.head_turtle.hideturtle()
        for t in self.body_turtles:
            t.hideturtle()


class Food:
    """食物类，负责管理食物的生成和绘制"""
    
    def __init__(self, screen, grid_width, grid_height):
        self.screen = screen
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.position = (0, 0)
        
        self.food_turtle = turtle.Turtle()
        self.food_turtle.speed(0)
        self.food_turtle.shape("circle")
        self.food_turtle.color(FOOD_COLOR)
        self.food_turtle.penup()
        self.food_turtle.shapesize(0.8, 0.8)
        
        self.generate_new([])
    
    def generate_new(self, snake_body, obstacles=[], margin=4):
        while True:
            x = random.randint(margin, self.grid_width - 1 - margin)
            y = random.randint(margin, self.grid_height - 1 - margin)
            self.position = (x, y)
            if self.position not in snake_body and self.position not in obstacles:
                break
    
    def draw(self):
        food_x, food_y = self.position
        self.food_turtle.goto(food_x * GRID_SIZE - self.grid_width * GRID_SIZE // 2 + GRID_SIZE // 2,
                              food_y * GRID_SIZE - self.grid_height * GRID_SIZE // 2 + GRID_SIZE // 2)
    
    def clear(self):
        self.food_turtle.hideturtle()

class Game:
    """游戏主类"""
    
    def __init__(self):
        self.game_mode = None
        self.current_level = 0
        
        # 关卡数据定义（增大地图尺寸，下调速度）
        self.levels = {
            1: {
                "name": "🟢 新手训练营",
                "grid_width": 20,
                "grid_height": 20,
                "speed_multiplier": 0.6,  # 下调速度
                "target_score": 100,
                "obstacles": [],
                "time_limit": 0,
                "description": "熟悉操作，轻松入门"
            },
            2: {
                "name": "🟡 迷宫探险",
                "grid_width": 24,
                "grid_height": 24,
                "speed_multiplier": 0.75,  # 下调速度
                "target_score": 150,
                "obstacles": [(6, 6), (6, 7), (6, 8), (17, 17), (17, 18), (17, 19),
                              (12, 10), (13, 10), (14, 10), (5, 18), (6, 18), (7, 18)],
                "time_limit": 0,
                "description": "绕过障碍，到达终点"
            },
            3: {
                "name": "🔵 限时挑战",
                "grid_width": 24,
                "grid_height": 24,
                "speed_multiplier": 0.9,  # 下调速度
                "target_score": 120,
                "obstacles": [],
                "time_limit": 45,
                "description": "时间紧迫，快速反应"
            },
            4: {
                "name": "🔴 终极考验",
                "grid_width": 26,
                "grid_height": 26,
                "speed_multiplier": 1.0,  # 下调速度
                "target_score": 200,
                "obstacles": [],
                "random_obstacles": True,
                "time_limit": 0,
                "description": "极速挑战，躲避障碍"
            }
        }
        
        # 加载进度
        self.unlocked_levels = self.load_progress()
        
        # 创建屏幕
        self.screen = turtle.Screen()
        self.screen.title("贪吃蛇游戏 🐍")
        self.screen.setup(width=SCREEN_WIDTH + 200, height=SCREEN_HEIGHT + 150)
        self.screen.bgcolor(BG_COLOR)
        self.screen.tracer(0)
        
        # 创建海龟对象
        self.border_turtle = turtle.Turtle()
        self.grid_turtle = turtle.Turtle()
        self.snake = None
        self.food = None
        self.obstacle_turtles = []
        
        # 游戏状态
        self.score = 0
        self.game_over = False
        self.paused = False
        self.level_complete = False
        self.waiting_for_start = True
        
        # 速度控制
        self.base_speed = 0.08
        self.speed_multiplier = 1.0
        self.max_speed_multiplier = 2.5
        self.last_speed_increase = 0
        
        # 彩虹变色控制
        self.rainbow_mode = False
        
        # 创建显示对象
        self.score_pen = turtle.Turtle()
        self.score_pen.speed(0)
        self.score_pen.color(SCORE_COLOR)
        self.score_pen.penup()
        self.score_pen.hideturtle()
        
        self.status_pen = turtle.Turtle()
        self.status_pen.speed(0)
        self.status_pen.color(STATUS_COLOR)
        self.status_pen.penup()
        self.status_pen.hideturtle()
        
        self.fail_reason_pen = turtle.Turtle()
        self.fail_reason_pen.speed(0)
        self.fail_reason_pen.color(FAIL_COLOR)
        self.fail_reason_pen.penup()
        self.fail_reason_pen.hideturtle()
        
        # tkinter 按钮
        self.menu_buttons = []
        self.game_buttons = []
        
        # 创建主菜单
        self.show_main_menu()
        
        # 绑定键盘事件
        self.setup_keybindings()
        
        # 游戏循环
        self.run()
    
    def load_progress(self):
        try:
            if os.path.exists("snake_progress.json"):
                with open("snake_progress.json", "r") as f:
                    data = json.load(f)
                    return data.get("unlocked_levels", [1])
        except:
            pass
        return [1]
    
    def save_progress(self):
        with open("snake_progress.json", "w") as f:
            json.dump({"unlocked_levels": self.unlocked_levels}, f)
    
    def setup_keybindings(self):
        self.screen.listen()
        self.screen.onkeypress(self.go_up, "Up")
        self.screen.onkeypress(self.go_down, "Down")
        self.screen.onkeypress(self.go_left, "Left")
        self.screen.onkeypress(self.go_right, "Right")
        self.screen.onkeypress(self.start_game, "Return")
        self.screen.onkeypress(self.start_game, "space")
        self.screen.onkeypress(self.toggle_pause, "p")
        self.screen.onkeypress(self.toggle_pause, "P")
        self.screen.onkeypress(self.toggle_pause, "1")
        self.screen.onkeypress(self.reset_game, "r")
        self.screen.onkeypress(self.reset_game, "R")
        self.screen.onkeypress(self.reset_game, "2")
        self.screen.onkeypress(self.show_main_menu, "Escape")
        self.screen.listen()
    
    def clear_all_turtles(self):
        """清除所有海龟文字和图形"""
        for t in turtle.turtles():
            t.clear()
            t.hideturtle()
        
        # 重新创建必要的海龟
        self.border_turtle = turtle.Turtle()
        self.grid_turtle = turtle.Turtle()
        
        self.score_pen = turtle.Turtle()
        self.score_pen.speed(0)
        self.score_pen.color(SCORE_COLOR)
        self.score_pen.penup()
        self.score_pen.hideturtle()
        
        self.status_pen = turtle.Turtle()
        self.status_pen.speed(0)
        self.status_pen.color(STATUS_COLOR)
        self.status_pen.penup()
        self.status_pen.hideturtle()
        
        self.fail_reason_pen = turtle.Turtle()
        self.fail_reason_pen.speed(0)
        self.fail_reason_pen.color(FAIL_COLOR)
        self.fail_reason_pen.penup()
        self.fail_reason_pen.hideturtle()
    
    def clear_buttons(self):
        for button in self.menu_buttons + self.game_buttons:
            try:
                button.destroy()
            except:
                pass
        self.menu_buttons = []
        self.game_buttons = []
    
    def clear_game_objects(self):
        if self.snake:
            self.snake.clear()
            self.snake = None
        if self.food:
            self.food.clear()
            self.food = None
        for t in self.obstacle_turtles:
            t.hideturtle()
        self.obstacle_turtles = []
        self.border_turtle.clear()
        self.grid_turtle.clear()

    def show_main_menu(self):
        """显示主菜单"""
        self.clear_buttons()
        self.clear_game_objects()
        self.clear_all_turtles()
        
        self.game_mode = None
        self.current_level = 0
        
        self.screen.bgcolor(BG_COLOR)
        
        # 绘制标题
        title = turtle.Turtle()
        title.speed(0)
        title.color("#FFFFFF")
        title.penup()
        title.hideturtle()
        title.goto(0, 150)
        title.write("🐍 贪吃蛇游戏 🐍", align="center", font=("微软雅黑", 36, "bold"))
        
        # 创建按钮
        canvas = self.screen.getcanvas()
        root = canvas.winfo_toplevel()
        
        # 无尽模式按钮
        endless_btn = tk.Button(root, text="🎯 无尽模式", bg="#2ECC71", fg="white",
                              font=("微软雅黑", 14, "bold"), width=18, height=2,
                              command=self.start_endless_mode)
        canvas.create_window(0, 30, window=endless_btn)
        self.menu_buttons.append(endless_btn)
        
        # 关卡模式按钮
        level_btn = tk.Button(root, text="📋 关卡模式", bg="#3498DB", fg="white",
                             font=("微软雅黑", 14, "bold"), width=18, height=2,
                             command=self.show_level_select)
        canvas.create_window(0, -40, window=level_btn)
        self.menu_buttons.append(level_btn)
        
        # 退出按钮
        exit_btn = tk.Button(root, text="❌ 退出游戏", bg="#E74C3C", fg="white",
                           font=("微软雅黑", 14, "bold"), width=18, height=2,
                           command=self.exit_game)
        canvas.create_window(0, -110, window=exit_btn)
        self.menu_buttons.append(exit_btn)
        
        # 底部提示
        hint = turtle.Turtle()
        hint.speed(0)
        hint.color("#95A5A6")
        hint.penup()
        hint.hideturtle()
        hint.goto(0, -200)
        hint.write("🎮 点击按钮选择模式", align="center", font=("微软雅黑", 12, "normal"))
        
        self.screen.update()
    
    def start_endless_mode(self):
        """开始无尽模式（手动触发开始）"""
        self.clear_buttons()
        self.clear_all_turtles()
        self.game_mode = "endless"
        
        # 初始化游戏对象（使用30x30大地图）
        self.init_game_objects(30, 30)
        
        # 等待用户按键开始
        self.waiting_for_start = True
        self.show_game_ui()
    
    def start_level(self, level_num):
        """开始指定关卡（手动触发开始）"""
        self.clear_buttons()
        self.clear_all_turtles()
        self.game_mode = "level"
        self.current_level = level_num
        level = self.levels[level_num]
        
        # 初始化游戏对象
        grid_width = level["grid_width"]
        grid_height = level["grid_height"]
        self.init_game_objects(grid_width, grid_height)
        
        # 生成障碍物
        if level.get("random_obstacles"):
            self.generate_random_obstacles(grid_width, grid_height)
        else:
            for obs in level["obstacles"]:
                self.create_obstacle(obs[0], obs[1], grid_width, grid_height)
        
        # 设置速度
        self.speed_multiplier = level["speed_multiplier"]
        
        # 等待用户按键开始
        self.waiting_for_start = True
        self.show_game_ui()
    
    def show_level_select(self):
        """显示关卡选择界面（优化排版）"""
        self.clear_buttons()
        self.clear_game_objects()
        self.clear_all_turtles()
        
        self.screen.bgcolor(BG_COLOR)
        
        # 创建返回按钮
        canvas = self.screen.getcanvas()
        root = canvas.winfo_toplevel()
        
        back_btn = tk.Button(root, text="← 返回主菜单", bg="#7F8C8D", fg="white",
                           font=("微软雅黑", 12, "bold"), width=12, height=1,
                           command=self.show_main_menu)
        canvas.create_window(-250, -260, window=back_btn)
        self.menu_buttons.append(back_btn)
        
        # 显示标题
        title = turtle.Turtle()
        title.speed(0)
        title.color("#FFFFFF")
        title.penup()
        title.hideturtle()
        title.goto(0, 200)
        title.write("📋 选择关卡", align="center", font=("微软雅黑", 28, "bold"))
        
        # 显示关卡列表（优化布局）
        y_start = 150
        
        # 创建关卡顺序映射（交换按钮功能：1号↔4号，2号↔3号）
        # 按钮显示位置与关卡名称对齐，但点击后启动交换后的关卡
        swap_mapping = {1: 4, 2: 3, 3: 2, 4: 1}
        
        for level_num in range(1, 5):
            level = self.levels[level_num]
            y_pos = y_start - (level_num - 1) * 85
            
            # 关卡名称
            level_text = turtle.Turtle()
            level_text.speed(0)
            unlocked = level_num in self.unlocked_levels
            level_text.color("#FFFFFF" if unlocked else "#7F8C8D")
            level_text.penup()
            level_text.hideturtle()
            level_text.goto(-180, y_pos)
            
            lock_icon = "" if unlocked else "🔒 "
            level_text.write(f"{lock_icon}{level['name']}", align="left", font=("微软雅黑", 18, "bold"))
            
            # 关卡描述
            desc_text = turtle.Turtle()
            desc_text.speed(0)
            desc_text.color("#95A5A6" if unlocked else "#7F8C8D")
            desc_text.penup()
            desc_text.hideturtle()
            desc_text.goto(-180, y_pos - 22)
            desc_text.write(f"   {level['description']}", align="left", font=("微软雅黑", 11, "normal"))
            
            # 关卡信息
            info_text = turtle.Turtle()
            info_text.speed(0)
            info_text.color("#BDC3C7" if unlocked else "#7F8C8D")
            info_text.penup()
            info_text.hideturtle()
            info_text.goto(-180, y_pos - 40)
            info_text.write(f"   🎯 目标: {level['target_score']}分 | ⚡ 速度: {level['speed_multiplier']}x", 
                          align="left", font=("微软雅黑", 10, "normal"))
            
            # 关卡按钮（与关卡名称对齐，但功能交换）
            # 检查交换后的关卡是否解锁
            target_level = swap_mapping[level_num]
            target_unlocked = target_level in self.unlocked_levels
            
            if target_unlocked:
                # 使用默认参数解决闭包问题
                def make_start_func(n):
                    return lambda: self.start_level(n)
                
                level_btn = tk.Button(root, text=f"开始", bg="#3498DB", fg="white",
                                     font=("微软雅黑", 11, "bold"), width=8, height=1,
                                     command=make_start_func(target_level))
                # 按钮y坐标往上移动5像素，与关卡名称更好地对齐
                canvas.create_window(180, y_pos + 5, window=level_btn)
                self.menu_buttons.append(level_btn)
            else:
                locked_label = tk.Label(root, text="🔒 未解锁", bg="#7F8C8D", fg="white",
                                       font=("微软雅黑", 11, "bold"), width=8, height=1)
                canvas.create_window(180, y_pos + 5, window=locked_label)
                self.menu_buttons.append(locked_label)
        
        self.screen.update()

    def start_level(self, level_num):
        """开始指定关卡"""
        self.clear_buttons()
        self.clear_all_turtles()
        self.game_mode = "level"
        self.current_level = level_num
        level = self.levels[level_num]
        
        # 初始化游戏对象
        grid_width = level["grid_width"]
        grid_height = level["grid_height"]
        self.init_game_objects(grid_width, grid_height)
        
        # 生成障碍物
        if level.get("random_obstacles"):
            self.generate_random_obstacles(grid_width, grid_height)
        else:
            for obs in level["obstacles"]:
                self.create_obstacle(obs[0], obs[1], grid_width, grid_height)
        
        # 设置速度
        self.speed_multiplier = level["speed_multiplier"]
        
        # 设置时间限制
        self.time_limit = level.get("time_limit", 0)
        self.time_left = self.time_limit
        
        # 等待用户按键开始
        self.waiting_for_start = True
        self.show_game_ui()
    
    def init_game_objects(self, grid_width, grid_height):
        """初始化游戏对象"""
        # 清除旧对象
        if self.snake:
            self.snake.clear()
        if self.food:
            self.food.clear()
        for t in self.obstacle_turtles:
            t.hideturtle()
        self.obstacle_turtles = []
        
        # 重置状态
        self.score = 0
        self.game_over = False
        self.paused = False
        self.level_complete = False
        self.waiting_for_start = True
        self.speed_multiplier = 1.0
        self.last_speed_increase = 0
        self.rainbow_mode = False
        self.current_obstacles = []  # 重置当前障碍物列表
        self.time_left = 0  # 剩余时间（秒）
        self.start_time = 0  # 游戏开始时间
        
        # 保存当前地图大小
        self.current_grid_width = grid_width
        self.current_grid_height = grid_height
        
        # 绘制边界和网格
        self.draw_game_border(grid_width, grid_height)
        self.draw_game_grid(grid_width, grid_height)
        
        # 创建蛇和食物
        self.snake = Snake(self.screen, grid_width, grid_height)
        self.food = Food(self.screen, grid_width, grid_height)
        self.food.generate_new(self.snake.body, [], margin=4)
        
        # 创建游戏按钮
        self.create_game_buttons()
        
        # 更新显示
        self.update_score_display()
    
    def draw_game_border(self, grid_width, grid_height):
        """绘制游戏边界"""
        width = grid_width * GRID_SIZE
        height = grid_height * GRID_SIZE
        
        self.border_turtle.clear()
        self.border_turtle.speed(0)
        self.border_turtle.color(BORDER_COLOR)
        self.border_turtle.pensize(3)
        self.border_turtle.penup()
        self.border_turtle.goto(-width//2 - 2, -height//2 - 2)
        self.border_turtle.pendown()
        
        for _ in range(4):
            self.border_turtle.forward(width + 4)
            self.border_turtle.left(90)
        
        self.border_turtle.hideturtle()
    
    def draw_game_grid(self, grid_width, grid_height):
        """绘制游戏网格"""
        width = grid_width * GRID_SIZE
        height = grid_height * GRID_SIZE
        
        self.grid_turtle.clear()
        self.grid_turtle.speed(0)
        self.grid_turtle.color(GRID_COLOR)
        self.grid_turtle.pensize(1)
        self.grid_turtle.penup()
        
        for x in range(-width//2, width//2 + 1, GRID_SIZE):
            self.grid_turtle.goto(x, -height//2)
            self.grid_turtle.pendown()
            self.grid_turtle.goto(x, height//2)
            self.grid_turtle.penup()
        
        for y in range(-height//2, height//2 + 1, GRID_SIZE):
            self.grid_turtle.goto(-width//2, y)
            self.grid_turtle.pendown()
            self.grid_turtle.goto(width//2, y)
            self.grid_turtle.penup()
        
        self.grid_turtle.hideturtle()
    
    def create_obstacle(self, x, y, grid_width, grid_height):
        """创建障碍物"""
        t = turtle.Turtle()
        t.speed(0)
        t.shape("square")
        t.color("#5D6D7E")
        t.penup()
        t.shapesize(0.9, 0.9)
        
        t.goto(x * GRID_SIZE - grid_width * GRID_SIZE // 2 + GRID_SIZE // 2,
               y * GRID_SIZE - grid_height * GRID_SIZE // 2 + GRID_SIZE // 2)
        
        self.obstacle_turtles.append(t)
        # 不再修改原始关卡数据，避免重复添加
        # 将障碍物位置存储在单独的列表中
        if not hasattr(self, 'current_obstacles'):
            self.current_obstacles = []
        self.current_obstacles.append((x, y))
    
    def generate_random_obstacles(self, grid_width, grid_height):
        """生成随机障碍物（不在蛇头附近生成）"""
        num_obstacles = random.randint(20, 30)
        margin = 6
        
        # 获取蛇头位置
        head_pos = self.snake.body[0]
        
        for _ in range(num_obstacles):
            while True:
                x = random.randint(margin, grid_width - 1 - margin)
                y = random.randint(margin, grid_height - 1 - margin)
                pos = (x, y)
                
                # 检查是否与蛇身重叠
                if pos in self.snake.body:
                    continue
                
                # 检查是否与已生成的障碍物重叠
                if pos in self.current_obstacles:
                    continue
                
                # 检查是否在蛇头附近（3格范围内）
                head_x, head_y = head_pos
                if abs(x - head_x) <= 3 and abs(y - head_y) <= 3:
                    continue
                
                self.create_obstacle(x, y, grid_width, grid_height)
                break

    def show_game_ui(self):
        """显示游戏界面UI"""
        self.score_pen.goto(0, SCREEN_HEIGHT//2 + 30)
        self.update_score_display()
        
        if self.game_mode == "level":
            level = self.levels[self.current_level]
            self.status_pen.goto(0, SCREEN_HEIGHT//2 + 60)
            self.status_pen.clear()
            self.status_pen.color("#FFFFFF")
            self.status_pen.write(f"{level['name']} | 目标: {level['target_score']}分", align="center", font=("微软雅黑", 16, "bold"))
        elif self.game_mode == "endless":
            self.status_pen.goto(0, SCREEN_HEIGHT//2 + 60)
            self.status_pen.clear()
            self.status_pen.color("#FFFFFF")
            self.status_pen.write("🎯 无尽模式", align="center", font=("微软雅黑", 16, "bold"))
        
        self.show_start_message()
        self.draw_key_hints()
    
    def create_game_buttons(self):
        """创建游戏界面按钮"""
        self.clear_buttons()
        
        canvas = self.screen.getcanvas()
        root = canvas.winfo_toplevel()
        
        button_x = SCREEN_WIDTH // 2 + 80
        
        # 返回菜单按钮
        menu_btn = tk.Button(root, text="← 菜单", bg="#7F8C8D", fg="white",
                            font=("微软雅黑", 12, "bold"), width=10, height=1,
                            command=self.show_main_menu)
        canvas.create_window(button_x, 100, window=menu_btn)
        self.game_buttons.append(menu_btn)
        
        # 暂停按钮
        self.pause_btn = tk.Button(root, text="暂停", bg="#F39C12", fg="white",
                                  font=("微软雅黑", 12, "bold"), width=10, height=1,
                                  command=self.toggle_pause)
        canvas.create_window(button_x, 50, window=self.pause_btn)
        self.game_buttons.append(self.pause_btn)
        
        # 重新开始按钮
        reset_btn = tk.Button(root, text="重新开始", bg="#E74C3C", fg="white",
                             font=("微软雅黑", 12, "bold"), width=10, height=1,
                             command=self.reset_game)
        canvas.create_window(button_x, 0, window=reset_btn)
        self.game_buttons.append(reset_btn)
    
    def draw_key_hints(self):
        """绘制按键提示"""
        hint = turtle.Turtle()
        hint.speed(0)
        hint.color("#BDC3C7")
        hint.penup()
        hint.hideturtle()
        hint.goto(-SCREEN_WIDTH//2 + 10, -SCREEN_HEIGHT//2 - 35)
        
        if self.game_mode == "level":
            hint.write("↑↓←→移动 | P暂停 | R重开 | Esc返回菜单 | 碰到障碍物游戏结束", align="left", font=("微软雅黑", 10, "normal"))
        else:
            hint.write("↑↓←→移动 | P暂停 | R重开 | Esc返回菜单", align="left", font=("微软雅黑", 10, "normal"))
    
    def exit_game(self):
        """退出游戏"""
        self.screen.bye()

    def start_game(self):
        """开始游戏（带按键反馈）"""
        if self.waiting_for_start:
            self.waiting_for_start = False
            # 记录游戏开始时间（用于倒计时）
            self.start_time = time.time()
            # 显示按键反馈
            self.show_start_feedback()
    
    def show_start_feedback(self):
        """显示开始反馈效果"""
        feedback = turtle.Turtle()
        feedback.speed(0)
        feedback.color("#2ECC71")
        feedback.penup()
        feedback.hideturtle()
        feedback.goto(0, 0)
        feedback.write("🚀 开始！", align="center", font=("微软雅黑", 32, "bold"))
        
        # 1秒后消失
        def hide_feedback():
            feedback.clear()
        self.screen.ontimer(hide_feedback, 500)
    
    def go_up(self):
        """向上移动"""
        if self.snake:
            self.snake.update_direction(UP)
    
    def go_down(self):
        """向下移动"""
        if self.snake:
            self.snake.update_direction(DOWN)
    
    def go_left(self):
        """向左移动"""
        if self.snake:
            self.snake.update_direction(LEFT)
    
    def go_right(self):
        """向右移动"""
        if self.snake:
            self.snake.update_direction(RIGHT)
    
    def toggle_pause(self):
        """切换暂停状态"""
        if not self.game_over and not self.waiting_for_start:
            self.paused = not self.paused
            if self.pause_btn:
                self.pause_btn.config(text="继续" if self.paused else "暂停")
    
    def update_score_display(self):
        """更新分数显示"""
        self.score_pen.clear()
        self.score_pen.write(f"🎯 分数: {self.score}", align="center", font=("微软雅黑", 22, "bold"))
    
    def show_start_message(self):
        """显示开始提示"""
        self.status_pen.clear()
        self.status_pen.color(STATUS_COLOR)
        self.status_pen.write("按 Enter 或 空格键 开始游戏", align="center", font=("微软雅黑", 18, "normal"))
    
    def show_fail_reason(self, reason):
        """显示失败原因"""
        self.fail_reason_pen.clear()
        self.fail_reason_pen.write(reason, align="center", font=("微软雅黑", 16, "bold"))
    
    def show_status(self, message):
        """显示游戏状态信息"""
        self.status_pen.clear()
        self.status_pen.color(STATUS_COLOR)
        self.status_pen.write(message, align="center", font=("微软雅黑", 16, "normal"))
    
    def check_collisions(self):
        """检查碰撞"""
        head = self.snake.body[0]
        
        # 检查食物碰撞
        if head == self.food.position:
            self.score += 10
            self.snake.grow()
            self.update_score_display()
            
            # 无尽模式变色和加速
            if self.game_mode == "endless":
                self.update_snake_color()
            
            # 关卡模式检查目标
            if self.game_mode == "level":
                level = self.levels[self.current_level]
                if self.score >= level["target_score"]:
                    self.level_complete = True
                    self.show_level_complete()
                    return
            
            # 生成新食物
            obstacles = self.levels.get(self.current_level, {}).get("obstacles", [])
            while self.food.position in self.snake.body or self.food.position in obstacles:
                self.food.generate_new(self.snake.body, obstacles, margin=4)
        
        # 检查自身碰撞
        if self.snake.check_self_collision():
            self.game_over = True
            self.show_fail_reason("头尾相触 - 游戏失败！")
        
        # 检查障碍物碰撞（关卡模式）
        if self.game_mode == "level":
            # 获取所有障碍物：包括关卡定义的和当前生成的
            obstacles = self.levels.get(self.current_level, {}).get("obstacles", [])
            # 添加当前游戏中的障碍物（随机生成的）
            if hasattr(self, 'current_obstacles'):
                obstacles += self.current_obstacles
            
            if self.snake.check_obstacle_collision(obstacles):
                self.game_over = True
                self.show_fail_reason("碰到障碍物 - 游戏失败！")
    def update_snake_color(self):
        """根据分数更新蛇的颜色（无尽模式）"""
        colors = {
            0: ("#FFFFFF", "#CCCCCC"),      # 白色
            20: ("#2ECC71", "#58D68D"),     # 绿色
            50: ("#3498DB", "#5DADE2"),     # 蓝色
            90: ("#9B59B6", "#BB8FCE"),     # 紫色
            140: ("#F1C40F", "#F4D03F"),    # 金色
            200: ("#E74C3C", "#EC7063")     # 红色
        }
        
        # 检查彩虹模式（300分）
        if self.score >= 300:
            self.rainbow_mode = True
            self.snake.update_rainbow_colors()
        else:
            self.rainbow_mode = False
            current_color = colors[0]
            for threshold in sorted(colors.keys()):
                if self.score >= threshold:
                    current_color = colors[threshold]
            self.snake.update_color(current_color[0], current_color[1])
            
            # 加速
            if self.score <= 300:
                current_segment = sum(1 for t in sorted(colors.keys()) if self.score >= t)
                if current_segment > self.last_speed_increase:
                    self.speed_multiplier = min(self.speed_multiplier + 0.1, self.max_speed_multiplier)
                    self.last_speed_increase = current_segment
    
    def show_level_complete(self):
        """显示关卡完成"""
        if self.current_level < 4 and (self.current_level + 1) not in self.unlocked_levels:
            self.unlocked_levels.append(self.current_level + 1)
            self.save_progress()
        
        self.status_pen.clear()
        self.status_pen.color("#2ECC71")
        self.status_pen.write(f"🎉 恭喜通关！得分: {self.score}", align="center", font=("微软雅黑", 24, "bold"))
        
        self.fail_reason_pen.clear()
        self.fail_reason_pen.color("#FFFFFF")
        self.fail_reason_pen.write("按 R 键重玩 | 按 Esc 返回菜单", align="center", font=("微软雅黑", 14, "normal"))

    def update(self):
        """更新游戏状态"""
        if not self.game_over and not self.paused and not self.waiting_for_start and not self.level_complete:
            # 处理倒计时（限时挑战关卡）
            if self.game_mode == "level" and self.time_limit > 0:
                elapsed = time.time() - self.start_time
                self.time_left = max(0, self.time_limit - int(elapsed))
                
                # 检查时间是否耗尽
                if self.time_left <= 0:
                    self.game_over = True
                    self.show_fail_reason("时间耗尽 - 游戏失败！")
                    return
            
            if self.snake.check_wall_collision():
                self.game_over = True
                self.show_fail_reason("头部碰墙 - 游戏失败！")
            else:
                self.snake.move()
                self.check_collisions()
        
        if self.rainbow_mode and not self.game_over and not self.paused:
            self.snake.update_rainbow_colors()
    
    def draw(self):
        """绘制游戏画面"""
        if self.snake and self.food:
            if not self.waiting_for_start:
                self.status_pen.clear()
                # 显示关卡信息（包含倒计时）
                if self.game_mode == "level":
                    level = self.levels[self.current_level]
                    status_text = f"{level['name']} | 目标: {level['target_score']}分"
                    # 如果有限时，显示倒计时
                    if self.time_limit > 0:
                        # 时间少于10秒时用红色显示
                        time_color = "#E74C3C" if self.time_left <= 10 else "#FFFFFF"
                        self.status_pen.color(time_color)
                        status_text += f" | ⏱️ {self.time_left}秒"
                    else:
                        self.status_pen.color("#FFFFFF")
                    self.status_pen.write(status_text, align="center", font=("微软雅黑", 16, "bold"))
            
            self.snake.draw()
            self.food.draw()
            
            if self.paused and not self.game_over:
                self.show_status("⏸️ 游戏暂停 - 按 P 键继续")
            if self.game_over:
                self.show_status("💀 游戏结束！按 R 键重新开始")
        
        self.screen.update()
    
    def reset_game(self):
        """重置游戏"""
        if self.game_mode == "level":
            self.start_level(self.current_level)
        else:
            self.start_endless_mode()
    
    def run(self):
        """游戏主循环（优化按键响应和速度控制）"""
        last_update_time = time.time()
        
        while True:
            # 多次调用 listen() 确保按键响应灵敏
            self.screen.listen()
            
            current_time = time.time()
            
            if self.game_mode in ["endless", "level"]:
                # 计算更新间隔（基于速度）
                update_interval = self.base_speed / self.speed_multiplier
                
                # 只有当时间间隔达到时才更新游戏状态
                if current_time - last_update_time >= update_interval:
                    self.update()
                    self.draw()
                    last_update_time = current_time
            
            # 使用更短的睡眠时间提高响应速度
            time.sleep(0.01)
            self.screen.update()


if __name__ == "__main__":
    game = Game()
