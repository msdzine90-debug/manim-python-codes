from manim import *
from manim.opengl import *
import numpy as np

class WavePackets(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60*DEGREES)

        center1 = np.array([0, 0])
        target_radius = 3 

        radius_tracker = ValueTracker(0.1) 
        angle_tracker = ValueTracker(0.0)   

        ## Defining initial surface function
        def uv_surface(u, v):
            theta = angle_tracker.get_value()
            r = radius_tracker.get_value()
            center2 = center1 + r * np.array([np.cos(theta), np.sin(theta)])
            return np.array([
                u,
                v,
                np.exp(-(u**2 + v**2)) + np.exp(-((u - center2[0])**2 + (v - center2[1])**2))
            ])

        wp1 = OpenGLSurface(
            uv_surface,
            u_range=[-5, 5],
            v_range=[-5, 5],
            resolution=(101, 101),
        )

        ## Color Function: Returns value from -1 to 1 which will be put into .set_color_by_func()
        def two_gaussian_color_func(x, y, z):
            theta = angle_tracker.get_value()
            r = radius_tracker.get_value()
            outer_center = center1 + r * np.array([np.cos(theta), np.sin(theta)])
            d1 = (x - center1[0])**2 + (y - center1[1])**2
            d2 = (x - outer_center[0])**2 + (y - outer_center[1])**2
            return np.exp(-d1) - np.exp(-d2)

        wp1.set_color_by_func(
            two_gaussian_color_func,
            colormap=("BLUE", "RED"),
            min_value=-1,
            max_value=1
        )

        self.play(Create(wp1))

        def update_surface(surface):

            ## Getting Surface Mesh Points
            nu, nv = surface.resolution
            u_vals = np.linspace(-5, 5, nu)
            v_vals = np.linspace(-5, 5, nv)
            points_list = []
            for du, dv in [(0,0), (surface.epsilon,0), (0,surface.epsilon)]:
                uv_grid = np.array([[[u+du, v+dv] for v in v_vals] for u in u_vals])
                point_grid = np.apply_along_axis(lambda p: uv_surface(*p), 2, uv_grid)
                points_list.append(point_grid.reshape((nu*nv, 3)))
            surface.set_points(np.vstack(points_list))

            ## Setting color of function for each frame
            surface.set_color_by_func(
                two_gaussian_color_func,
                colormap=("BLUE", "RED"),
                min_value=-1,
                max_value=1
            )
            return surface

        wp1.add_updater(update_surface)

        self.play(radius_tracker.animate.set_value(target_radius), run_time=2, rate_func=smooth)

        self.play(angle_tracker.animate.set_value(4*PI), run_time=12, rate_func=linear)
        self.wait()

        wp1.remove_updater(update_surface)
