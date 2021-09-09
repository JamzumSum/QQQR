import os
import sys
from math import floor

import cv2 as cv
import pytest
from tencentlogin.up.captcha.jigsaw import Jigsaw, Piece

desktoponly = pytest.mark.skipif(
    sys.platform != 'win32', reason='cv.show not available'
)


@desktoponly
class TestJigsaw:
    @classmethod
    def setUp(cls) -> None:
        cls.j = Jigsaw.load('data/7.yml')

    def testLoad(self):
        cv.imshow('origin', self.j.ans)
        cv.imshow('puzzle', self.j.puzzle)
        cv.imshow('piece', self.j.piece.img)
        cv.waitKey()

    def testSpt(self):
        self.j.piece.strip()
        top = self.j.top + self.j.piece.padding[1]
        lans = cv.line(self.j.ans, (0, top), (self.j.width - 1, top), (0, 0, 255))
        lj = cv.line(self.j.puzzle, (0, top), (self.j.width - 1, top), (0, 0, 255))
        cv.imshow('background', lans)
        cv.imshow('foreground', lj)
        cv.waitKey()

    def testSolve(self):
        for i in os.listdir('data'):
            j = Jigsaw.load("data/" + i)
            left = j.solve()
            assert left > 0

    def testRate(self):
        assert self.j.rate > 0


@desktoponly
class TestPiece:
    @classmethod
    def setup_class(cls) -> None:
        cls.p = Jigsaw.load('data/6.yml').piece

    def testStrip(self):
        r = self.p.strip()
        cv.imshow('strip', r)
        cv.waitKey()
