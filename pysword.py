#!/usr/bin/env python

# * ztext format documentation
# I'll use Python's struct module's format strings.
# See http://docs.python.org/lib/module-struct.html
# Take the Old Testament (OT) for example. Three files:
#
#  - ot.bzv: Maps verses to character ranges in compressed buffers.
#    10 bytes ('<IIH') for each verse in the Bible:
#    - buffer_num (I): which compressed buffer the verse is located in
#    - verse_start (I): the location in the uncompressed buffer where the verse begins
#    - verse_len (H): length of the verse, in uncompressed characters
#    These 10-byte records are densely packed, indexed by VerseKey 'Indicies' (docs later).
#    So the record for the verse with index x starts at byte 10*x.
#
#  - ot.bzs: Tells where the compressed buffers start and end.
#    12 bytes ('<III') for each compressed buffer:
#    - offset (I): where the compressed buffer starts in the file
#    - size (I): the length of the compressed data, in bytes
#    - uc_size (I): the length of the uncompressed data, in bytes (unused)
#    These 12-byte records are densely packed, indexed by buffer_num (see previous).
#    So the record for compressed buffer buffer_num starts at byte 12*buffer_num.
#
#  - ot.bzz: Contains the compressed text. Read 'size' bytes starting at 'offset'.
#
#  NT is analogous.
#
# Example usage:
#  python pysword.py esv ot 1

import os
modules_path = os.environ["HOME"]+"/.sword/modules/texts/ztext"


import struct, zlib
from os.path import join as path_join

class ZModule(object):
    def __init__(self, module):
        self.module = module
        self.files = {
            'ot': self.get_files('ot'),
            'nt': self.get_files('nt')
            }
   
    def get_files(self, testament):
        '''Given a testament ('ot' or 'nt'), returns a tuple of files
        (verse_to_buf, buf_to_loc, text)
        '''
        base = path_join(modules_path, self.module)
        v2b_name, b2l_name, text_name = [path_join(base, '%s.bz%s' % (testament, code))
                                         for code in ('v', 's', 'z')]
        return [open(name, 'rb') for name in (v2b_name, b2l_name, text_name)]

    def text(self, testament, index):
        '''Get the text for a given index.'''
        verse_to_buf, buf_to_loc, text = self.files[testament]

        # Read the verse record.
        verse_to_buf.seek(10*index)
        buf_num, verse_start, verse_len = struct.unpack('<IIH', verse_to_buf.read(10))
       
        uncompressed_text = self.uncompressed_text(testament, buf_num)
        return uncompressed_text[verse_start:verse_start+verse_len]

    def uncompressed_text(self, testament, buf_num):
        verse_to_buf, buf_to_loc, text = self.files[testament]

        # Determine where the compressed data starts and ends.
        buf_to_loc.seek(buf_num*12)
        offset, size, uc_size = struct.unpack('<III', buf_to_loc.read(12))

        # Get the compressed data.
        text.seek(offset)
        compressed_data = text.read(size)
        return zlib.decompress(compressed_data)


def find_book(book):
    book = book.lower()
    for testament, contents in books.iteritems():
        for num, (name, osis, pref_abbr, num_chapters) in enumerate(contents):
            if book in [name.lower(), osis.lower(), pref_abbr.lower()]:
                return testament, num, num_chapters
    return None

def ref_to_index(book, chapter, verse):
    '''
    Computes the index corresponding to a reference.

    book: a full name of a book
    chapter, verse: 1-based numbers.
    '''
    testament, book_num, num_chapters = find_book(book)
    
