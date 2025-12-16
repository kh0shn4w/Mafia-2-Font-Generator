# Mafia II Font Generator

A Python 3 script designed to simplify the process of creating custom font mods for *Mafia II*. It takes a TrueType font (`.ttf`) and a set of characters, then generates the necessary texture atlas (`fonttexture.png`) and the XML definition file (`fonttexture.xml`) that the game engine requires.

## Features

-   **Automated Texture Generation:** Creates a perfectly laid-out font atlas from any `.ttf` file.
-   **XML Definition Creation:** Automatically generates the complex XML file with character coordinates, advance, and bearing data for every required font size in the game.
-   **Right-to-Left Language Support:** Includes logic to handle character shaping for languages like Arabic and Kurdish, mapping isolated, initial, medial, and final forms correctly.
-   **Efficient Atlas Packing:** Avoids rendering duplicate glyphs to maximize the use of texture space, ensuring a single visual character shape is only stored once.

## Requirements

-   Python 3.6+
-   Pillow library
-   arabic-reshaper library

## Installation & Usage

#### 1. Install Prerequisites
Open your terminal or command prompt and install the required Python libraries using pip:

```bash
pip install Pillow arabic_reshaper
```

#### 2. Setup Your Project
-   Create a new folder for your font project.
-   Place the `mafia2font.py` script inside this folder.
-   Place your desired TrueType font in the same folder and **rename it to `font.ttf`**.

#### 3. Configure Characters (Optional)
-   Open `mafia2font.py` in a text editor.
-   Find the `INPUT_CHARS` variable at the top of the script.
-   Add or remove any characters you need your font to support.

#### 4. Run the Script
Navigate to your project folder in the terminal or command prompt and execute the script:

```bash
python3 mafia2font.py
```
*(Use `python` instead of `python3` if your system is configured that way)*

The script will process the font and generate two files in the same folder:
-   `fonttexture.png`
-   `fonttexture.xml`

#### 5. Convert Texture to DDS
The game engine requires the font texture to be in `.dds` format. This final step must be done manually.

1.  Open `fonttexture.png` in an image editor that supports DDS export (e.g., **Paint.NET**, **GIMP** with a DDS plugin, or **Photoshop** with the NVIDIA Texture Tools Exporter).
2.  Verify that the image background is transparent (it should appear as a checkerboard pattern).
3.  Save or export the image as a `.dds` file. Use the following settings:
    *   **Compression / Format:** **DXT5**
    *   **Mipmaps:** **Generate Mipmaps**
    *   **Alpha Channel:** Ensure it is saved (e.g., "Interpolated Alpha" in Paint.NET).

#### 6. Use in Game
You now have the final `fonttexture.dds` and `fonttexture.xml` files. You can now use a modding tool (like the SDS Tool GUI) to pack these files into an `.sds` archive and install it in your game.
