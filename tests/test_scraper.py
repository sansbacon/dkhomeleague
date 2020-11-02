# test_dkhomeleague.py

import json
import os
import random

import pandas as pd
import pytest

from dkhomeleague import *


@pytest.fixture
def p():
    return 'p'


def test_func(p):
    """Tests func"""
    # get random sampling of leaderboards
    assert p