# Data about book names and abbreviations, from canon.h
# Name, OSIS name, preferred abbreviation, number of chapters
books = {
    'ot': [
        ["Genesis", "Gen", "Gen", 50],
        ["Exodus", "Exod", "Exod", 40],
        ["Leviticus", "Lev", "Lev", 27],
        ["Numbers", "Num", "Num", 36],
        ["Deuteronomy", "Deut", "Deut", 34],
        ["Joshua", "Josh", "Josh", 24],
        ["Judges", "Judg", "Judg", 21],
        ["Ruth", "Ruth", "Ruth", 4],
        ["I Samuel", "1Sam", "1Sam", 31],
        ["II Samuel", "2Sam", "2Sam", 24],
        ["I Kings", "1Kgs", "1Kgs", 22],
        ["II Kings", "2Kgs", "2Kgs", 25],
        ["I Chronicles", "1Chr", "1Chr", 29],
        ["II Chronicles", "2Chr", "2Chr", 36],
        ["Ezra", "Ezra", "Ezra", 10],
        ["Nehemiah", "Neh", "Neh", 13],
        ["Esther", "Esth", "Esth", 10],
        ["Job", "Job", "Job", 42],
        ["Psalms", "Ps", "Ps", 150],
        ["Proverbs", "Prov", "Prov", 31],
        ["Ecclesiastes", "Eccl", "Eccl", 12],
        ["Song of Solomon", "Song", "Song", 8],
        ["Isaiah", "Isa", "Isa", 66],
        ["Jeremiah", "Jer", "Jer", 52],
        ["Lamentations", "Lam", "Lam", 5],
        ["Ezekiel", "Ezek", "Ezek", 48],
        ["Daniel", "Dan", "Dan", 12],
        ["Hosea", "Hos", "Hos", 14],
        ["Joel", "Joel", "Joel", 3],
        ["Amos", "Amos", "Amos", 9],
        ["Obadiah", "Obad", "Obad", 1],
        ["Jonah", "Jonah", "Jonah", 4],
        ["Micah", "Mic", "Mic", 7],
        ["Nahum", "Nah", "Nah", 3],
        ["Habakkuk", "Hab", "Hab", 3],
        ["Zephaniah", "Zeph", "Zeph", 3],
        ["Haggai", "Hag", "Hag", 2],
        ["Zechariah", "Zech", "Zech", 14],
        ["Malachi", "Mal", "Mal", 4]],
    
    'nt': [
        ["Matthew", "Matt", "Matt", 28],
        ["Mark", "Mark", "Mark", 16],
        ["Luke", "Luke", "Luke", 24],
        ["John", "John", "John", 21],
        ["Acts", "Acts", "Acts", 28],
        ["Romans", "Rom", "Rom", 16],
        ["I Corinthians", "1Cor", "1Cor", 16],
        ["II Corinthians", "2Cor", "2Cor", 13],
        ["Galatians", "Gal", "Gal", 6],
        ["Ephesians", "Eph", "Eph", 6],
        ["Philippians", "Phil", "Phil", 4],
        ["Colossians", "Col", "Col", 4],
        ["I Thessalonians", "1Thess", "1Thess", 5],
        ["II Thessalonians", "2Thess", "2Thess", 3],
        ["I Timothy", "1Tim", "1Tim", 6],
        ["II Timothy", "2Tim", "2Tim", 4],
        ["Titus", "Titus", "Titus", 3],
        ["Philemon", "Phlm", "Phlm", 1],
        ["Hebrews", "Heb", "Heb", 13],
        ["James", "Jas", "Jas", 5],
        ["I Peter", "1Pet", "1Pet", 5],
        ["II Peter", "2Pet", "2Pet", 3],
        ["I John", "1John", "1John", 5],
        ["II John", "2John", "2John", 1],
        ["III John", "3John", "3John", 1],
        ["Jude", "Jude", "Jude", 1],
        ["Revelation of John", "Rev", "Rev", 22]]}

