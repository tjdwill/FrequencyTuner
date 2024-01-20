"""
@title: Frequency Tuner
@author: tjdwill
@date: 19 January 2024
@description:
    Defined herein is a program that generates and executes the FFmpeg
    command that tunes a song to the selected frequency. Full description
    is available in the documentation.
"""

import argparse
from pathlib import Path

import ffmpy

# Invariants
SUPPORTED_FREQ = [432, 639]
SUPPORTED_TYPES = [".mp3", ".opus", ".flac"]
CONVERSION_FACTORS = {
    432: (432./440.),
    639: 639/622.25,
}
codec_key = "codec"
bitrate_key = "bitrate"
AUDIO_INFO = {
    ".mp3": {codec_key: "libmp3lame", bitrate_key: "256k"},
    ".opus": {codec_key: "libopus", bitrate_key: "128k"},
    ".flac": {codec_key: "flac", bitrate_key: "48k"}
}
DEFAULT_FREQ = 432
DEFAULT_EXT = ".mp3"


# Helpers
def is_audio(name: Path) -> bool:
    answer = False
    if isinstance(name, str):
        name = Path(name)
    if name.is_file() and name.suffix in SUPPORTED_TYPES:
        answer = True
    return answer


def tune(song: Path, out_path: Path, hz: int, ext: str, dry_run: bool) -> None:
    """Convert the song in question"""
    # Pathing
    name = song.stem
    filename = out_path / f"{name}_({hz}Hz){ext}"
    ext_info = AUDIO_INFO[ext]
    codec, bitrate = ext_info[codec_key], ext_info[bitrate_key]
    factor = CONVERSION_FACTORS[hz]

    # Create the conversion object
    ff = ffmpy.FFmpeg(
        inputs={song.resolve(): None},
        outputs={filename.resolve(): f'-af "rubberband=pitch={factor}" -y -acodec {codec} -b:a {bitrate}'}
    )
    if dry_run:
        print(ff.cmd)
    else:
        ff.run()


def tune_songs(curr_dir: Path, dir_list: list, hz: int, ext: str, dry_run: bool) -> list:
    """Traverse directory and convert songs as encountered"""
    next_dirs = [path for path in curr_dir.iterdir() if path.is_dir()]
    audio_files = [track for track in curr_dir.iterdir() if is_audio(track)]
    if audio_files:
        converted = curr_dir / f"{hz}Hz"
        if (not converted.is_dir()) and (not dry_run):
            converted.mkdir()
        for track in audio_files:
            tune(track, converted, hz, ext, dry_run)
    dir_list.remove(curr_dir)
    return [*next_dirs, *path_list]


if __name__ == "__main__":
    # Command Line Support
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filetype",
        choices=SUPPORTED_TYPES,
        default=DEFAULT_EXT,
        help=f"(Default: {DEFAULT_EXT}) Determines the output file type.\n"
    )
    parser.add_argument("filepath", help="Path to the audio file(s)")
    parser.add_argument(
        "--hz",
        default=DEFAULT_FREQ,
        type=int,
        choices=SUPPORTED_FREQ,
        help=f"(Default: {DEFAULT_FREQ}) Desired output tuning frequency"
    )
    parser.add_argument(
        "-d", "--dryrun",
        default=False,
        action="store_true",
        help="(Default: False) Performs a dry run of the program, "
             "outputting the generated commands to the screen."
    )
    args = parser.parse_args()
    desired_hz = args.hz
    desired_ext = args.filetype
    audio_path = Path(args.filepath)
    test_run = args.dryrun
    if not audio_path.exists:
        raise ValueError("Provided path does not exist.\n")
    if not (audio_path.is_file() or audio_path.is_dir()):
        raise ValueError("Provided path is neither a file nor a directory.\n")

    # Tuning Action
    if is_audio(audio_path):
        outdir = audio_path.parent / f"{desired_hz}Hz"
        if (not outdir.is_dir()) and (not test_run):
            outdir.mkdir()
        tune(audio_path, outdir, desired_hz, desired_ext, test_run)
    else:
        path_list = [audio_path]
        while path_list:
            path_list = tune_songs(path_list[0], path_list, desired_hz, desired_ext, test_run)
    print("Done!")
