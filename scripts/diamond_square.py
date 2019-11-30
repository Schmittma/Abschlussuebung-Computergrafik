# -*- coding: utf-8 -*-
"""Diamond Square algorithm implementation.

This module generates a heightmap using the Diamond-Square-Algorithm.
Parameters are hardcoded into the module attributes.

Example:
        $ python diamond_square.py

Attributes:
    ds_width (int): Width of the resulting DiamondSquare heightmap.
    ds_height (int): Height of the resulting DiamondSquare heightmap.
    ds_noise (int): Noise used during the DS generation process.
    ds_corner_max (int): Upper border for the corner initializtion values.
    ds_equal_corners (boolean): Corner initialization with same random value if true.
                        Else generate new random value for each corner.
    heightmap_path (str): Path to which the heightmap will be saved.

Todo:
    * -

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
ds_width = 1920
ds_height = 1080
ds_noise = 128
ds_corner_max = 256
ds_equal_corners = False
heightmap_path = "Heightmap{}x{}.png".format(ds_width, ds_height)

import numpy
import random
import matplotlib.pyplot as plt

class DiamondSquare:
    """Contains all functions to generate a heightmap using the DiamondSquare-Algorithm
    Attributes:
        size (int): Side length for Diamond-Square map generation.
        max_index (int): Max index of map array.
        step_size (int): Current step size during map generation.
        half_step (int): Half of step_size.
        map (numpy.array): 2D array realising heightmap
    """

    def __init__(self, width=10, height=20, noise=128, corner_max=256, equal_corners=False, max_exp=14):
        """
        Initializes the Class and calls set_size.
        Note:
            The Values for Noise and noise reduction must be chosen carefully. Wrong values will result
            in an unrealistic/unusable heightmap.
            Altering the arg max_exp can result in wrong beahaviour or prolong the generation indefinetly.
        Args:
            width (int): The width of the generated heightmap.
            height (int): The height of the generated heightmap.
            noise (int): Range for Noise (-noise,noise) that is added during each point calculation.
            corner_max (int): Max random value for the initialization of the corner values.
            equal_corners (boolean): If True sets the same value for each corner during initialization.
        """
        #Values set via Arguments
        self.width = width
        self.height = height
        self.noise = noise
        self.equal_corners = equal_corners
        self.corner_max = corner_max
        self.max_exp = max_exp

        # Normalized vectors for the selection of outer points to generate
        # the value of a point.
        # Square:            Diamond:
        #   UL      UR              U
        #       C               L   C   R
        #   LL      LR              D
        self.square_pattern = [[0,0], [0,1], [1,0], [1,1]]
        self.diamond_pattern = [[1,0], [0,1], [-1,0], [0,-1]]

        # Calculate side length of DS-Map
        self.set_size()

    def set_size(self):
        """Calculates the needed side length for the Diamond-Square-Algorithm.
        This function calculates the needed square dimension in order for
        the algorithm to work (side length = 2 ^ n + 1).

        Note:
            Wrong values for the attributes max_exp and width/height may lead to an indefinite runtime.
        """

        # Square dimensions need to be larger than the longest side of
        # the output rectangular map.
        max_length = max(self.height, self.width)

        # Calculated side length
        opt_side = 0

        # Current n for side length formula 2^n+1
        cur_exp = 0

        # Calculate 2^n+1 with current n and stop once the number
        # is large enough.
        while opt_side < max_length:
            # Calculate side length with exponent
            opt_side = pow(2,cur_exp) + 1
            # Increment exponent for next run
            cur_exp += 1
            # Prevent indefinite runs by limiting to a max exponent.
            if cur_exp > self.max_exp:
                raise Exception("Size of Heightmap too large! Max exponent reached.")

        # Side length for map
        self.size = opt_side

        # Max index of map array
        self.max_index = self.size - 1

        #Step sizes for generation runs
        self.step_size = self.size - 1
        self.half_step = self.step_size // 2

    def init_map(self):
        """Initializes a 2D array which realizes the terrain map for the DS-Algorithm.
        Creates the array and sets the corner values needed by the algorithm.
        """

        # Create 2D numpy array
        self.map = numpy.zeros((self.size, self.size))

        # Class can generate different random Corner values or
        # the same random value for all 4 corners
        fixed_rval = random.randint(0,self.corner_max)
        rval = 0

        # Loop over Corner vectors
        for corner_vector in self.square_pattern:
            # Get corner coordinates by multiplying normalized vectors
            # with the side lengths.
            y = self.max_index * corner_vector[0]
            x = self.max_index * corner_vector[1]

            # Decide whether to set same or different values
            if self.equal_corners:
                rval = fixed_rval
            else:
                rval = random.randint(0, self.corner_max)

            # Write value to map
            self.map[y][x] = rval

    def rand(self):
        """ Generates random float value in noise range.
        Returns:
            The random float value
        """
        return random.uniform(-self.noise,self.noise)

    def generate(self):
        """Main generation process of the Diamond-Square algorithm.
        For an explanation of the algorithm itself visit:
        https://medium.com/@nickobrien/diamond-square-algorithm-explanation-and-c-implementation-5efa891e486f

        Returns:
            2D Array map with dimensions specified by self.width and self.height
        """
        # Create 2D array that realizes the heightmap
        self.init_map()

        # Main loop, do diamond and square steps until every point has been filled
        # The step size is reduced each loop and is used to calculate coordinates of
        # new points. By reducing it, the algorithm makes sure to calculate all points.
        while self.step_size > 1:

            # x and y coordinates represent the upper left corner of each square
            # Range using size - 1 so that the points at the right border are ignored
            for x in range(0, self.max_index, self.step_size):
                for y in range(0, self.max_index, self.step_size):
                    # Execute diamond step from current coords
                    self.diamond_step(x, y)

            # The diamond step centers are distributed inequally, this counter
            # is used to calculate the needed distribution.
            step_counter = 0

            # x and y coordinates represent the center of each diamond
            # For every even step (including 0):
            #   Start at half a step in y direction and end half a step before the edge
            # For every odd number:
            #   Start at y = 0 and step until y = max_index
            for x in range(0,self.max_index + 1, self.half_step):

                # Check if current step is even/odd
                if (step_counter % 2) == 0:
                    # y step range for even steps
                    y_steps = range(self.half_step, self.max_index, self.step_size)
                else:
                    # y step range for odd steps
                    y_steps = range(0, self.size, self.step_size)

                # Step using predefined range
                for y in y_steps:
                    # execute square step from current coords
                    self.square_step(x, y)

                # Incremetn step counter
                step_counter += 1

            # Step size is halved after every loop
            self.step_size = self.step_size // 2
            self.half_step = self.step_size // 2

            # Reduce noise and make sure that it never hits 0 to
            # prevent errors.
            self.noise = max(self.noise // 2, 1)

        # Cut the desired map with dimensions defined by self.width and self.height
        # from the generated map.
        result_map = self.map[:self.height,:self.width]
        return result_map

    def diamond_step(self,x,y):
        """Calculates center value at given coordinates.

        Note:
            Calculation pattern:
                    UL      UR
                        C
                    LL      LR
            Distance from center to outer points is step_size / 2

        Args:
            y (int): x coordinate of center.
            x (int): y coordinate of center.

        """
        # Collects values of outer points by using the vectors from square pattern
        vals = []
        for point_vector in self.square_pattern:
            try:
                # Get vector to square edges
                vector = [y + point_vector[0] * self.step_size, x + point_vector[1] * self.step_size]
                # Collect value
                vals.append(self.map[vector[0]][vector[1]])
            except:
                continue
        # Calculate new center value
        avg = self.get_avg(vals)
        # Write value to map
        self.map[y + self.half_step][x + self.half_step] = avg

    def square_step(self,x, y):
        """Calculates center value at given coordinates.

        Note:
            Calculation pattern:
                        U
                    L   C   R
                        D
            Distance from center to outer points is step_size / 2

        Args:
            y (int): x coordinate of center.
            x (int): y coordinate of center.
        """
        # Collects values of outer points by using the vectors from square pattern
        vals = []
        for point_vector in self.diamond_pattern:
            try:
                # Get vector to diamond edges
                vector = [y + point_vector[0] * self.half_step, x + point_vector[1] * self.half_step]
                # Collect value
                vals.append(self.map[vector[0]][vector[1]])
            except:
                continue

        avg = self.get_avg(vals)
        self.map[y][x] = avg

    def get_avg(self,val_list):
        """Calculates the average for a step center and add a noise.

        Args:
            val_list (list[float]): Collected values if outer points.
        Returns:
            The calculated value.
        """

        # Calculate arithmetic average
        elem_sum = sum(val_list)
        avg = elem_sum / len(val_list)

        # Add noise to average
        avg = avg + self.rand()
        return avg

class DS_image_converter():
    """Contains all functions to convert a 2D heightmap to image
    """
    def __init__(self,cmap='gray',interpolation='nearest',bbox_inches='tight'):
        """
        Initializes the Class
        Note:
            Parameters cmap, interpolation, axis and bbox_inches are strings and inserted directly into
            the matplot functions imshow and savefig.
            Change these parameters only if you know what you are doing.
        Args:
            cmap (str): Name of the matplotlib colormap.
            interpolation (str): Name of the matplotlib interpolation method.
            bbox_inches (str): Parameter for matplotlib savefig method.
        """
        self.cmap = cmap
        self.interpolation = interpolation
        self.bbox_inches = bbox_inches

    def save_img(self, heightmap, path):
        """Generates heatmap and saves it as a file.
        Args:
            heightmap (numpy.array): 2D array with containing height values.
            path (str): path/name of file to save to.

        """
        # Generate heatmap
        dpi = 100
        fig = plt.figure(frameon=False)

        # Generating a pixel excat image is a bit tricky with matplotlib
        # Set size so that 100 pixels per inch
        fig.set_size_inches(ds_width/dpi,ds_height/dpi)

        #set axis off
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)

        # Generate heatmap
        ax.imshow(heightmap, cmap=self.cmap, interpolation=self.interpolation)

        # Save with dpi so that width and height of image are pixel exact
        fig.savefig(heightmap_path, dpi=dpi)

if __name__ == "__main__":
    # Initialize DiamondSquare Class
    ds = DiamondSquare(width=ds_width,height=ds_height, noise=ds_noise,corner_max=ds_corner_max,equal_corners=ds_equal_corners)
    # Initialize converter
    converter = DS_image_converter()
    # Generate and save image
    converter.save_img(ds.generate(),heightmap_path)