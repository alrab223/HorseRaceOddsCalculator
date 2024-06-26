import streamlit as st
from streamlit_modal import Modal
import pandas as pd
import json
import os

from odds import Odds


class Project:
   def __init__(self, name, num_horses):
      self.name = name
      self.num_horses = num_horses
      self.votes = {}

   def to_dict(self):
      return {"name": self.name, "num_horses": self.num_horses, "votes": self.votes}

   @classmethod
   def from_dict(cls, data):
      project = cls(data["name"], data["num_horses"])
      project.votes = data["votes"]
      return project


class StreamlitOddsApp:
   def __init__(self):
      self.odds = Odds()
      self.projects = {}
      self.current_project = None
      self.load_projects()

   def save_projects(self):
      data = {name: project.to_dict() for name, project in self.projects.items()}
      with open("projects.json", "w") as f:
         json.dump(data, f)

   def load_projects(self):
      if os.path.exists("projects.json"):
         with open("projects.json", "r") as f:
            data = json.load(f)
         self.projects = {
            name: Project.from_dict(project_data) for name, project_data in data.items()
         }

   def run(self):
      st.title("競馬オッズ計算システム")

      self.manage_projects()

      if self.current_project:
         menu = [
            "ホーム",
            "単勝・複勝",
            "馬連",
            "枠連",
            "馬単",
            "ワイド",
            "三連複",
            "三連単",
            "オッズ表示",
         ]
         choice = st.sidebar.selectbox("メニュー", menu, key="main_menu")

         if choice == "ホーム":
            st.write(f"現在のプロジェクト: {self.current_project.name}")
            st.write(f"出走頭数: {self.current_project.num_horses}")
         elif choice == "オッズ表示":
            self.display_odds()
         else:
            self.input_votes(choice)

   def manage_projects(self):
      st.sidebar.header("プロジェクト管理")

      # 新規プロジェクト作成ボタン
      if st.sidebar.button("新規プロジェクト作成"):
         self.create_new_project()

      project_names = list(self.projects.keys())
      if project_names:
         selected_project = st.sidebar.selectbox(
            "プロジェクト選択", project_names, key="project_select"
         )
         self.current_project = self.projects[selected_project]

         # プロジェクトの情報を表示
         st.sidebar.write(f"選択中のプロジェクト: {self.current_project.name}")
         st.sidebar.write(f"出走頭数: {self.current_project.num_horses}")

         # 削除ボタンをサイドバーの下部に配置
         st.sidebar.markdown("---")  # 区切り線を追加
         if st.sidebar.button("選択中のプロジェクトを削除"):
            confirm_delete = st.sidebar.button("本当に削除しますか？")
            if confirm_delete:
               del self.projects[selected_project]
               self.save_projects()
               st.sidebar.success(f"プロジェクト '{selected_project}' を削除しました")
               self.current_project = None
               st.experimental_rerun()
      else:
         st.sidebar.warning(
            "プロジェクトが存在しません。新しいプロジェクトを作成してください。"
         )
         self.current_project = None

   def create_new_project(self):
      modal = Modal("新規プロジェクト作成", key="new_project_modal")
      with modal.container():
         new_project_name = st.text_input("プロジェクト名")
         new_project_horses = st.number_input(
            "出走頭数", min_value=1, max_value=40, value=18
         )

         if st.button("作成"):
            if new_project_name and new_project_name not in self.projects:
               self.projects[new_project_name] = Project(
                  new_project_name, new_project_horses
               )
               self.save_projects()
               st.success(f"プロジェクト '{new_project_name}' を作成しました")
               modal.close()
            else:
               st.error("無効なプロジェクト名です")

   def input_votes(self, bet_type):
      if not self.current_project:
         st.error("プロジェクトが選択されていません")
         return

      st.subheader(f"{bet_type} 票数入力")

      num_horses = self.current_project.num_horses

      if bet_type == "単勝・複勝":
         keys = [f"{i}番" for i in range(1, num_horses + 1)]
      elif bet_type == "馬連":
         keys = [
            f"{i}-{j}"
            for i in range(1, num_horses + 1)
            for j in range(i + 1, num_horses + 1)
         ]
      elif bet_type == "枠連":
         keys = [f"{i}-{j}" for i in range(1, 9) for j in range(i, 9)]
      elif bet_type == "馬単":
         keys = [
            f"{i}-{j}"
            for i in range(1, num_horses + 1)
            for j in range(1, num_horses + 1)
            if i != j
         ]
      elif bet_type == "ワイド":
         keys = [
            f"{i}-{j}"
            for i in range(1, num_horses + 1)
            for j in range(i + 1, num_horses + 1)
         ]
      elif bet_type == "三連複":
         keys = [
            f"{i}-{j}-{k}"
            for i in range(1, num_horses + 1)
            for j in range(i + 1, num_horses + 1)
            for k in range(j + 1, num_horses + 1)
         ]
      elif bet_type == "三連単":
         keys = [
            f"{i}-{j}-{k}"
            for i in range(1, num_horses + 1)
            for j in range(1, num_horses + 1)
            for k in range(1, num_horses + 1)
            if i != j and j != k and i != k
         ]

      votes = self.current_project.votes.get(bet_type, {})
      cols = st.columns(3)
      for idx, key in enumerate(keys):
         votes[key] = cols[idx % 3].number_input(
            f"{key}",
            min_value=0,
            value=votes.get(key, 0),
            key=f"{self.current_project.name}-{bet_type}-{key}",
         )

      if st.button("保存", key=f"{self.current_project.name}-{bet_type}-save"):
         self.current_project.votes[bet_type] = votes
         self.save_projects()
         st.success(f"{bet_type}の票数を保存しました")

   def display_odds(self):
      if not self.current_project:
         st.error("プロジェクトが選択されていません")
         return

      st.subheader("オッズ表示")

      if not self.current_project.votes:
         st.error("票数が入力されていません")
         return

      num_horses = self.current_project.num_horses

      if "単勝・複勝" in self.current_project.votes:
         win_odds = self.odds.calculate_win_odds(
            self.current_project.votes["単勝・複勝"]
         )
         place_odds = self.odds.calculate_place_odds(
            self.current_project.votes["単勝・複勝"]
         )

         st.write("単勝オッズ:")
         df_win = pd.DataFrame({"馬番": win_odds.keys(), "オッズ": win_odds.values()})
         st.dataframe(df_win)

         st.write("複勝オッズ:")
         df_place = pd.DataFrame(
            {
               "馬番": place_odds.keys(),
               "最小オッズ": [odds[1] for odds in place_odds.values()],
               "最大オッズ": [odds[0] for odds in place_odds.values()],
            }
         )
         st.dataframe(df_place)

      for title, calc_func in [
         ("馬連", self.odds.calculate_quinella_odds),
         ("枠連", self.odds.calculate_quinella_odds),
         ("馬単", self.odds.calculate_exacta_odds),
         ("ワイド", self.odds.calculate_quinella_place_odds),
         ("三連複", self.odds.calculate_trio_odds),
         ("三連単", self.odds.calculate_trifecta_odds),
      ]:
         if title in self.current_project.votes:
            odds = calc_func(self.current_project.votes[title])
            st.write(f"{title}オッズ:")
            df = pd.DataFrame({"組み合わせ": odds.keys(), "オッズ": odds.values()})
            st.dataframe(df)


if __name__ == "__main__":
   app = StreamlitOddsApp()
   app.run()
