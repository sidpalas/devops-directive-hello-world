import cv2
import glob
import subprocess
from argparse import Namespace
from apiclient.errors import HttpError
from gtts import gTTS 
from PIL import Image, ImageDraw, ImageFont

from upload_video import get_authenticated_service, initialize_upload

def animate_single_line(base_background_image, input_string, line_y_position, start_frame):
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

def create_video_from_frames(frame_list, frame_size):
  out = cv2.VideoWriter('content_files/hello_world.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, frame_size)
  for i in range(len(frame_list)):
    frame_idx = i
    out.write(frame_list[frame_idx])

  out.release()

def create_audio(inputs_strings):
  audio_text = ''.join(input_strings)
  myobj = gTTS(text=audio_text) 
  myobj.save("content_files/hello_world.mp3") 
  
def mux_audio_and_video():  
  cmd = 'ffmpeg -y -i content_files/hello_world.mp3  -r 30 -i content_files/hello_world.avi -filter:a aresample=async=1 -c:a flac -c:v copy hello_world_video_and_audio.mkv'
  subprocess.call(cmd, shell=True)                           
  print('Muxing Done')

if __name__ == "__main__":
  frame = 0
  frame_size = (720,480)
  line_height = 35
  input_strings = [
    'Hello YouTube!  ', 
    'This video was created by a computer....',
    '',
    'Welcome to DevOps Directive!'
    '                            '
    ]
  fnt = ImageFont.truetype('Monaco', 25)
  background_img = Image.new('RGB', frame_size, color = 'black')

  for string_idx, input_string in enumerate(input_strings):
    line_y_position = frame_size[1]/2 - line_height * (0.5 + len(input_strings) / 2) + line_height * string_idx
    frame = 1 + animate_single_line(background_img, input_string, line_y_position, frame)

  frame_list = get_frame_list()
  create_video_from_frames(frame_list, frame_size)

  create_audio(input_strings)
  mux_audio_and_video()

  args = Namespace(
    file='hello_world_video_and_audio.mkv',
    title='Hello Youtube! (AUDIO & VIDEO generated and uploaded with python)',
    description='''
This video was created (and uploaded) using:
- Python
- OpenCV
- gTTS
- ffmpeg 
- YouTube API. 

More content coming soon! 

Code used to generate and upload the video @ https://github.com/sidpalas/devops-directive-hello-world

http://devopsdirective.com
''',
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