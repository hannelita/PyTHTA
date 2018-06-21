import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from resistor import Resistor
from capacitor import Capacitor
from inductor import Inductor

class Resolver:
  def __init__(self):
    self.df = None
    self.sources = []
    self.nodes = []
    self.elements = None
    self.g_matrix = None

  def build(self):
    self.import_file()
    self.get_info()
    self.build_elements()
    self.build_g_matrix()
  
  def import_file(self):
    self.df = pd.read_csv('test.csv', header=None)
    return self.df

  def get_info(self):
    build_info = np.array(self.df[:1]).reshape(10,)
    self.nodes_qty = build_info[1]
    self.sources_qty = build_info[2]
    self.dt = build_info[3]
    self.elements = self.df.drop([0])
    self.elements = self.elements[:-1]

  def build_elements(self):
    self.ndcvs = 0
    self.ndccs = 0
    self.energy_storage_el = 0
    self.gkm = np.zeros(self.elements.shape[0])

    for index, row in self.elements.iterrows():
      if row[0] == 'R':
        resistor = Resistor(row[3])
        self.gkm[index-1] = 1/resistor.value
      elif row[0] == 'C':
        capacitor = Capacitor((row[3]*1e-6))
        self.gkm[index-1] = 2*capacitor.value/self.dt
      elif row[0] == 'L':
        inductor = Inductor((row[3]*1e-3))
        self.gkm[index-1] = self.dt/(2*inductor.value)
      elif row[0] == 'EDC':
        self.ndcvs = self.ndcvs + 1

  def build_g_matrix(self):
    self.g_matrix = np.zeros((self.elements.shape[0], self.elements.shape[0]))
    print(self.g_matrix[0,0])
    for index, row in self.elements.iterrows():
      k = row[1]
      m = row[2]
      if m == 0:
        self.g_matrix[k,k] = self.g_matrix[k,k] + self.gkm[index-1]
      elif k == 0:
        self.g_matrix[m,m] = self.g_matrix[m,m] + self.gkm[index-1]
      else:
        self.g_matrix[k,k] = self.g_matrix[k,k] + self.gkm[index-1]
        self.g_matrix[m,m] = self.g_matrix[m,m] + self.gkm[index-1]
        self.g_matrix[k,m] = self.g_matrix[k,m] + self.gkm[index-1]
        self.g_matrix[m,k] = self.g_matrix[m,k] + self.gkm[index-1]
    print(self.g_matrix)




