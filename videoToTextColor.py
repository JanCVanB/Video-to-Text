import numpy as np
import cv2
import pickle
import sys
import time

aspect_ratio = 1 / 1
input_fps = 30
output_fps = 5

#Dimensions of the output in terminal characters
width = 60
height = int(width / (2 * aspect_ratio))

#Our characters, and their approximate brightness values
charSet = " riledWWdelir "

# Generates a character sequence to set the foreground and background colors
def setColor (bg, fg):
  return "\u001b[48;5;%s;38;5;%sm" % (bg, fg)

black = setColor(16, 16)

# Load in color lookup table data
lerped =  pickle.load( open( "colors.pkl", "rb" ) )
LUT = np.load("LUT.npy")

# Convert an RGB image to a stream of text with ANSI color codes
def convertImg(img, input_frame_index):
  frame = ""
  
  for row in img:
    for color in row:
      color = np.round(color).astype(int)

      b, g, r = color[0], color[1], color[2]

      # Lookup the color index in the RGB lookup table
      idx = LUT[b, g, r]

      # Get the ANSI color codes and lerp character
      bg, fg, lerp, rgb = lerped[idx]

      char = charSet[lerp]
  
      frame += "%s%c" % (setColor(bg, fg), char)
    # Reset colors and end line
    frame += "\033[0m\n"

  # Move the cursor back to the top of the frame to prevent rolling
  frame += "\u001b[%iD\u001b[%iA" % (width, height + 1)

  return frame

def pencils_down():
  print("\u001b[%iC\u001b[%iB" % (width, height))

def main():
  if len(sys.argv) == 2:
    print()
    cap = cv2.VideoCapture(sys.argv[1])

    skippiness = input_fps // output_fps
    input_frame_index = 0
    while(cap.isOpened()):
      frame_start_time = time.time()
      ret, frame = cap.read()

      input_frame_index += 1
      if input_frame_index % skippiness != 0:
        continue

      if frame is None:
        break

      img = cv2.resize(frame, (width, height))
      print(convertImg(img, input_frame_index))

      frame_end_time = time.time()
      time.sleep((1/output_fps)-(frame_end_time-frame_start_time))
    pencils_down()
  else:
    print("Expected video file as argument.")

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    pencils_down()
    sys.exit()

