
import os
import sys
import time
import shutil
import subprocess
import random

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEOS = {
    "1": "assets_cache.mp4",
    "2": "module_data.mp4",
    "3": "system_core.mp4"
}

FPS = 20
WIDTH = 140
HEIGHT = 40

# 16 brightness levels for more detailed ASCII output
CHARS = " .,:;irsXA253hMH"

CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


# ==========================================
# REQUIREMENT CHECKS
# ==========================================

def check_requirements():

    for program in ("ffmpeg", "ffplay"):
        if shutil.which(program) is None:
            raise RuntimeError(
                f"{program} is not installed or in PATH."
            )

    for filename in VIDEOS.values():

        filepath = os.path.join(BASE_DIR, filename)

        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                f"Required media file missing: {filename}"
            )


# ==========================================
# ASCII FRAME RENDERER
# ==========================================

def render_frame(data):

    output = []

    for y in range(HEIGHT):

        row = []

        for x in range(WIDTH):

            i = (y * WIDTH + x) * 3

            r, g, b = data[i:i+3]

            brightness = (
                0.299 * r +
                0.587 * g +
                0.114 * b
            ) / 255

            index = int(
                brightness * (len(CHARS) - 1)
            )

            char = CHARS[index]

            row.append(
                f"\033[38;2;{r};{g};{b}m{char}"
            )

        output.append(
            "".join(row) + RESET
        )

    return "\n".join(output)


# ==========================================
# READ COMPLETE RGB FRAMES
# ==========================================

def read_frame(stream, frame_size):

    data = bytearray()

    while len(data) < frame_size:

        chunk = stream.read(
            frame_size - len(data)
        )

        if not chunk:
            break

        data.extend(chunk)

    if len(data) != frame_size:
        return None

    return data


# ==========================================
# MAIN MENU
# ==========================================

def show_menu():

    os.system("cls")

    print(f"{CYAN}")
    print("==============================================================")
    print("                    SYSTEM DIAGNOSTICS")
    print("==============================================================")
    print(RESET)

    print(f"{GREEN}[SYS] Multimedia subsystem initialized.")
    print("[SYS] RGB framebuffer operational.")
    print("[SYS] Audio drivers detected.")
    print("[SYS] All media modules verified.")
    print(RESET)

    print()
    print("                 SELECT AN OPERATION")
    print()

    print(f"             {CYAN}[1]{RESET}  Operation Alpha")
    print(f"             {CYAN}[2]{RESET}  Operation Beta")
    print(f"             {CYAN}[3]{RESET}  Operation Gamma")

    print()
    print(f"             {GREEN}[4]{RESET}  Surprise Me")
    print()
    print(f"             {RED}[0]{RESET}  Exit")

    print()
    print("==============================================================")


# ==========================================
# VIDEO PLAYER
# ==========================================

def play_video(filename):

    audio = None
    video = None

    frame_number = 0

    filepath = os.path.join(
        BASE_DIR,
        filename
    )

    try:

        os.system("cls")

        print(f"{CYAN}Initializing selected subsystem...{RESET}")
        print("[SYS] Preparing media decoder...")
        print("[SYS] Establishing audio connection...")
        print("[SYS] Starting RGB output...")

        time.sleep(1)

        # Start original audio

        audio = subprocess.Popen(
            [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel", "quiet",
                "-i", filepath
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Decode video into high-resolution RGB frames

        video = subprocess.Popen(
            [
                "ffmpeg",
                "-loglevel", "error",
                "-i", filepath,
                "-vf",
                f"fps={FPS},scale={WIDTH}:{HEIGHT}:flags=lanczos",
                "-an",
                "-f", "rawvideo",
                "-pix_fmt", "rgb24",
                "pipe:1"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**7
        )

        frame_size = WIDTH * HEIGHT * 3

        start_time = time.perf_counter()

        # Hide terminal cursor

        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        # Main rendering loop

        while True:

            data = read_frame(
                video.stdout,
                frame_size
            )

            if data is None:
                break

            target_time = (
                start_time + frame_number / FPS
            )

            delay = (
                target_time - time.perf_counter()
            )

            if delay > 0:
                time.sleep(delay)

            rendered = render_frame(data)

            sys.stdout.write("\033[H\033[2J")

            sys.stdout.write(
                f"{CYAN}SYSTEM DIAGNOSTICS "
                f"// LIVE OUTPUT{RESET}\n"
            )

            sys.stdout.write(rendered)

            sys.stdout.write(
                f"\n{GREEN}"
                f"FRAME: {frame_number:06d} "
                f"| FPS: {FPS} "
                f"| TIME: {frame_number/FPS:.1f}s"
                f"{RESET}"
            )

            sys.stdout.flush()

            frame_number += 1

        print(
            f"\n\n{CYAN}PROCESS COMPLETED.{RESET}"
        )

    except KeyboardInterrupt:

        print(
            f"\n\n{RED}Process interrupted.{RESET}"
        )

    finally:

        # Stop video decoder

        if video:

            if video.stdout:
                video.stdout.close()

            if video.poll() is None:
                video.terminate()

            video.wait()

        # Stop audio playback

        if audio:

            if audio.poll() is None:
                audio.terminate()

            audio.wait()

        # Restore terminal cursor and colours

        sys.stdout.write(
            f"\033[0m\033[?25h"
        )

        sys.stdout.flush()

    input(
        "\nPress ENTER to return to the main menu..."
    )


# ==========================================
# APPLICATION
# ==========================================

def main():

    os.system("title SYSTEM DIAGNOSTICS")

    check_requirements()

    while True:

        show_menu()

        choice = input(
            "\nEnter selection (0-4): "
        ).strip()

        if choice == "0":

            os.system("cls")

            print(
                f"{CYAN}System diagnostics terminated.{RESET}"
            )

            break

        elif choice in VIDEOS:

            play_video(
                VIDEOS[choice]
            )

        elif choice == "4":

            selected_video = random.choice(
                list(VIDEOS.values())
            )

            print(
                f"\n{GREEN}"
                "[SYS] Random module selected."
                f"{RESET}"
            )

            time.sleep(1)

            play_video(
                selected_video
            )

        else:

            print(
                f"\n{RED}Invalid selection. Try again.{RESET}"
            )

            time.sleep(1)


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        sys.stdout.write(
            "\033[0m\033[?25h"
        )

        print(
            f"\n{RED}SYSTEM ERROR: {error}{RESET}"
        )

        input(
            "\nPress ENTER to exit..."
        )
