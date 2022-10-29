from manim import *
class WindmillScene(Scene):
    CONFIG = {
        "dot_config": {
            "fill_color": LIGHT_GREY,
            "radius": 0.1,
            "background_stroke_width": 2,
            "background_stroke_color": BLACK,
        },
        "windmill_style": {
            "stroke_color": RED,
            "stroke_width": 2,
            "background_stroke_width": 3,
            "background_stroke_color": BLACK,
        },
        "windmill_length": 2 * config['frame_width'],
        "windmill_rotation_speed": 0.25,
        "hit_sound": "pen_click.wav",
        "leave_shadows": False,
    }
    def construct(self):
        points=self.get_random_point_set(n_points=20)
        windmill=self.get_windmill(points=points)
        dots=self.get_dots(points)
        dot_pivot=self.get_pivot_dot(windmill)
        dots_non_pivot=self.next_pivot_and_angle(windmill)
        for mob in [
            dots,
            windmill,
            dot_pivot,
            *dots_non_pivot[-1],
        ]:
            self.play(Create(mob))
        run_time=self.rotate_next_pivot(windmill)
        self.let_windmill_run(windmill,4)
        next_pivot, angle=self.next_pivot_and_angle(windmill)
        self.wait()
    def get_random_point_set(self, n_points=11, width=6, height=6):
        return np.array([
            [
                -width / 2 + np.random.random() * width,
                -height / 2 + np.random.random() * height,
                0
            ]
            for n in range(n_points)
        ])
    def get_dots(self, points):
        return VGroup(*[
            Dot(point, **self.CONFIG['dot_config'])
            for point in points
        ])
    def get_windmill(self,points,pivot=None,angle=TAU/8):
        windmill=Line(LEFT,RIGHT)
        windmill.set_angle(angle)
        windmill.set_length(self.CONFIG['windmill_length'])
        windmill.points_set=points
        if pivot is not None:
            windmill.pivot=pivot
        else:
            windmill.pivot=points[0]
        windmill.rot_speed=self.CONFIG['windmill_rotation_speed']
        windmill.add_updater(lambda l: l.move_to(l.pivot))
        return windmill
    def get_pivot_dot(self,windmill):
        pivot_dot=Dot(color=RED,radius=0.06).move_to(windmill.pivot)
        pivot_dot.set_z_index(5)
        pivot_dot.add_updater(lambda t: t.move_to(windmill.pivot))
        return pivot_dot
    def next_pivot_and_angle(self,windmill):
        curr_angle=windmill.get_angle()
        line=Line(LEFT,RIGHT)
        line.set_angle(curr_angle)
        line.to_edge(UL,buff=1)
        line.add_updater(lambda t:t.rotate(TAU))
        pivot=windmill.pivot
        non_pivots=list(
            filter(lambda t: not np.all(t==pivot),windmill.points_set)
        )
        dots_non_pivot=VGroup(*[
            Dot(color=BLACK,radius=0.07).move_to(point) for point in non_pivots
        ])
        dots_non_pivot.set_z_index(3)
        angles=np.array([
            -(angle_of_vector(point-pivot)-curr_angle)%PI
            for point in non_pivots
        ])
        integers=VGroup()
        for angle,point in zip(angles,non_pivots):
            integer=Integer(angle)
            integer.add_updater(lambda t: t.set_value(angle))
            integer.next_to(point,UP,buff=.1)
            integer.scale(.6)
            integers.add(integer)
        tiny_indices=angles<1e-6
        textos=VGroup()
        for tiny_index, point in zip(tiny_indices,non_pivots):
            texto=Tex(tiny_index)
            texto.add_updater(lambda t:t.set_value(tiny_index))
            texto.next_to(point,DOWN,buff=.1)
            texto.scale(.6)
            textos.add(texto)
        if np.all(tiny_indices):
            return non_pivots[0], PI
        angles[tiny_indices]=np.inf
        index=np.argmin(angles)
        return [[non_pivots[index],angles[index]], [line,dots_non_pivot,integers,textos]]
    def rotate_next_pivot(self,windmill,max_time=None,added_anims=None):
        new_pivot,angle=self.next_pivot_and_angle(windmill)[0]
        changle_pivot_at_end=True
        if added_anims is None:
            added_anims=[]
        run_time=angle/windmill.rot_speed
        if max_time is not None and run_time>max_time:
            ratio=max_time/run_time
            rate_func=(lambda t: ratio*t)
            run_time=max_time
            changle_pivot_at_end=False
        else:
            rate_func=linear
        self.play(Rotate(windmill,angle=-angle,rate_func=rate_func,run_time=run_time))
        if changle_pivot_at_end:
            self.handle_pivot_change(windmill,new_pivot)
        return run_time
    def handle_pivot_change(self,windmill,new_pivot):
        windmill.pivot=new_pivot
    def let_windmill_run(self,windmill,time):
        while time>0:
            last_run_time=self.rotate_next_pivot(windmill,time)
            time-=last_run_time