# Verses per chapter
verses_per_chapter = [
  # Genesis
  31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38,
    18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36,
    30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26,
  # Exodus
  22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25,
    26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29,
    31, 43, 38,
  # Leviticus
  17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37,
    27, 24, 33, 44, 23, 55, 46, 34,
  # Numbers
  54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22,
    29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13,
  # Deuteronomy
  46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21,
    20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12,
  # Joshua
  18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51,
    9, 45, 34, 16, 33,
  # Judges
  36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30,
    48, 25,
  # Ruth
  22, 23, 18, 22,
  # I Samual
  28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24,
    42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13,
  # II Samuel
  27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43,
    26, 22, 51, 39, 25,
  # I Kings
  53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21,
    43, 29, 53,
  # II Kings
  18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37,
    21, 26, 20, 37, 20, 30,
  # I Chronicles
  54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19,
    8, 30, 19, 32, 31, 31, 32, 34, 21, 30,
  # II Chronicles
  17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11,
    37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23,
  # Ezra
  11, 70, 13, 24, 17, 22, 28, 36, 15, 44,
  # Nehemiah
  11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31,
  # Esther
  22, 23, 15, 17, 14, 14, 10, 17, 32, 3,
  # Job
  22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29,
    29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41,
    30, 24, 34, 17,
  # Psalms
  6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13,
    31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17,
    13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12,
    8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13,
    19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9,
    5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176,
    7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7,
    12, 15, 21, 10, 20, 14, 9, 6,
  # Proverbs
  33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29,
    30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31,
  # Ecclesiastes
  18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14,
  # Song of Solomon
  17, 17, 11, 16, 16, 13, 13, 14,
  # Isaiah
  31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6,
    17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8,
    31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21,
    14, 21, 22, 11, 12, 19, 12, 25, 24,
  # Jeremiah
  19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15,
    18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21,
    28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34,
  # Lamentations
  22, 22, 66, 22, 22,
  # Ezekiel
  28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14,
    49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28,
    23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35,
  # Daniel
  21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13,
  # Hosea
  11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9,
  # Joel
  20, 32, 21,
  # Amos
  15, 16, 15, 13, 27, 14, 17, 14, 15,
  # Obadiah
  21,
  # Jonah
  17, 10, 10, 11,
  # Micah
  16, 13, 12, 13, 15, 16, 20,
  # Nahum
  15, 13, 19,
  # Habakkuk
  17, 20, 19,
  # Zephaniah
  18, 15, 20,
  # Haggai
  15, 23,
  # Zechariah
  21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21,
  # Malachi
  14, 17, 18, 6,
  # -----------------------------------------------------------------
  # Matthew
  25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30,
    34, 46, 46, 39, 51, 46, 75, 66, 20,
  # Mark
  45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20,
  # Luke
  80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48,
    47, 38, 71, 56, 53,
  # John
  51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42,
    31, 25,
  # Acts
  26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41,
    38, 40, 30, 35, 27, 27, 32, 44, 31,
  # Romans
  32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27,
  # I Corinthians
  31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24,
  # II Corinthians
  24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14,
  # Galatians
  24, 21, 29, 31, 26, 18,
  # Ephesians
  23, 22, 21, 32, 33, 24,
  # Philippians
  30, 30, 21, 23,
  # Colossians
  29, 23, 25, 18,
  # I Thessalonians
  10, 20, 13, 18, 28,
  # II Thessalonians
  12, 17, 18,
  # I Timothy
  20, 15, 16, 16, 25, 21,
  # II Timothy
  18, 26, 17, 22,
  # Titus
  16, 15, 15,
  # Philemon
  25,
  # Hebrews
  14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25,
  # James
  27, 26, 18, 17, 20,
  # I Peter
  25, 25, 22, 19, 14,
  # II Peter
  21, 22, 18,
  # I John
  10, 29, 24, 21, 21,
  # II John
  13,
  # III John
  14,
  # Jude
  25,
  # Revelation of John
  20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21,
    15, 27, 21]


class Book(object):
    def __init__(self, name, osis_name, preferred_abbreviation, chapter_lengths):
        self.name = name
        self.osis_name = osis_name
        self.preferred_abbreviation = preferred_abbreviation
        self.chapter_lengths = chapter_lengths
        self.num_chapters = len(chapter_lengths)


