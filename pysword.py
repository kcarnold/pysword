#!/usr/bin/env python

# A native Python implementation of the SWORD Project Bible Reader
# Currently only ztext Bible modules are implemented.

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
#  python pysword.py esv 1pet 2 9

import os
modules_path = os.environ["HOME"]+"/.sword/modules/texts/ztext"
from books import ref_to_index

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

    def text_for_index(self, testament, index):
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

    def text_for_ref(self, book, chapter, verse):
        '''Get the text for a given reference'''
        chapter, verse = int(chapter), int(verse)
        testament, idx = ref_to_index(book, chapter, verse)
        return self.text_for_index(testament, idx)


if __name__=='__main__':
    import sys
    mod_name, book, chapter, verse = sys.argv[1:]
   
    module = ZModule(mod_name)
    print module.text_for_ref(book, chapter, verse)
    
    
