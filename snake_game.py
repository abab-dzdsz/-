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