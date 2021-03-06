# SpaceX launch tracking

Idea: use OCR to convert the telemetry info in the SpaceX launch videos into
data for a plottable visual gravity turn/launch profile.

### **NOTE:** This is just a WIP idea and nothing in here is promised to work for you :)

Immediately obvious TODOs:
 * Cache extracted values.
 * Detect and track stage 2.
 * Output to console if redirecting to a file.

## Source video

You could use `youtube-dl` to get https://www.youtube.com/watch?v=QJXxVtp3KqI,
downloading to an mp4.

I don't know if that's legal where you are so I'll leave that bit up to you.

This code is set up for a video that can be shrunk to 1280x720.

## Generating data

### Install

Firstly, Tesseract: https://github.com/tesseract-ocr/tesseract

Then with Python 3.9.

    pipenv install

### Run

    pipenv run python generate.py [seconds where telem appears] [seconds where separation happens] [video path]

Example:

    pipenv run python generate.py 1192 1368 "GPS III Space Vehicle 05 Mission-QJXxVtp3KqI.mp4"

### The data

The data is CSV data of elapsed time (in seconds), estimated distance
downrange (in metres) and altitude (in metres).

The distance downrange is calculated over these steps:
 * When the altitude changes, we know how long it was since the last time, how far vertically we have travelled, and can also know the velocity at this point in time, and the previous time the altitude changes. This gives a change in velocity over a time.
 * The change in velocity can give us an average velocity (this bit is wobbly and I need to work on it).
 * The change in altitude tells us a distance straight up. The average velocity over time gives us a distance actually travelled. Knowing the two distances we can use Pythagoras to work out the downrange distance.
 * Accumulating these downrange distances and plotting against altitude gives us a flight profile.

## OCR

Some images grabbed by the code during an extract.

![](img/text_height.jpg) ![](img/text_speed.jpg)

![](img/last_frame.jpg)

## Example profiles

### 1 FPS sample rate, just stage 1

Ran with [code tagged at 1.0](https://github.com/thisismyrobot/spacex-video-telemetry-extraction/releases/tag/1.0).

This was stunningly successful, the final landing distance for Stage 1 was [647km down range according to the Everyday Astronaut](https://everydayastronaut.com/gps-iii-sv05-falcon-9-block-5-2/) and my code's simple estimation approach put it at 622.747km.

![](img/1FPS_Stage_1.png)
