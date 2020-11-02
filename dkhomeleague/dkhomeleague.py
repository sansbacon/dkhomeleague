# dkhomeleague.py
import json
import logging
import os
from string import ascii_uppercase

import pandas as pd
from requests_html import HTMLSession
import browser_cookie3

import pdsheet


class Scraper:
    """scrapes league results"""

    def __init__(self, league_key=None, username=None):
        """Creates instance

        Args:
            league_key (str): id for home league
            username (str): your username

        Returns:
            Scraper
        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.league_key = league_key if league_key else os.getenv('DK_LEAGUE_KEY')
        self.username = username if username else os.getenv('DK_USERNAME')
        self.s = HTMLSession()
        self.s.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'DNT': '1',
            'Accept': '*/*',
            'Origin': 'https://www.draftkings.com',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.draftkings.com/',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        })
        self.cj = browser_cookie3.firefox()

    @property
    def api_url(self):
        return 'https://api.draftkings.com/'

    @property
    def base_params(self):
        return {'format': 'json'}

    def _embed_params(self, embed_type):
        return dict(**self.base_params, **{'embed': embed_type})

    def contest_leaderboard(self, contest_id):
        """Gets contest leaderboard"""
        url = self.api_url + f'scores/v1/megacontests/{contest_id}/leaderboard'
        params = self._embed_params('leaderboard')
        return self.get_json(url, params=params)

    def contest_lineup(self, draftgroup_id, entry_key):
        """Gets contest lineup
        
        Args:
            draftgroup_id (int): the draftgroupId
            entry_key (int): the id for the user's entry into the contest
                             can find entryKey in the leaderboard resource

        Returns:
            dict
        """
        url = self.api_url + f'scores/v2/entries/{draftgroup_id}/{entry_key}'
        params = self._embed_params('roster')
        return self.get_json(url, params=params)

    def get_json(self, url, params, headers=None, response_object=False):
        """Gets json resource"""
        headers = headers if headers else {}
        r = self.s.get(url, params=params, headers=headers, cookies=self.cj)
        if response_object:
            return r
        try:
            return r.json()
        except:
            return r.content()

    def historical_contests(self, limit=50, offset=0):
        """Gets historical contests"""
        url = self.api_url + f'contests/v1/contestsets/league/{self.league_key}/historical'
        extra_params = {'limit': limit, 'offset': offset}
        params = dict(**self.base_params, **extra_params)
        return self.get_json(url, params=params)

    def historical_contests_user(self):
        """Gets user historical results"""
        url = self.api_url + f'scores/v1/entries/user/{self.username}/historical'
        extra_params = {'contestSetKey': self.league_key, 'contestSetType': 'league'}
        params = dict(**self.base_params, **extra_params)
        return self.get_json(url, params=params)

    def live_contests(self):
        pass
        #url = self.api_url + f'contests/v1/contestsets/league/{self.league_key}'
        #params = self.base_params
        #return self.get_json(url, params=params)

    def league_metadata(self):
        """Gets league metadata"""
        url = self.api_url + f'leagues/v2/leagues/{self.league_key}'
        params = self.base_params
        return self.get_json(url, params=params)

    def upcoming_contests(self):
        """Gets upcoming contests"""
        url = self.api_url + f'contests/v1/contestsets/league/{self.league_key}'
        params = self.base_params
        return self.get_json(url, params=params)

        
class Parser:
    """Parses league results"""

    def __init__(self, league_key=None, username=None):
        """Creates instance

        Args:
            league_key (str): id for home league
            username (str): your username
            
        Returns:
            Parser
        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.league_key = league_key if league_key else os.getenv('DK_LEAGUE_KEY')
        self.username = username if username else os.getenv('DK_USERNAME')

    def _to_dataframe(self, container):
        """Converts container to dataframe"""
        return pd.DataFrame(container)

    def _to_obj(self, pth):
        """Reads json text in pth and creates python object"""
        if isinstance(pth, str):
            pth = Path(pth)
        return json.loads(pth.read_text())

    def contest_entry(self, data):
        """Parses contest entry

        Args:
            data (dict): parsed JSON

        Returns:
            list: of dict
        """
        wanted = ['draftGroupId', 'contestKey', 'entryKey', 'lineupId', 'userName',
                  'userKey', 'timeRemaining', 'rank', 'fantasyPoints']
        player_wanted = ['displayName', 'rosterPosition', 'percentDrafted', 'draftableId', 'score', 
                         'statsDescription', 'timeRemaining']
        entry = data['entries'][0]
        d = {k: entry[k] for k in wanted}
        d['players'] = []
        for player in entry['roster']['scorecards']:
            d['players'].append({k: player[k] for k in player_wanted})
        return d

    def contest_leaderboard(self, data):
        """Parses contest leaderboard

        Args:
            data (dict): parsed JSON

        Returns:
            list: of dict
        """
        wanted = ['userName', 'userKey', 'draftGroupId', 'contestKey', 'entryKey', 'rank', 'fantasyPoints']
        return [{k: item.get(k) for k in wanted} for item in data['leaderBoard']]
        
    def historical_contests(self, data):
        """Parses historical league contests

        Args:
            data (dict): parsed JSON

        Returns:
            list: of contest dict
        """
        vals = []
        wanted = ['contestStartTime', 'gameSetKey', 'contestKey', 'name', 'draftGroupId', 
                  'entries', 'maximumEntries', 'maximumEntriesPerUser', 'entryFee', 'contestState']
        for contest in data['contests']:
            d = {k: contest[k] for k in wanted}
            attrs = contest['attributes']
            if attrs.get('Root Recurring Contest ID'):
                d['recurringContestId'] = attrs.get('Root Recurring Contest ID')
            vals.append(d)
        return vals

    def historical_contests_user(self, data):
        """Parses historical contests for user in league

        Args:
            data (dict): parsed JSON

        Returns:
            list: of dict
        """
        wanted = ['draftGroupId', 'contestKey', 'entryKey', 'userName', 'userKey', 'rank', 'fantasyPoints',
                  'fantasyPointsOpponent', 'userNameOpponent']
        return [{k: item[k] for k in wanted} for item in data['entries']]

    def league_members(self, data):
        """Gets league members
           Example URL: https://api.draftkings.com/leagues/v2/leagues/67ymkfy8

        Args:
            data (dict): parsed JSON

        Returns:
            list: of str
        """
        return [item['username'] for item in data['league']['members']]      

    def league_metadata(self, data):
        """Gets league metadata
           Example URL: https://api.draftkings.com/leagues/v2/leagues/67ymkfy8

        Args:
            data (dict): parsed JSON

        Returns:
            dict: with user details
        """
        d = {}
        league = data['league']
        d['league_name'] = league['name']
        d['league_key'] = league['key']
        d['league_commissioner'] = league['creatorUsername']
        d['members'] = {item['username']: item['userKey'] for item in league['members']}       
        return d

    def live_contests(self, data):
        # TODO: this may same as upcoming_contests, then filter on contestState
        pass

    def upcoming_contests(self, data):
        contests = data['contests']
        wanted = ['name', 'contestKey', 'draftGroupId', 'entries', 'contestStartTime', 'contestState']
        return [{k: contest[k] for k in wanted} for contest in contests]


