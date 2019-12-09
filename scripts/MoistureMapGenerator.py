import bpy
import mathutils
import os 

# Map the given number input from the range [ir_min; ir_max] to the range
# [or_min; or_max]
def map_number(input, ir_min, ir_max, or_min, or_max):
    return (input - ir_min) * ((or_max - or_min) / (ir_max - ir_min) ) + or_min   

heightmap_path = "//textures\\heightmap.png"   # Path to the heightmap to determine the size of the image
scale = 5           # The scale factor of the vectors (Bigger means zoomed out of the noise)

size = 500,500 # Default image size
heightmap = bpy.data.images.load(heightmap_path) #Load the heightmap to determine the size of the moisture map
size = heightmap.size


image = bpy.data.images.new(("MoistureMap"), width=size[0], height=size[1]) #Create the image for the moisture map that will be saved
pixels = []         # Generate an array of pixels, which will hold the color of each pixel
noisevalues = []    # array that holds the noisevalue for every pixel


 
print("Pixels to edit: " + str(size[0] * size[1]))

# For every pixel in the image generate a noise
for y in range(size[1]):
    for x in range(size[0]):
        
        # Perlin noise operates in a decimal scale with whole numbers beeing maxima (Norm the coordinates to a fraction of the full size of the image)
        # The Perlin coordinate can then be scaled to create a more "zoomed out" pattern
        xPerlin = x / size[1] * scale
        yPerlin = y / size[0] * scale
        
        # Noise function needs 3D Vector, default z-coord to 0
        noise = mathutils.noise.noise(mathutils.Vector((xPerlin,yPerlin,0)), noise_basis="PERLIN_ORIGINAL")
        noisevalues.append(noise)           
        
# It is explicitly stated to contain values between 0 and 1, we need to map
# the generated noisevalues which we don't now the limits for onto the 0 to 1 range.
# We solve this by searching the generated noisevalues for a min and a max value and take these
# as the limits of the noisevalues. 
# We then need to map the [min; max] range onto [0; 1]
min_noise = min(noisevalues)
max_noise = max(noisevalues)

# For every pixel in the image, apply the mapped noisevalue onto the rgb values of the pixel
# and default the alpha to 1.0
for y in range(size[1]):
    for x in range(size[0]):
        
        # Get the current index of the pixel (for any y, we have travelled all x of the row)
        pixel_index = (size[0] * y) + x
        
        color_value = map_number(noisevalues[pixel_index], min_noise, max_noise, 0.0, 1.0)
        #print(str(max_noise) +  " | " + str(min_noise) +  " | " + str(noisevalues[pixel_index]) +  " | " + str(color_value))
        
        # Append the mapped values onto the rgb positions
        for s in range(3):
            pixels.append(color_value)
        pixels.append(1.0)         
        

print("Finished generating pixels")
print("Start saving image...")

# Override the image pixels with the generated pixels and save the file as png
image.pixels = pixels
image.filepath_raw = "//textures/moisturemap.png"
image.file_format = "PNG"
image.save()

print("Image saved successfully")



