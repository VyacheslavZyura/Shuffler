# -*- coding: utf-8 -*-
from os import walk, path
from random import shuffle
from shutil import SameFileError, disk_usage, copy

# Сбор списка песен из источника: возвращает список песен songs
def aggregation(source):
    sorts = []
    lim_file = 30*1024*1024
    for paths, dirs, files in walk(source):
        for file in files:
            sorts.append(path.join(paths, file))
    songs = [song for song in sorts if (song.endswith(".mp3")) \
                        and (path.getsize(song)<= lim_file)]

    return songs 

# Копирование из списка песен: не возрващает ничего
def shuffler(songs, destination, limit):
    shuffle(songs) 
    size = 0
    for song in songs: 
        size += path.getsize(song)
        if size > limit:
            break
        try:
            copy (song, destination)
        except SameFileError: 
            continue

# Проверка на ошибки входных данных: возвращает значения для MessageBox
def check_memory (destination, limit):
    tot, usd, free = disk_usage(destination)
    if limit > free:
        return False
    else:
        return True
        