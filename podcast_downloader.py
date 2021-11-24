#!/usr/bin/env python
"""
podcast_downloader.py

USAGE:
    python podcast_downloader.py "https://youtube.com/link" "path/to/output/folder"
"""
import click
import json
import os
import re
import subprocess

from datetime import time
from typing import *

YOUTUBE_DL_EXE = 'youtube-dl'
FFMPEG_EXE = 'ffmpeg'

TRACK_RE = re.compile(
    r'^((?P<hr>\d{1,2}):)?(?P<min>\d{1,2}):(?P<sec>\d{2})[\s\-]+(?P<track_title>.+)$')


def get_filename(url, format_id=251):
    cmd = f'{YOUTUBE_DL_EXE} {url} -f {format_id} --get-filename'
    p = subprocess.run(cmd.split(' '), capture_output=True)
    return p.stdout.decode('utf-8').strip()


def download_file(url, format_id=251):
    cmd = f'{YOUTUBE_DL_EXE} {url} -f {format_id}'
    print(f'Running "{cmd}"')
    subprocess.run(cmd, shell=True)


class SubtitleSection:
    def __init__(self, ts, text):
        self.start, self.end = ts.split(' --> ')
        self.text = text

    @property
    def start(self) -> time:
        return self._start

    @start.setter
    def start(self, value: str):
        self._start = time.fromisoformat(value + '000')

    @property
    def end(self) -> time:
        return self._end

    @end.setter
    def end(self, value: str):
        self._end = time.fromisoformat(value.split(' ')[0] + '000')

    def __str__(self):
        return self.text

    def __repr__(self):
        return str(self)


def get_subtitles_by_track(
    url: str,
    tracks: List[Dict[str, Any]],
    lang: str = 'en',
    fmt: str = 'vtt',
) -> Dict[int, List[str]]:
    cmd = (f'{YOUTUBE_DL_EXE} {url}'
           f'   --skip-download'
           f'   --write-sub'
           f'   --sub-lang {lang}'
           f'   --sub-format {fmt}')
    p = subprocess.run(cmd.split(' '), capture_output=True)
    stdout = p.stdout.decode('utf-8').strip()
    s = 'Writing video subtitles to: '
    filename = stdout[stdout.find(s)+len(s):]

    with open(filename) as f:
        subtitle_sections = list(_yield_subtitle_sections(f.read()))

    return _get_subtitles_by_track_number(subtitle_sections, tracks)


def _yield_subtitle_sections(subs: str) -> Iterable[SubtitleSection]:
    lines = subs.splitlines()
    for i, line in enumerate(lines):
        if '-->' not in line:
            continue

        ts = lines[i]
        txt = []
        j = i + 1
        while lines[j].strip():
            txt.append(lines[j])
            j += 1
        yield SubtitleSection(ts, ' '.join(txt))


def _get_subtitles_by_track_number(
    subtitles: List[SubtitleSection],
    tracks: List[Dict[str, Any]],
) -> Dict[int, List[str]]:
    subs_by_track = {}
    track_i = 0
    for sub in subtitles:
        if track_i + 1 < len(tracks) and sub.start > tracks[track_i]['end_time']:
            track_i += 1
        track = tracks[track_i]
        subs_by_track.setdefault(track['track_num'], []).append(sub.text)
    for track_num in subs_by_track:
        subs_by_track[track_num] = [line.strip() for line in ' '.join(
            subs_by_track[track_num]).replace('.', '.\n').splitlines()]
    return subs_by_track


def get_tracks_from_string(string: str) -> List[Dict[str, Any]]:
    lines = [line.strip()
             for line in string.splitlines()
             if line.strip()]
    tracks = {}
    track_num = 0
    for line in lines:
        m = TRACK_RE.match(line)
        if not m:
            continue

        track_info: dict = m.groupdict()
        for key in {'hr', 'min', 'sec'}:
            track_info[key] = int(track_info[key] or 0)
        track_num += 1

        tracks[track_num] = dict(
            track_title=track_info['track_title'].replace('"', "'").replace('/', '-'),
            track_num=track_num,
            start_time=time.fromisoformat(
                '%(hr).02d:%(min).02d:%(sec).02d' % track_info
            ),
        )

    for num, track in tracks.items():
        track['end_time'] = tracks.get(num + 1, {}).get('start_time')

    return list(tracks.values())