class Tracker:
    """Track league results with Google Sheets
    
    Sheet is set up with week as Column A, League Users as Column B -
    Each row is a weekly result starting with the week number

    """
    def __init__(self, sskey=None, json_secret_fn=None, sheet_id=0):
        """Creates instance

        Args:
            sskey (str): key for worksheet
            json_secret_fn (str): fn with authentication secrets
            sheet_id (int): id for individual sheet

        Returns:
            Tracker
        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._colmap = None
        self.app = pdsheet.get_app(json_secret_fn)
        self.sskey = sskey if sskey else os.getenv('DK_LEAGUE_SPREADSHEET')
        self.sheet_id = sheet_id

    @property
    def column_map(self):
        """Gets map of league members -> column number (A=1, etc.)"""
        if not self._colmap:
            ws = pdsheet.get_worksheet(self.sskey)
            s = ws.get_sheet_by_id(self.sheet_id)
            rng = s.get_data_range()
            headers = rng.get_values()[0]
            self._colmap = {user:idx for idx, user in enumerate(headers)}
        return self._colmap   

    def add_week_results(self, week, results):
        """Adds week results to sheet

        Args:
            week (int): the week
            results (dict): key is username, value is score
        """
        # get the sheet
        ws = pdsheet.get_worksheet(app, self.sskey)
        s = ws.get_sheet_by_id(self.sheet_id)

        # figure out the last row
        rng = s.get_data_range()
        newrow_index = rng.coordinates.number_of_row + 1

        # now loop through the results and add to sheet
        colmap = self.column_map
        for k,v in results.items():
            colnum = colmap.get(k)
            if colnum:
                cell = s.get_range(newrow_index, colnum, 1, 1)
                cell.set_value(v)

    def get_week_results(self, week):
        """Gets week results from sheet

        Args:
            week (int): the week of results
        """
        ws = pdsheet.get_worksheet(app, self.sskey)
        s = ws.get_sheet_by_id(self.sheet_id)
        rng = s.get_data_range()
        rows = rng.get_values()
        headers = rows.pop(0)
        for row in rows:
            if row[0] == week:
                return dict(zip(headers, row))
        return None

            
    def summary(self):
        """Creates summary table of results"""
        pass


if __name__ == '__main__':
    pass
