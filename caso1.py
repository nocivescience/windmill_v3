from manim import *
class EjemploScene(Scene):
    def construct(self):
        dot=Dot().move_to(3*RIGHT)
        letter=Integer(dot.get_center()[0])
        letter.add_updater(lambda t: t.set_value(dot.get_center()[0]))
        letter.scale(.6)
        letter.add_updater(lambda t: t.next_to(dot,UP,buff=.2))
        self.add(letter)
        self.play(dot.animate.shift(6*LEFT),run_time=4)
        self.wait()