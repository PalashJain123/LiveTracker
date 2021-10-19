import os
import pandas as pd
import sys
import glob
import seaborn as sns
import matplotlib
from pathlib import Path
if os.environ.get('DISPLAY','') == '':
  print('no display found. Using non-interactive Agg backend')
  matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import figure

dump_type = sys.argv[1]
underlier = sys.argv[2]
main_path = "/spare/local/pjain/data_dump/Tim/Logs/"
interested_columns = ["Total_PnL", "Theo_Margin_Util", "Actual_Margin_Util", "Delta_PnL", "Vega_PnL"]

print("\n\nInitializing Sim-Real comparison...\n")
print("@params:\n\tUnderlier: ", underlier,
    "\n\tDump_Type: ", dump_type,
    "\n\tInterested_columns: ", interested_columns)

def intersection(lst1, lst2):
  lst3 = [value for value in lst1 if value in lst2]
  return lst3

def getDictStructure(path):
  dict_files = {}
  all_files = []
  for f in glob.glob(path):
    all_files.append(f)
  all_files = sorted(all_files)
  for f in all_files:
    if ((len(underlier) != 0) & (f.find(underlier) != -1)):
      date = f.split("-")[1]
      pid = f.split("_")[3].split("-")[0]
      try:
        df = pd.read_csv(f, index_col = 0)
        if date not in dict_files:
          dict_files[date] = {}
        dict_files[date][pid] = df
      except:
        print(" | Pandas failed | PID: ", pid, " Date: ", date, " File: ", f)
  return dict_files

def plotSimReal(comp_files):
  for today in comp_files.keys():
    Path(main_path + "Images/" + str(today)).mkdir(parents=True, exist_ok=True)
    for pid in comp_files[today].keys():
      sel_cols = {}
      for ins in interested_columns:
        sel_cols[ins] = []
        for col in comp_files[today][pid].columns:
          if(col.find(ins) != -1):
            sel_cols[ins].append(col)
      print(sel_cols)
      plt.figure(num=None, figsize=(12, 8), dpi=200, facecolor='w', edgecolor='k')
      font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 5}
      matplotlib.rc('font', **font)
      plt.title('Date: ' + str(today))
      i=0
      for ins in interested_columns:
        print(pid, i, sel_cols[ins])
        df = comp_files[today][pid].loc[:,sel_cols[ins]]
        plt.subplot(len(interested_columns), 1, i+1)
        print(df.head())
        plt.plot(df, linewidth=0.6)
        plt.ylabel(ins)
        plt.grid()
        i+=1
        plt.legend(["Sim", "Real"])
      #plt.tight_layout()
      plt.savefig(main_path + "Images/" + str(today) + "/Plot_" + str(pid) + ".png")


sim_files = getDictStructure(main_path + "Sim/STATS*")
real_files = getDictStructure(main_path + "Real/STATS*")
print("\n\nReceived sim-real dicts: ", sim_files.keys(), real_files.keys())
comp_files = {}
if dump_type == "CRON":
  #today_date = date.today().strftime("%Y%m%d")
  today_date = "20211014"
  comp_files[today_date] = {}
if dump_type == "HISTORY":
  all_dates = intersection(sim_files.keys(), real_files.keys())
  for d in all_dates:
    comp_files[d] = {}
for today_date in comp_files.keys():
  print(today_date)
  if((today_date in sim_files.keys()) & (today_date in real_files.keys())):
    intersected_pids = intersection(sim_files[today_date].keys(), real_files[today_date].keys())
    print("\nDate: ", today_date)
    print("\tPID list: ", intersected_pids)
    for pid in intersected_pids:
      sim_df = sim_files[today_date][pid]
      real_df = real_files[today_date][pid]
      sim_df.reset_index(inplace=True)
      real_df.reset_index(inplace=True)
      comp_df = pd.merge(sim_df[interested_columns], real_df[interested_columns],
          suffixes = ["_Sim", "_Real"], left_index = True, right_index = True)
      comp_files[today_date][pid] = comp_df
  elif (today_date not in sim_files.keys()):
    print("Not present in Sim Dicts")
  elif (today_date not in real_files.keys()):
    print("Not present in Real Dicts")
plotSimReal(comp_files)