def run_ffmpeg(
    input_filename: str,
    artist: str,
    album: str,
    tracks: List[dict],
    output_directory: str,
    output_format: str,
    subtitles: Dict[int, List[str]],
) -> None:
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    for track in tracks:
        output_path, cmd_parts = _get_ffmpeg_cmd(
            input_filename,
            start_time=track['start_time'],
            end_time=track['end_time'],
            artist=artist,
            album=album,
            track_title=track['track_title'],
            track_num=track['track_num'],
            output_directory=output_directory,
            output_format=output_format,
        )

        print(' '.join(cmd_parts))
        subprocess.run(' '.join(cmd_parts), shell=True)

        sub_filename = output_path.rsplit('.', maxsplit=1)[0] + '.subs'
        with open(sub_filename, 'w') as f:
            f.write('\n'.join(subtitles[track['track_num']]))


def _get_ffmpeg_cmd(
    input_filename: str,
    start_time: str,
    end_time: str,
    artist: str,
    album: str,
    track_title: str,
    track_num: int,
    output_directory: str,
    output_format: str,
) -> Tuple[str, List[str]]:
    output_file = os.path.join(
        output_directory,
        (
            f"{' - '.join(str(x) for x in [track_num, track_title, artist, album])}"
            f".{output_format}"
        ).replace('/', '-').replace(':', '-')
    )

    cmd_parts = [
        FFMPEG_EXE,
        # input file
        '-i "%s"' % input_filename,
        # output options
        '-c copy',  # keep input format
        '-ss %s' % start_time,  # track start time (hh:mm:ss[.xx])
        f'-metadata track="{track_num}"',
        f'-metadata artist="{artist}"',
        f'-metadata album="{album}"',
        f'-metadata title="{track_title}"',
        # f'-metadata year="{year}"',
    ]
    if end_time:
        cmd_parts.append(f'-to %s' % end_time)  # track end time (hh:mm:ss[.xx])
    cmd_parts.append(f'"{output_file}"')

    return output_file, cmd_parts


def get_video_info(url: str) -> Tuple[str, Dict]:
    cmd = f'{YOUTUBE_DL_EXE} {url} --write-info-json --skip-download'
    p = subprocess.run(cmd.split(' '), capture_output=True)
    stdout = p.stdout.decode('utf-8').strip()
    s = 'Writing video description metadata as JSON to: '
    filename = stdout[stdout.find(s)+len(s):]
    with open(filename) as f:
        return filename, json.load(f)


# def get_yt_video_details(url):
#     r = requests.get(url)
#     html = r.content.decode('utf-8')
#     s = _extract_json_from_string(html, '"videoDetails":', '{', '}')
#     return json.loads(s)
#
#
# def _extract_json_from_string(s, search_start, open_char, close_char):
#     start_i = s.find(search_start)+len(search_start)
#     stack = 0
#     for i, char in enumerate(s[start_i:]):
#         if char == open_char:
#             stack += 1
#         elif char == close_char:
#             stack -= 1
#             if stack == 0:
#                 return s[start_i:start_i + i + 1]


@click.command()
@click.argument('url')
@click.argument('directory')
def main(url, directory):
    print('downloading video info')
    video_info_filename, video_info = get_video_info(url)

    audio_formats = sorted(
        [x for x in video_info['formats']
         if x['format_note'] == 'tiny'
         and x['acodec'] == 'opus'],
        key=lambda d: d['tbr']
    )
    fmt = audio_formats[-1]  # highest quality
    # fmt = audio_formats[0]  # smallest files

    print(f'selected audio format {fmt["format"]}')

    filename = get_filename(url, format_id=fmt['format_id'])
    if not os.path.exists(filename):
        download_file(url, format_id=fmt['format_id'])

    tracks = get_tracks_from_string(video_info['description'])

    run_ffmpeg(filename,
               artist=video_info['channel'],
               album=(video_info['title']
                      .split('|')[0]
                      .replace('/', '-')
                      .replace(':', '-')),
               tracks=tracks,
               output_directory=directory,
               output_format=fmt['acodec'],
               subtitles=get_subtitles_by_track(url, tracks))

    # os.remove(video_info_filename)
    # os.remove(filename)


if __name__ == '__main__':
    main()
