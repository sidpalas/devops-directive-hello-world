import cv2
import glob
import subprocess
from argparse import Namespace
from apiclient.errors import HttpError
from gtts import gTTS 
from PIL import Image, ImageDraw, ImageFont

from upload_video import get_authenticated_service, initialize_upload

def animate_single_line(base_background_image, input_string, line_y_position, start_frame):
  fnt = ImageFont.truetype('Monaco', 25)
  input_string = '$ ' + input_string
  for i in range(len(input_string)):
    
    d = ImageDraw.Draw(base_background_image)
    d.text((50,line_y_position), input_string[:i], font=fnt, fill=(255,255,255))
      
    base_background_image.save(f'./content_files/black_480p_{(i + start_frame):05}.png')
  return i + start_frame

def get_frame_list():
  img_list = []
  for filename in sorted(glob.glob('./content_files/*.png')):
    img = cv2.imread(filename)
    img_list.append(img)
  return img_list

def create_video_from_frames(frame_list, frame_size, filename):
  out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'DIVX'), 15, frame_size)
  for i in range(len(frame_list)):
    frame_idx = i
    out.write(frame_list[frame_idx])

  out.release()

def create_audio(input_strings, filename):
  audio_text = ''.join(input_strings)
  myobj = gTTS(text=audio_text) 
  myobj.save(filename) 
  
def mux_audio_and_video(video_filename, audio_filename, output_filename):  
  cmd = f'ffmpeg -y -i {audio_filename}  -r 30 -i {video_filename} -filter:a aresample=async=1 -c:a flac -c:v copy {output_filename}'
  subprocess.call(cmd, shell=True)                           
  print('Muxing Done')

if __name__ == "__main__":
  FRAME_SIZE = (720,480)
  LINE_HEIGHT = 35
  INPUT_STRINGS = [
    'Hello YouTube! ', 
    'This video was created by a script... .',
    '.', # This extra period adds a slight pause in the audio
    'Welcome to DevOps Directive!'
    '                                                     '
    ]
  VIDEO_FILENAME = 'content_files/hello_world.avi'
  AUDIO_FILENAME = 'content_files/hello_world.mp3'
  OUTPUT_FILENAME = 'hello_world_video_and_audio.mkv'

  frame = 0
  background_img = Image.new('RGB', FRAME_SIZE, color = 'black')

  for string_idx, input_string in enumerate(INPUT_STRINGS):
    line_y_position = FRAME_SIZE[1]/2 - LINE_HEIGHT * (0.5 + len(INPUT_STRINGS) / 2) + LINE_HEIGHT * string_idx
    frame = 1 + animate_single_line(background_img, input_string, line_y_position, frame)

  frame_list = get_frame_list()
  create_video_from_frames(frame_list, FRAME_SIZE, VIDEO_FILENAME)

  create_audio(INPUT_STRINGS, AUDIO_FILENAME)
  mux_audio_and_video(VIDEO_FILENAME, AUDIO_FILENAME, OUTPUT_FILENAME)

  video_description = '''
This video was created (and uploaded) using:

- Python
- OpenCV
- gTTS
- ffmpeg 
- The YouTube API 

More content coming soon! 

Code used to generate and upload the video @ https://github.com/sidpalas/devops-directive-hello-world

http://devopsdirective.com
'''
  
  # Creating the namespace directly (rather than using argparse)
  # enabled me to make the video description to span multiple lines
  args = Namespace(
    file='hello_world_video_and_audio.mkv',
    title='Hello Youtube! (AUDIO & VIDEO generated and uploaded with python)',
    description=video_description,
    category='28',
    keywords='',
    privacyStatus='public',
    logging_level='DEBUG',
    noauth_local_webserver='true'
  )

  youtube = get_authenticated_service(args)
  try:
    initialize_upload(youtube, args)
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))