testaments = {
'ot': [
Book('Genesis', 'Gen', 'Gen', [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26]),
Book('Exodus', 'Exod', 'Exod', [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38]),
Book('Leviticus', 'Lev', 'Lev', [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34]),
Book('Numbers', 'Num', 'Num', [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13]),
Book('Deuteronomy', 'Deut', 'Deut', [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12]),
Book('Joshua', 'Josh', 'Josh', [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33]),
Book('Judges', 'Judg', 'Judg', [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25]),
Book('Ruth', 'Ruth', 'Ruth', [22, 23, 18, 22]),
Book('I Samuel', '1Sam', '1Sam', [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13]),
Book('II Samuel', '2Sam', '2Sam', [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25]),
Book('I Kings', '1Kgs', '1Kgs', [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53]),
Book('II Kings', '2Kgs', '2Kgs', [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30]),
Book('I Chronicles', '1Chr', '1Chr', [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30]),
Book('II Chronicles', '2Chr', '2Chr', [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23]),
Book('Ezra', 'Ezra', 'Ezra', [11, 70, 13, 24, 17, 22, 28, 36, 15, 44]),
Book('Nehemiah', 'Neh', 'Neh', [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31]),
Book('Esther', 'Esth', 'Esth', [22, 23, 15, 17, 14, 14, 10, 17, 32, 3]),
Book('Job', 'Job', 'Job', [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17]),
Book('Psalms', 'Ps', 'Ps', [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6]),
Book('Proverbs', 'Prov', 'Prov', [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31]),
Book('Ecclesiastes', 'Eccl', 'Eccl', [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14]),
Book('Song of Solomon', 'Song', 'Song', [17, 17, 11, 16, 16, 13, 13, 14]),
Book('Isaiah', 'Isa', 'Isa', [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24]),
Book('Jeremiah', 'Jer', 'Jer', [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34]),
Book('Lamentations', 'Lam', 'Lam', [22, 22, 66, 22, 22]),
Book('Ezekiel', 'Ezek', 'Ezek', [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35]),
Book('Daniel', 'Dan', 'Dan', [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13]),
Book('Hosea', 'Hos', 'Hos', [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9]),
Book('Joel', 'Joel', 'Joel', [20, 32, 21]),
Book('Amos', 'Amos', 'Amos', [15, 16, 15, 13, 27, 14, 17, 14, 15]),
Book('Obadiah', 'Obad', 'Obad', [21]),
Book('Jonah', 'Jonah', 'Jonah', [17, 10, 10, 11]),
Book('Micah', 'Mic', 'Mic', [16, 13, 12, 13, 15, 16, 20]),
Book('Nahum', 'Nah', 'Nah', [15, 13, 19]),
Book('Habakkuk', 'Hab', 'Hab', [17, 20, 19]),
Book('Zephaniah', 'Zeph', 'Zeph', [18, 15, 20]),
Book('Haggai', 'Hag', 'Hag', [15, 23]),
Book('Zechariah', 'Zech', 'Zech', [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21]),
Book('Malachi', 'Mal', 'Mal', [14, 17, 18, 6]),
],
'nt': [
Book('Matthew', 'Matt', 'Matt', [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20]),
Book('Mark', 'Mark', 'Mark', [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20]),
Book('Luke', 'Luke', 'Luke', [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53]),
Book('John', 'John', 'John', [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25]),
Book('Acts', 'Acts', 'Acts', [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31]),
Book('Romans', 'Rom', 'Rom', [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27]),
Book('I Corinthians', '1Cor', '1Cor', [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24]),
Book('II Corinthians', '2Cor', '2Cor', [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14]),
Book('Galatians', 'Gal', 'Gal', [24, 21, 29, 31, 26, 18]),
Book('Ephesians', 'Eph', 'Eph', [23, 22, 21, 32, 33, 24]),
Book('Philippians', 'Phil', 'Phil', [30, 30, 21, 23]),
Book('Colossians', 'Col', 'Col', [29, 23, 25, 18]),
Book('I Thessalonians', '1Thess', '1Thess', [10, 20, 13, 18, 28]),
Book('II Thessalonians', '2Thess', '2Thess', [12, 17, 18]),
Book('I Timothy', '1Tim', '1Tim', [20, 15, 16, 16, 25, 21]),
Book('II Timothy', '2Tim', '2Tim', [18, 26, 17, 22]),
Book('Titus', 'Titus', 'Titus', [16, 15, 15]),
Book('Philemon', 'Phlm', 'Phlm', [25]),
Book('Hebrews', 'Heb', 'Heb', [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25]),
Book('James', 'Jas', 'Jas', [27, 26, 18, 17, 20]),
Book('I Peter', '1Pet', '1Pet', [25, 25, 22, 19, 14]),
Book('II Peter', '2Pet', '2Pet', [21, 22, 18]),
Book('I John', '1John', '1John', [10, 29, 24, 21, 21]),
Book('II John', '2John', '2John', [13]),
Book('III John', '3John', '3John', [14]),
Book('Jude', 'Jude', 'Jude', [25]),
Book('Revelation of John', 'Rev', 'Rev', [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]),
],
}

        
idx = 0
print 'testaments = {'
for testament, contents in books.iteritems():
    print '%r: [' % testament
    for num, (name, osis, pref_abbr, num_chapters) in enumerate(contents):
        new_idx = idx + num_chapters
        print 'Book(%r, %r, %r, %r),' % (
            name, osis, pref_abbr,
            verses_per_chapter[idx:new_idx])
        idx = new_idx
    print '],'
print '}'        


if __name__=='__main__':
    import sys
    mod_name = sys.argv[1]
    testament = sys.argv[2]
    index = int(sys.argv[3])
   
    module = ZModule(mod_name)
    print module.text(testament, index)
    
