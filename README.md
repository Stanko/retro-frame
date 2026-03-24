# Retro Frame

DIY pixel art frame, inspired by [Game Frame](https://ledseq.com/product/game-frame/).

![Retro Frame photo showing Mario chasing a gumba](./docs/mario.jpg)
![Retro Frame photo showing Hollow Knight](./docs/hk.jpg)
<video src="https://github.com/Stanko/retro-frame/assets/776788/32b4b00a-9a80-41c9-9a88-cf3a86338d27"></video>
<video src="https://github.com/Stanko/retro-frame/assets/776788/2ef91225-8ba0-4dff-8bf8-045a9eec68e6"></video>

## Intro

The brain is [Adafruit MatrixPortal M4](https://www.adafruit.com/product/4745), an ESP32-based controller. You'll need to follow Adafruit's documentation to install CircuitPython. Then you can copy the code (don't forget to create src/settings.py).

Files you'll need to copy to your MatrixPortal are:

Rename `src/settings_example.py` to `src/settings.py`. If you want the frame to connect to the internet in order to fetch the correct time, add your network name, password, and set `skip_connection=False`.

Then copy the following files and folders:

- `code.py` and `src/*.py` (see `copy.bat|sh`)
- `firmware/[current_version]/lib` to `lib`
- `assets` (which includes splash screen and digital clock sprite)
- `gif` (pick and choose animations you like)

## Apps

There are four apps:

- Gif player (runs each animation for 5 minutes then switches to the next one)
- Digital clock (needs internet connection to get time)
- Analogue clock (needs internet connection to get time)
- Blank - used to preserve power during the night

By default, the display will switch to the digital clock at 23:30, to blank at midnight, and to gif player at 8:30 in the morning. Check [src/settings_example.py](./src/settings_example.py), copy it to src/settings.py, and update it to your preferences.


### Controls

Tilting the display **left** and **right** will cycle between the apps (button up will do the same).

Tilting the display **back** and **forward** will (button down will do the same):

- Gif app - switch between gifs
- Digital clock - switch between 12 and 24 hours clock modes

|Digital Clock|Analogue Clock|
|-|-|
|![Retro Frame with digital clock app showing](./docs/retro-frame-clock-1.jpg)|![Retro Frame with analogue clock app showing](./docs/retro-frame-clock-2.jpg)|

## List of parts

This is a list of all of the main parts with the links to the ones we used.

- Adafruit MatrixPortal M4 https://www.adafruit.com/product/4745
- 64x64 RGB LED Matrix - 2.5mm Pitch - 1/32 Scan - https://www.adafruit.com/product/3649 or https://www.aliexpress.com/item/32816409052.html
- LED diffuser - https://www.adafruit.com/product/4594
- USB C charger - I had one lying around
- The display fits into the IKEA SANNAHED picture frame. But check [frame-v2.png](./random-backup-files/frame/frame-v2.png) for a custom frame blueprints.
- USB C cable - https://www.aliexpress.com/item/1005002105030431.html
- You can control the display by tilting it, but if you want to add buttons, I used these in the first version - https://www.aliexpress.com/item/4000043687021.html
- [3D printed hooks](./random-backup-files/frame/hook.png) for the rubber band that presses the display against the diffuser. Code for generating the model is [here](./random-backup-files/frame/hook.js).

![Retro Frame internals](./docs/retro-frame-internals.jpg)

## Similar projects

There is a few similar projects you might want to check out:

- https://github.com/hanneslinder/esp-pixel-matrix
- https://www.youtube.com/watch?v=A5A6ET64Oz8


## Art credits

If I included your art and you want it removed, I'm sorry, just open an issue and I'll take care of it. The only reason I included your work in the first place is because it is awesome and it makes me happy.

### Other people:

- [Bear](https://rephildesign.tumblr.com/post/120859307063/filbertgames-this-is-what-happens-when-you)
- [Bunny](https://x.com/ko_dll/status/1792974719563485218)
- [Dog](https://dribbble.com/shots/2367354-Doggy-Rabbit)
- [Dota emojis (diretide, giff, es)](https://dota2.fandom.com/wiki/Emoticons)
- Earth and Moon - generated using wonderful [PixelPlanets](https://github.com/Deep-Fold/PixelPlanets)
- [Ember Spirit](https://33.media.tumblr.com/3f53a2565f16799b155d33072ef5fca0/tumblr_nalmwaJGah1sgajexo2_250.gif)
- [Firepit](https://old.reddit.com/r/PixelArt/comments/7d0y1p/oc_fireplace_animation/)
- [Fox](https://elthen.itch.io/2d-pixel-art-fox-sprites)
- [Hollow Knight](https://www.deviantart.com/haykira/art/Hallownest-Fellas-841502305)
- [Jim](https://hani-amir.com/blog/2017/2/7/pixel-art-animation-basics-5-classic-side-scrolling-walking-running-animations-from-the-snes-era)
- [Link](https://www.deviantart.com/world-of-noel/art/Linked-Seasons-Link-361192040)
- [Madeline](https://rephil.dribbble.com/)
- [Mario chase](https://rephil.dribbble.com/)
- [Mario jumping](https://pug-of-war.tumblr.com/post/116535010016/its-a-me-ah-mario)
- [Mega Man](https://www.deviantart.com/bionicandrew1/art/MegaMan-MvC-Moves-736040903)
- [Nyan cat](https://www.nyan.cat/credits.php)
- [Ori](https://twitter.com/WoostarsPixels/status/1543954734108872705?cxt=HHwWgsC8vdCpne0qAAAA)
- [Rafael](https://adamklingpixel.weebly.com/)
- [Robin](http://www.playiconoclasts.com/)
- [Ronin](https://old.reddit.com/user/reinbo_game)
- [Spinning skull](https://www.artstation.com/artwork/ykRDB3)
- [The One Ring](https://dribbble.com/shots/3273233-The-One-Ring)
- [Tears of the Kingdom](https://www.pixeljess.com/portfolio)
- [WC2 Footman](https://old.reddit.com/r/warcraft3/comments/f3b6fw/warcraft_2_footman_remaster/)
- [Penguin](https://old.reddit.com/r/PixelArt/comments/1pt8vqg/some_people_were_convinced_my_last_post_used_3d_i/)


### Myself

- Splash screen
- Clock digits
- [Pulsar](https://muffinman.io/pulsar) animations
- Totoro - heavily inspired by [this one](https://www.deviantart.com/andrewjohnnnn/art/Totoro-Rain-GIF-613239881)
- Tutur, in loving a memory of Artur <3
