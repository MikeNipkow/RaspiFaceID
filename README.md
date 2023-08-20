# RaspiFaceID
Toggle Raspberry Pi GPIOs when a camera detects an authorized person.

Using ``face_recognition`` this script can toggle the GPIOs of a Raspberry Pi with ``pigpio``.

# WARNING
Please note that the script will simply look for any faces in the video stream. It does not check if it is a real person or just a printed image of the face!

# Features
You can connect a camera via a __rtsp stream__ or similar, or use a directly connected camera. The script will scan the current frame for faces and compare those to your defined reference images. If any face matches a reference face a GPIO of your pi will be turned on for a defined amount of time.

``RaspiFaceID`` will automatically draw a box around the recognized faces and save the frame if an authorized person was found and the GPIO therefore turned on. If your reference image contain the persons name, e.g. ``Alex.png`` it will also display their names in the console and their name will be put under the drawn box in the frame.

# Configuration
This repository provides a default configuration, which will be copied to the project root folder. You need to edit this ``config.ini`` file to your needs.

Typically you have to configure at least:
- Video URL (Camera Data)
- RaspberryPi IP-Address
- GPIO address of the Pi that you want to toggle

The images will be stored inside the ``/data/images`` folder, which will also be created on the first startup. Note that you will have to rerun the container after you added new reference images or removed some.

# Installation
### Requirements
- Python 3.3+
- macOS or Linux (Windows is also supported, but you will need to install ``cmake`` and ``dlib`` correctly)
- Optional: RaspberryPi with pigpio installed

### Run
To start the script simply use ``python main.py``. Make sure that you have installed all dependencies before via ``pip install <Module>`` or ``pip install --no-cache-dir -r requirements.txt``.

### Docker
You can run this script inside a docker container. Therefore you will have to clone this repository:
 ```git clone https://github.com/MikeNipkow/RaspiFaceID.git```

After that you can build the docker image with the included dockerfile:
 ```sudo docker build -t raspifaceid .```

Run the container with:
 ```sudo docker run -v ${PWD}:/usr/src/app raspifaceid```
