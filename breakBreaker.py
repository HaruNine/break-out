import tkinter as tk
import random

class BrickBreaker(tk.Frame):
    def __init__(self, root):
        super(BrickBreaker, self).__init__(root)
        self.life = 3
        self.width = 1210
        self.height= 480
        self.canvas = tk.Canvas(self, bg = 'blue', width = self.width, height = self.height)
        self.canvas.pack()
        self.pack()


        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 420)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            f1 = random.randrange(1, 6)
            f2 = random.randrange(1, 6)
            f3 = random.randrange(1, 6)
            f4 = random.randrange(1, 6)
            f5 = random.randrange(1, 6)
            self.add_brick(x + 37.5, 50, f5)
            self.add_brick(x + 37.5, 70, f4)
            self.add_brick(x + 37.5, 90, f3)
            self.add_brick(x + 37.5, 110, f2)
            self.add_brick(x + 37.5, 130, f1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))

    def setup_game(self):
           self.add_ball()
           self.update_life_text()
           self.text = self.draw_text(600, 200,
                                      '스패이스바를 눌러 시작하세요!')
           self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 280)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_life_text(self):
        text = 'LIFE: %s' % self.life
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(600, 200, '다 부셔버렸네요~')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.life -= 1
            if self.life < 0:
                self.draw_text(600, 200, '죽어버렸네요~')
                self.draw_text(600, 260, f'벽돌이 {num_bricks}만큼 남았자나요~')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 20
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='white')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, velocity):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + velocity >= 0 and coords[2] + velocity <= width:
            super(Paddle, self).move(velocity, 0)
            if self.ball is not None:
                self.ball.move(velocity, 0)

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [random.choice([2, 1, -1, -2]), -1]
        self.speed = 7
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='red')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

class Brick(GameObject):
    COLORS = {1: '#00f7ff', 2: '#48ff00', 3: '#f6ff00', 4: '#ff9100', 5: '#ff0000'}
    # 1 = 하늘색 2 = 녹색 3 = 노란색 4 = 주황색 5 = 빨간색

    def __init__(self, canvas, x, y, hits):
        self.width = 50
        self.height = 20
        self.hits = hits

        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])

if __name__ == '__main__':
    root = tk.Tk()
    root.title('벽돌 깨기 !!')
    game = BrickBreaker(root)
    game.mainloop()