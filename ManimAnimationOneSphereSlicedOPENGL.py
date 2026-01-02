from manim import *
from manim.opengl import *
import numpy as np


class SphereSliceGL(ThreeDScene):
    def construct(self):
        #--------------
        # CONFIGURATION
        #--------------
        NUM_SLICES = 5
        RADIUS = 1.5
        START_COLOR = GREY_B
        COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]
        SIDE_COLOR = MAROON_C
        PART_LABELS = ["mitochondria", "nucleus", "ribosomes"] 
        EXPLODE_DISTANCE = 3.0
        SLICE_ANGLE = TAU / NUM_SLICES
        CAMERA_OFFSET = 90 * DEGREES
        LABEL_COLOR = WHITE
        TITLE_COLOR = WHITE
        TITLE_TEXT = "Sphere sliced into individual identical slices"

        #---------------------
        # INITIAL CAMERA SETUP
        #---------------------
        first_midpoint = (SLICE_ANGLE / 2) + CAMERA_OFFSET
        self.set_camera_orientation(phi=75 * DEGREES, theta=first_midpoint)

        #---------------------
        # INITIAL LIGHT SETUP
        #---------------------
        light_pos = np.array([0.0, -4.0, 5.0])
        self.renderer.camera.light_source.move_to(light_pos)

        # Light rotation
        def rotate_z(vec, angle):
            c, s = np.cos(angle), np.sin(angle)
            return np.array([
                c * vec[0] - s * vec[1],
                s * vec[0] + c * vec[1],
                vec[2],
            ])

        #----------------
        # GENERATE SLICES
        #----------------

        # Grouping all slices into a sphere
        all_slices = Group()
        direction_list = []

        for i in range(NUM_SLICES):
            math_midpoint = (i * SLICE_ANGLE) + (SLICE_ANGLE / 2)
            direction_list.append(
                np.array([np.cos(math_midpoint), np.sin(math_midpoint), 0])
            )

            # Positions for making the slice cuts
            p_start = i * SLICE_ANGLE
            p_end = (i + 1) * SLICE_ANGLE

            # Create outer curved surface
            outer = OpenGLSurface(
                lambda u, v, ps=p_start, pe=p_end: np.array([
                    RADIUS * np.sin(u) * np.cos(ps + v * (pe - ps)),
                    RADIUS * np.sin(u) * np.sin(ps + v * (pe - ps)),
                    RADIUS * np.cos(u),
                ]),
                u_range=[0, PI],
                v_range=[0, 1],
                color=START_COLOR,
                opacity=1.0
            )

            # Create flat side surfaces
            sides = Group()
            for p in (p_start, p_end):
                side = OpenGLSurface(
                    lambda u, v, p_val=p: np.array([
                        u * RADIUS * np.sin(v * PI) * np.cos(p_val),
                        u * RADIUS * np.sin(v * PI) * np.sin(p_val),
                        u * RADIUS * np.cos(v * PI),
                    ]),
                    u_range=[0, 1],
                    v_range=[0, 1],
                    color=SIDE_COLOR,
                    opacity=1.0
                )
                sides.add(side)

            all_slices.add(Group(outer, sides))

        #------------------
        # TITLE SETUP
        #------------------
        title = Text(TITLE_TEXT, color=TITLE_COLOR, font_size=36)
        title.to_edge(UP, buff=0.5)
        
        # This is the "Billboard Effect": fixing it to the screen frame
        self.add_fixed_in_frame_mobjects(title)

        # Move the sphere group way down and slightly back so it's off-screen 
        all_slices.move_to([0, -200, -100])

        # Add all slices (sphere) and fade in title
        self.add(all_slices)

        # Sphere and title animation
        self.play(
            all_slices.animate.move_to(ORIGIN),
            FadeIn(title),
            run_time=3,
            rate_func= smooth
        )
        self.wait(1)

        #---------------
        # ANIMATION LOOP
        #---------------
        current_theta = first_midpoint

        for i in range(NUM_SLICES):
            math_midpoint = (i * SLICE_ANGLE) + (SLICE_ANGLE / 2)
            target_theta = math_midpoint + CAMERA_OFFSET

            delta_theta = target_theta - current_theta
            current_theta = target_theta

            start_light_pos = light_pos.copy()

            def light_alpha_update(mob, alpha):
                pos = rotate_z(start_light_pos, alpha * delta_theta)
                self.renderer.camera.light_source.move_to(pos)

            # Camera rotation with light update
            self.play(
                self.camera.animate.set_euler_angles(theta=target_theta),
                UpdateFromAlphaFunc(all_slices, light_alpha_update),
                run_time=0.8,
                rate_func=smooth
            )

            light_pos = rotate_z(light_pos, delta_theta)

            # Slice color change
            self.play(
                all_slices[i][0].animate.set_color(COLORS[i % len(COLORS)]),
                run_time=0.5
            )

            # Slice explode animation
            self.play(
                all_slices[i].animate.shift(direction_list[i] * EXPLODE_DISTANCE),
                run_time=1.2
            )
            
            # Add label
            label_text = PART_LABELS[i] if i < len(PART_LABELS) else f"Slice {i+1}"
            label = Text(label_text, font="Arial", font_size=60, weight=NORMAL, color=LABEL_COLOR).scale(0.5)
            
            # Rotate label to face camera
            label.flip(axis=Y_AXIS)
            label.rotate(90 * DEGREES, axis=RIGHT)
            label.rotate(math_midpoint - 90 * DEGREES, axis=OUT)
            label.move_to(
                direction_list[i] * (RADIUS + EXPLODE_DISTANCE + 0.5)
            )

            # Label animation
            self.play(FadeIn(label), run_time=0.5)
            self.wait(0.5)
            self.play(FadeOut(label), run_time=0.5)
            self.wait(0.5)

        #---------------------------
        # FINAL ROTATION + RECOMBINE
        #---------------------------

        # Calculate distance to return to starting position
        final_delta_theta = TAU + SLICE_ANGLE
        start_light_pos = light_pos.copy()

        # Light update function for final rotation
        def final_light_update(mob, alpha):
            pos = rotate_z(start_light_pos, alpha * final_delta_theta)
            self.renderer.camera.light_source.move_to(pos)
        
        # Final rotation and recombination animation
        self.play(
            self.camera.animate.set_euler_angles(theta=current_theta + final_delta_theta),
            UpdateFromAlphaFunc(all_slices, final_light_update),
            *[
                all_slices[i].animate.shift(-direction_list[i] * EXPLODE_DISTANCE)
                for i in range(NUM_SLICES)
            ],
            run_time=5,
            rate_func=smooth
        )

        self.wait(2)