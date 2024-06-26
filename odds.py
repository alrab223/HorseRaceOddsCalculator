import math
import itertools


class Odds:
   def __init__(self):
      # 払戻率
      self.payout_rate_win = 0.80  # 単勝
      self.payout_rate_place = 0.80  # 複勝
      self.payout_rate_quinella = 0.775  # 馬連
      self.payout_rate_bracket_quinella = 0.775  # 枠連
      self.payout_rate_quinella_place = 0.775  # ワイド
      self.payout_rate_exacta = 0.75  # 馬単
      self.payout_rate_trio = 0.75  # 三連複
      self.payout_rate_trifecta = 0.725  # 三連単

   def calculate_win_odds(self, votes):
      total_votes = sum(votes.values())
      odds_list = {}
      for horse, winning_votes in votes.items():
         if winning_votes == 0:
            odds_list[horse] = 0  # 票数が0の場合はオッズを0とする
         else:
            odds = (total_votes * self.payout_rate_win) / winning_votes
            truncated_odds = math.floor(odds * 10) / 10
            odds_list[horse] = truncated_odds
      return odds_list

   def calculate_place_odds(self, votes):
      total_votes = sum(votes.values())
      indexed_list = list(votes.items())
      index_combinations = list(itertools.combinations(indexed_list, 3))
      odds_list = {horse: [] for horse in votes.keys()}
      for horse in votes.keys():
         for i in index_combinations:
            if horse in [i[0][0], i[1][0], i[2][0]]:
               odds_list[horse].append(i)

      place_odds = {}
      answer = {}
      for horse, value in odds_list.items():
         place_odds[horse] = []
         for i in value:
            if votes[horse] == 0:
               place_odds[horse].append(0)  # 票数が0の場合はオッズを0とする
            else:
               odds = (
                  (votes[horse] + (total_votes - i[0][1] - i[1][1] - i[2][1]) / 3)
                  * self.payout_rate_place
                  / votes[horse]
               )
               odds = math.floor(odds * 10) / 10
               place_odds[horse].append(odds)
         if place_odds[horse]:
            answer[horse] = [max(place_odds[horse]), min(place_odds[horse])]
         else:
            answer[horse] = [0, 0]  # 票数が0の場合はオッズを[0, 0]とする

      return answer

   def calculate_quinella_odds(self, votes):
      total_votes = sum(votes.values())
      answer = {}
      for key, value in votes.items():
         if value == 0:
            answer[key] = 0  # 票数が0の場合はオッズを0とする
         else:
            odds = (
               (value + (total_votes - value) / 2) * self.payout_rate_quinella / value
            )
            odds = math.floor(odds * 10) / 10
            answer[key] = odds
      return answer

   def calculate_exacta_odds(self, votes):
      return self.calculate_quinella_odds(votes)  # 同じロジックを使用

   def calculate_trio_odds(self, votes):
      total_votes = sum(votes.values())
      answer = {}
      for key, value in votes.items():
         if value == 0:
            answer[key] = 0  # 票数が0の場合はオッズを0とする
         else:
            odds = (value + (total_votes - value) / 3) * self.payout_rate_trio / value
            odds = math.floor(odds * 10) / 10
            answer[key] = odds
      return answer

   def calculate_trifecta_odds(self, votes):
      total_votes = sum(votes.values())
      answer = {}
      for key, value in votes.items():
         if value == 0:
            answer[key] = 0  # 票数が0の場合はオッズを0とする
         else:
            odds = (
               (value + (total_votes - value) / 3) * self.payout_rate_trifecta / value
            )
            odds = math.floor(odds * 10) / 10
            answer[key] = odds
      return answer

   def calculate_quinella_place_odds(self, votes):
      total_votes = sum(votes.values())
      answer = {}
      for key, value in votes.items():
         if value == 0:
            answer[key] = [0, 0]  # 票数が0の場合はオッズを[0, 0]とする
         else:
            odds_min = (
               (value + (total_votes - value) / 2)
               * self.payout_rate_quinella_place
               / value
            )
            odds_max = (
               (value + (total_votes - value) / 3)
               * self.payout_rate_quinella_place
               / value
            )
            odds_min = math.floor(odds_min * 10) / 10
            odds_max = math.floor(odds_max * 10) / 10
            answer[key] = [odds_min, odds_max]
      return answer
