import logging
import random

import pytest

from dkhomeleague import Parser


@pytest.fixture
def p():
    return Parser()


def test_parser():
    """Tests __init__"""
    p = Parser()
    assert p.league_key is not None
    assert p.username is not None
    

def test_contest_leaderboard(p, test_directory, tprint):
    """Tests contest_leaderboard"""
    fn = test_directory / 'contest_leaderboard.json'
    data = p._to_obj(fn)
    lb = p.contest_leaderboard(data)
    assert isinstance(lb, list)
    l = random.choice(lb)
    assert isinstance(l, dict)
    fields = {'userName', 'userKey', 'draftGroupId', 'contestKey', 'entryKey', 'rank', 'fantasyPoints'}
    assert fields <= set(l.keys())


def test_contest_lineup(p, test_directory, tprint):
    """Tests contest_lineup"""
    fn = test_directory / 'contest_entry.json'
    data = p._to_obj(fn)
    entry = p.contest_entry(data)
    assert isinstance(entry, dict)
    lineup = entry.get('players')
    assert isinstance(lineup, list)
    player = random.choice(lineup)
    assert isinstance(player, dict)
    fields = {'displayName', 'rosterPosition', 'percentDrafted', 'draftableId', 'score', 
              'statsDescription', 'timeRemaining'}
    assert fields <= set(player.keys())

def test_historical_contests(p, test_directory, tprint):
    """Tests historical_contests"""
    fn = test_directory / 'historical_contests.json'
    data = p._to_obj(fn)
    contests = p.historical_contests(data)
    assert isinstance(contests, list)
    contest = random.choice(contests)
    assert isinstance(contest, dict)
    fields = {'contestStartTime', 'gameSetKey', 'contestKey', 'name', 'draftGroupId', 
              'entries', 'maximumEntries', 'maximumEntriesPerUser', 'entryFee', 'contestState'}
    assert fields <= set(contest.keys())
        

def test_historical_contests_user(p, test_directory, tprint):
    fn = test_directory / 'historical_contests_user.json'
    data = p._to_obj(fn)
    contests = p.historical_contests_user(data)
    assert isinstance(contests, list)
    contest = random.choice(contests)
    assert isinstance(contest, dict)
    fields = {'draftGroupId', 'contestKey', 'entryKey', 'userName', 'userKey', 'rank', 'fantasyPoints',
              'fantasyPointsOpponent', 'userNameOpponent'}
    assert fields <= set(contest.keys())
    

def test_league_members(p, test_directory, tprint):
    fn = test_directory / 'league_metadata.json'
    data = p._to_obj(fn)
    members = p.league_members(data)
    assert isinstance(members, list)
    member = random.choice(members)
    assert isinstance(member, str)


def test_league_metadata(p, test_directory, tprint):
    fn = test_directory / 'league_metadata.json'
    data = p._to_obj(fn)
    md = p.league_metadata(data)
    assert isinstance(md, dict)
    fields = {'league_name', 'league_key', 'members'}
    assert fields <= set(md.keys())


@pytest.mark.skip(reason="unimplemented method - no way to test yet")
def test_live_contests(p, test_directory, tprint):
    fn = test_directory / 'live_contests.json'
    data = p._to_obj(fn)
    contests = p.live_contests(data)
    assert isinstance(contests, list)
    contest = random.choice(contests)
    assert isinstance(contest, dict)
    fields = {'contestStartTime', 'gameSetKey', 'contestKey', 'name', 'draftGroupId', 
              'entries', 'maximumEntries', 'maximumEntriesPerUser', 'entryFee', 'contestState'}
    assert fields <= set(contest.keys())


def test_upcoming_contests(p, test_directory, tprint):
    fn = test_directory / 'upcoming_contests.json'
    data = p._to_obj(fn)
    contests = p.upcoming_contests(data)
    assert isinstance(contests, list)
    contest = random.choice(contests)
    assert isinstance(contest, dict)
    fields = {'name', 'contestKey', 'draftGroupId', 
              'entries', 'contestStartTime', 'contestState'}
    assert fields <= set(contest.keys())


